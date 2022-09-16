import pytest
import requests
import json
from src import config

from src.error import InputError
from src.error import AccessError

@pytest.fixture
def reg_login():
    #register three users
    reg_result =   [0,0,0,0]
    login_result = [0,0,0,0]

    reg_result[0] = request_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    reg_result[1] = request_register_v2('yetanother.validemail123@gmail.com', '123abc!@#++', 'Dylan', 'Meringue')
    reg_result[2] = request_register_v2('notthisagain.validemail456@gmail.com', '123abc!@#--', 'Manuel', 'Internetiquette')
    reg_result[3] = request_register_v2('thisisavalidemail@gmail.com', '!@#$%^&*()', 'Jim', 'J Thompson')
    
    login_result[0] = request_login_v2('validemail@gmail.com', '123abc!@#')
    login_result[1] = request_login_v2('yetanother.validemail123@gmail.com', '123abc!@#++')
    login_result[2] = request_login_v2('notthisagain.validemail456@gmail.com', '123abc!@#--')
    login_result[3] = request_login_v2('thisisavalidemail@gmail.com', '!@#$%^&*()')

    return {
        "reg_result": reg_result,
        "login_result": login_result,
    }


@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

def test_login(clear, reg_login):
    # tests to determine if login works correctly

    rr = reg_login['reg_result']
    lr = reg_login['login_result']

    for i in range (0, len(rr)):
        assert lr[i]['auth_user_id'] == rr[i]['auth_user_id']


def test_unregistered_email():
    requests.delete(config.url + 'clear/v1')
    assert(request_login_v2('validemail@gmail.com', '123abc!@#')['code'] == 400)


def test_wrong_login(clear, reg_login):
    # invalid login attempts using wrong password
    assert(request_login_v2('validemail@gmail.com', '__123abc!@#')['code'] == 400)
    assert(request_login_v2('yetanother.validemail123@gmail.com', '__123abc!@#++')['code'] == 400)
    assert(request_login_v2('notthisagain.validemail456@gmail.com', '__123abc!@#--')['code'] == 400)

    # test unregistered email
    assert(request_login_v2('unregistered@bmail.com', '__123abc!@#--')['code'] == 400)


def test_wrong_register(clear):
    # tests to determine if register errors work
    
    # email not valid
    assert(request_register_v2('_invalidemail@gmail.comics', '123abc!@#', 'Hayden', 'Everest')['code'] == 400)
    
    # repeated email used to register
    request_register_v2('thisisavalidemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert(request_register_v2('thisisavalidemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')['code'] == 400)
    
    # passwords too short
    assert(request_register_v2('herewehave.validemail123@gmail.com', '123ab', 'Dylan', 'Meringue')['code'] == 400)
    
    # first/last name not valid (not between 1 and 50 chars in length)
    assert(request_register_v2('herewehaveagain.validemail456@gmail.com', '123abc!@#--', '', 'Internetiquette')['code'] == 400)
    assert(request_register_v2('andagain.validemail456@gmail.com', '123abc!@#--', 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz', 'Internetiquette')['code'] == 400)
    assert(request_register_v2('thelast.validemail456@gmail.com', '123abc!@#--', 'Manuel', '')['code'] == 400)
    assert(request_register_v2('theverylast.validemail456@gmail.com', '123abc!@#--', 'Manuel', 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz')['code'] == 400)


def test_handle(clear):
    # tests for multiple valid registrations but with the same names
    
    reg_result = [0,0,0]
    login_result = [0,0,0]

    reg_result[0] = request_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    reg_result[1] = request_register_v2('yetanother.validemail123@gmail.com', '123abc!@#++', 'Hayden', 'Everest')
    reg_result[2] = request_register_v2('notthisagain.validemail456@gmail.com', '123abc!@#--', 'Hayden', 'Everest')

    login_result[0] = request_login_v2('validemail@gmail.com', '123abc!@#')
    login_result[1] = request_login_v2('yetanother.validemail123@gmail.com', '123abc!@#++')
    login_result[2] = request_login_v2('notthisagain.validemail456@gmail.com', '123abc!@#--')

    for i in range (0, len(reg_result)):
        assert login_result[i]["auth_user_id"] == reg_result[i]["auth_user_id"]


def test_sessions(clear):
    # tests for multiple sessions    

    login_result = [0,0,0]

    reg_result = request_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')

    login_result[0] = request_login_v2('validemail@gmail.com', '123abc!@#')
    login_result[1] = request_login_v2('validemail@gmail.com', '123abc!@#')
    login_result[2] = request_login_v2('validemail@gmail.com', '123abc!@#')
    
    for i in range (0, len(login_result)):
        assert login_result[i]["auth_user_id"] == reg_result["auth_user_id"]


def test_logout(clear, reg_login):
    # test logging out sessions
    lr = reg_login['login_result']
    

    for i in range (0, len(lr)):
        assert request_logout_v2(lr[i]['token'])['is_success']


"""
sends a post request to register (v2)
returns payload
"""
def request_register_v2(email, password, name_first, name_last):
    resp = requests.post(config.url + 'auth/register/v2', json={
        'email' : email,
        'password' : password,
        'name_first' : name_first,
        'name_last' : name_last,
    })
    payload = resp.json()
    return payload


"""
sends a post request to login (v2)
returns payload
"""
def request_login_v2(email, password):
    resp = requests.post(config.url + 'auth/login/v2', json={
        'email' : email,
        'password' : password,
    })
    payload = resp.json()
    return payload


"""
sends a post request to logout (v2)
returns payload
"""
def request_logout_v2(token):
    resp = requests.post(config.url + 'auth/logout/v1', json={
        'token' : token,
    })
    payload = resp.json()
    return payload