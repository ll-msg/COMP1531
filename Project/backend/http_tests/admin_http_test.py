import pytest
import requests
import json
from src import config

from http_tests.auth_http_test import request_register_v2
from http_tests.auth_http_test import request_login_v2
from http_tests.auth_http_test import request_logout_v2


from src.error import InputError
from src.error import AccessError

@pytest.fixture
def clean():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def rr():
    #register three users
    reg_result = [0,0,0]

    reg_result[0] = request_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    reg_result[1] = request_register_v2('yetanother.validemail123@gmail.com', '123abc!@#++', 'Dylan', 'Meringue')
    reg_result[2] = request_register_v2('notthisagain.validemail456@gmail.com', '123abc!@#--', 'Manuel', 'Internetiquette')
    
    return reg_result


def test_permission_change(clean, rr):
    
    # 0 makes 1 an admin then 1 makes 2 an admin
    request_pmc_v1(rr[0]['token'], rr[1]['auth_user_id'], 1)
    request_pmc_v1(rr[1]['token'], rr[2]['auth_user_id'], 1)

    # 2 removes 0 as admin then 1 removes 2 as admin
    request_pmc_v1(rr[2]['token'], rr[0]['auth_user_id'], 2)
    request_pmc_v1(rr[1]['token'], rr[2]['auth_user_id'], 2)


def test_permission_change_fail(clean, rr):
    
    # 1 tries to makes 2 an admin
    assert(request_pmc_v1(rr[1]['token'], rr[2]['auth_user_id'], 1)['code'] == 403)
    
    # 0 tries to remove themselves as the owner (but is the only owner)
    assert(request_pmc_v1(rr[0]['token'], rr[0]['auth_user_id'], 2)['code'] == 400)


def test_remove(clean, rr):

    # 0 makes 1 an admin then 1 makes 2 an admin
    request_pmc_v1(rr[0]['token'], rr[1]['auth_user_id'], 1)
    request_pmc_v1(rr[1]['token'], rr[2]['auth_user_id'], 1)
    
    # 1 removes 2 as an admin
    request_remove_v1(rr[1]['token'], rr[2]['auth_user_id'])
    
    # 0 removes 1 as an admin
    request_remove_v1(rr[0]['token'], rr[1]['auth_user_id'])


def test_remove_fail(clean, rr):
    
    # 1 tries to remove 2 as an admin
    assert(request_remove_v1(rr[1]['token'], rr[2]['auth_user_id'])['code'] == 403)
    
    # 0 tries to remove themselves as the owner (but is the only owner)
    assert(request_remove_v1(rr[0]['token'], rr[0]['auth_user_id'])['code'] == 400)


"""
sends a post request to remove admin (v1)
returns payload
"""
def request_remove_v1(token, u_id):
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token' : token,
        'u_id' : u_id,
    })
    payload = resp.json()
    return payload


"""
sends a post request to change user permission (v1)
returns payload
"""
def request_pmc_v1(token, u_id, permission_id):
    resp = requests.post(config.url + 'admin/userpermission/change/v1', json={
        'token' : token,
        'u_id' : u_id,
        'permission_id' : permission_id,
    })
    payload = resp.json()
    return payload

