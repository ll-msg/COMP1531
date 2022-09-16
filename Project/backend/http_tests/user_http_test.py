import pytest
import requests
import json
from src import config
from src.error import InputError
from src.error import AccessError

@pytest.fixture
def set_up_one_user():
    requests.delete(config.url + 'clear/v1')
    r = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "harbinger11@gmail.com",
        "password" : "123abc!",
        "name_first" : "Ajax",
        "name_last" : "Tartaglia",
    })
    return_dic = r.json()
    return return_dic['token']

def test_user_profile(set_up_one_user):
    r = requests.get(config.url + '/user/profile/v2', params = {
        'token': set_up_one_user,
        'u_id': 0
    })
    r = r.json()
    assert r == {
        'user': {
                'u_id': 0,
                'email': 'harbinger11@gmail.com',
                'name_first': 'Ajax',
                'name_last': 'Tartaglia',
                'handle_str': 'ajaxtartaglia',
                'profile_img_url' : '',
            }
    }

def test_user_profile_setemail_success(set_up_one_user):
    requests.put(config.url + '/user/profile/setemail/v2', json = {
        'token': set_up_one_user,
        'email': 'childe@gmail.com'
    })
    
    check = requests.get(config.url + '/user/profile/v2', params = {
        'token': set_up_one_user,
        'u_id': 0,
    })
    
    check = check.json()
    assert check['user']['email'] == 'childe@gmail.com' 

def test_user_profile_setemail_inputerror_invalid(set_up_one_user):
    #returns input error as email is invalid
    assert requests.put(config.url + '/user/profile/setemail/v2', json = {
        'token': set_up_one_user,
        'email': ''
    }).status_code == 400
    
def test_user_profile_setemail_inputerror_inuse(set_up_one_user):
    #set up second user 
    requests.post(config.url + '/auth/register/v2', json = {
        "email" : "fatui@gmail.com",
        "password" : "123abc!",
        "name_first" : "Scaramouche",
        "name_last" : "Balladeer",
    })
    
    #returns input error as email is in use
    assert requests.put(config.url + '/user/profile/setemail/v2', json = {
        'token': set_up_one_user,
        'email': 'fatui@gmail.com'
    }).status_code == 400
    
def test_user_profile_setemail_accesserror(set_up_one_user):
    #returns access error as token is invalid
    assert requests.put(config.url + '/user/profile/setemail/v2', json = {
        'token': '',
        'email': 'childe@gmail.com'
    }).status_code == 403
    
def test_user_profile_setname_success(set_up_one_user):
    requests.put(config.url + '/user/profile/setname/v2', json = {
        'token': set_up_one_user,
        'name_first': 'Childe',
        'name_last': 'Harbinger',
    })
    
    check = requests.get(config.url + '/user/profile/v2', params = {
        'token': set_up_one_user,
        'u_id': 0,
    })
    
    check = check.json()
    assert check['user']['name_first'] == 'Childe'
    assert check['user']['name_last'] == 'Harbinger'

def test_user_profile_setname_inputerror_first(set_up_one_user):
    #returns input error as first name does not meet reqs
    assert requests.put(config.url + '/user/profile/setname/v2', json = {
        'token': set_up_one_user,
        'name_first': '',
        'name_last': 'Harbinger',
    }).status_code == 400
    
def test_user_profile_setname_inputerror_last(set_up_one_user):
    #returns input error as last name does not meet reqs
    assert requests.put(config.url + '/user/profile/setname/v2', json = {
        'token': set_up_one_user,
        'name_first': 'Childe',
        'name_last': '',
    }).status_code == 400

def test_user_profile_setname_accesserror(set_up_one_user):
    #returns access error as token is invalid
    assert requests.put(config.url + '/user/profile/setname/v2', json = {
        'token': '',
        'name_first': 'Childe',
        'name_last': 'Harbinger',
    }).status_code == 403
    
def test_user_profile_sethandle_success(set_up_one_user):
    requests.put(config.url + '/user/profile/sethandle/v1', json = {
        'token': set_up_one_user,
        'handle_str': 'fatuiharbinger',
    })
    
    check = requests.get(config.url + '/user/profile/v2', params = {
        'token': set_up_one_user,
        'u_id': 0,
    })
    
    check = check.json()
    assert check['user']['handle_str'] == 'fatuiharbinger'

def test_user_profile_sethandle_inputerror_invalid(set_up_one_user):
    #returns input error as handle does not meet reqs
    assert requests.put(config.url + '/user/profile/sethandle/v1', json = {
        'token': set_up_one_user,
        'handle_str': ''
    }).status_code == 400

def test_user_profile_sethandle_inputerror_inuse(set_up_one_user):
    #set up second user
    requests.post(config.url + '/auth/register/v2', json = {
        "email" : "fatui@gmail.com",
        "password" : "123abc!",
        "name_first" : "Fatui",
        "name_last" : "Harbinger",
    })
    
    #returns input error as handle is already in use 
    assert requests.put(config.url + '/user/profile/sethandle/v1', json = {
        'token': set_up_one_user,
        'handle_str': 'fatuiharbinger'
    }).status_code == 400

def test_user_profile_sethandle_accesserror(set_up_one_user):
    #returns access error as token is invalid
    assert requests.put(config.url + '/user/profile/sethandle/v1', json = {
        'token': '',
        'handle_str': 'fatuiharbinger',
    }).status_code == 403

