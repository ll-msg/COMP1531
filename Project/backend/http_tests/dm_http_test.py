import pytest
import requests
import json
from src import config
import src.other
from src.error import InputError
from src.error import AccessError

@pytest.fixture
def set_up_test():
    requests.delete(config.url + 'clear/v1')
    rsp_global_owner = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vai@gma.com",
        "password" : "123abc!",
        "name_first" : "Obi",
        "name_last" : "K",
    })
    owner = rsp_global_owner.json()
    owner_token = owner['token']

    rsp_member = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vail@gma.com",
        "password" : "123abc!",
        "name_first" : "ma",
        "name_last" : "Y",
    })
    member = rsp_member.json()
    member_token = member['token']
    member_id = member['auth_user_id']

    rsp_non_member = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "va@gma.com",
        "password" : "123abc!!",
        "name_first" : "m",
        "name_last" : "Yo",
    })
    non_member = rsp_non_member.json()
    non_member_token = non_member['token']
    non_member_id = non_member['auth_user_id']

    r_dm = requests.post(config.url + '/dm/create/v1', json = {
        "token" : owner_token,
        "u_ids" : [member_id],
    })
    dm = r_dm.json()
    dm_id = dm['dm_id']
    dm_name = dm['dm_name']
    #             0              1         2        3         4          5                 6
    r_list = [owner_token, member_token, dm_id, member_id, dm_name, non_member_token, non_member_id]
    return r_list
   


''' test create function '''

# test create inputerror - when the given uid does not refer to a valid user
def test_create_inputerror():
    requests.delete(config.url + '/clear/v1')
    # set up testing users
    r1 = requests.post(config.url + "/auth/register/v2", json = {
        "email" : "validmail@gmail.com",
        "password" : "123abc!",
        "name_first" : "Obiwan",
        "name_last" : "Kenobi",
    })
    r1_dic = r1.json()
    r2 = requests.post(config.url + "/auth/register/v2", json = {
        "email" : "valid2mail@gmail.com",
        "password" : "456abc!",
        "name_first" : "master",
        "name_last" : "Yoda",
    })
    r2_dic = r2.json()

    test_invalid_id = r2_dic['auth_user_id'] - 2
    assert requests.post(config.url + "/dm/create/v1", json = {
        "token" : r1_dic['token'],
        "u_ids" :  [test_invalid_id]
    }).status_code == 400
    requests.delete(config.url + 'clear/v1')


def test_create_success(set_up_test):
    r = requests.post(config.url + '/dm/create/v1', json = {
        "token" : set_up_test[0],
        "u_ids" :  [set_up_test[3]]
    })
    test_dic = r.json()
    dm_id = test_dic["dm_id"]
    dm_name = test_dic["dm_name"]
    assert test_dic == {"dm_id" : dm_id, "dm_name" : dm_name}
    requests.delete(config.url + 'clear/v1')

''' test list function '''

def test_list_success(set_up_test):
    resp = requests.get(config.url + '/dm/list/v1', params={'token': set_up_test[0]})
    resp_data = resp.json()
    assert resp_data == {'dms':[{'dm_id' : set_up_test[2], 'name' : set_up_test[4]}]}
    requests.delete(config.url + 'clear/v1')


''' test remove function '''

# check if the given token does not refer to the original creator - AccessError
def test_remove_accesserror(set_up_test):
    assert requests.delete(config.url + '/dm/remove/v1', json = {
        "token" : set_up_test[5],
        "dm_id" : set_up_test[2],
    }).status_code == 403
    requests.delete(config.url + 'clear/v1')

# check if dm_id refers to an existing dm - InputError
def test_remove_inputerror(set_up_test):
    assert requests.delete(config.url + '/dm/remove/v1', json = {
        "token" : set_up_test[1],
        "dm_id" : set_up_test[2] - 19,
    }).status_code == 400
    requests.delete(config.url + 'clear/v1')

def test_remove_success(set_up_test):
    assert requests.delete(config.url + '/dm/remove/v1', json = {
        "token" : set_up_test[0],
        "dm_id" : set_up_test[2],
    }).status_code == 200
    resp = requests.get(config.url + '/dm/list/v1', params={'token': set_up_test[0]})
    resp_data = resp.json()
    assert resp_data == {'dms':[]}
    requests.delete(config.url + 'clear/v1')



''' test invite function '''
def test_invite_success(set_up_test):
    assert requests.post(config.url + '/dm/invite/v1', json = {
        "token" : set_up_test[0],
        "dm_id" : set_up_test[2],
        "u_id"  : set_up_test[6]
    }).status_code == 200
    resp = requests.get(config.url + '/dm/details/v1', params={'token': set_up_test[0], 'dm_id': set_up_test[2]})
    resp_data = resp.json()
    assert resp_data['members'] == [{'email': 'vai@gma.com','handle': 'obik','name_first': 'Obi','name_last': 'K','u_id': 0}, {'email': 'vail@gma.com', 'handle': 'may', 'name_first': 'ma', 'name_last': 'Y', 'u_id': 1}, {'email': 'va@gma.com','handle': 'myo','name_first': 'm','name_last': 'Yo','u_id': 2},]
    requests.delete(config.url + 'clear/v1')

# check if dm_id refers to an existing dm - InputError
def test_invite_inputerror(set_up_test):
    assert requests.post(config.url + '/dm/invite/v1', json = {
        "token" : set_up_test[0],
        "dm_id" : set_up_test[2] - 10,
        "u_id"  : set_up_test[6]
    }).status_code == 400
    requests.delete(config.url + 'clear/v1')

# check if the authorised user is not already a member of the dm - AccessError
def test_invite_accesserror(set_up_test):
    assert requests.post(config.url + '/dm/invite/v1', json = {
        "token" : set_up_test[5],
        "dm_id" : set_up_test[2],
        "u_id"  : set_up_test[6]
    }).status_code == 403
    requests.delete(config.url + 'clear/v1')


''' test leave function '''
# check if dm_id refers to an existing dm - InputError
def test_leave_inputerror(set_up_test):
    assert requests.post(config.url + '/dm/leave/v1', json = {
        "token" : set_up_test[1],
        "dm_id" : set_up_test[2] - 19
    }).status_code == 400
    requests.delete(config.url + 'clear/v1')

# check if the authorised user is not already a member of the dm - AccessError
def test_leave_accesserror(set_up_test):
    assert requests.post(config.url + '/dm/leave/v1', json = {
        "token" : set_up_test[5],
        "dm_id" : set_up_test[2]
    }).status_code == 403
    requests.delete(config.url + 'clear/v1')


def test_leave_success(set_up_test):
    requests.post(config.url + '/dm/leave/v1', json = {
        "token" : set_up_test[1],
        "dm_id" : set_up_test[2]
    })
    resp = requests.get(config.url + '/dm/details/v1', params={'token': set_up_test[0], 'dm_id': set_up_test[2]})
    resp_data = resp.json()
    assert resp_data['members'] == [{'email': 'vai@gma.com','handle': 'obik','name_first': 'Obi','name_last': 'K','u_id': 0},]
    requests.delete(config.url + 'clear/v1')


''' test messages function '''

def test_messages_success(set_up_test):
    resp = requests.get(config.url + '/dm/messages/v1', params={'token': set_up_test[0], 'dm_id': set_up_test[2], 'start': 0})
    resp_data = resp.json()
    assert resp_data == {'end': -1, 'messages': [], 'start': 0}
    requests.delete(config.url + 'clear/v1')

# check if dm_id refers to an existing dm - InputError
def test_messages_inputerror1(set_up_test):
    assert requests.get(config.url + '/dm/messages/v1', params={'token': set_up_test[0], 'dm_id': set_up_test[2] - 19, 'start': 0}).status_code == 400
    requests.delete(config.url + 'clear/v1')

# check if start is greater than the total number of messages - InputError
def test_messages_inputerror2(set_up_test):
    assert requests.get(config.url + '/dm/messages/v1', params={'token': set_up_test[0], 'dm_id': set_up_test[2], 'start': 500}).status_code == 400
    requests.delete(config.url + 'clear/v1')

# check if authorised user is not a member of dm with dm_id - AccessError
def test_messages_accesserror(set_up_test):
    assert requests.get(config.url + '/dm/messages/v1', params={'token': set_up_test[5], 'dm_id': set_up_test[2], 'start': 0}).status_code == 403
    requests.delete(config.url + 'clear/v1')



''' test details function '''

def test_details_success(set_up_test):
    resp = requests.get(config.url + '/dm/details/v1', params={'token': set_up_test[0], 'dm_id': set_up_test[2]})
    resp_data = resp.json()
    assert resp_data['members'] == [{'email': 'vai@gma.com','handle': 'obik','name_first': 'Obi','name_last': 'K','u_id': 0}, {'email': 'vail@gma.com','handle': 'may','name_first': 'ma','name_last': 'Y','u_id': 1}, ]
    requests.delete(config.url + 'clear/v1')

# check if dm_id refers to an existing dm - InputError
def test_details_inputerror(set_up_test):
    assert requests.get(config.url + '/dm/details/v1', params={'token': set_up_test[0], 'dm_id': set_up_test[2] - 10}).status_code == 400
    requests.delete(config.url + 'clear/v1')

# check if authorised user is not a member of dm with dm_id - AccessError
def test_details_accesserror(set_up_test):
    assert requests.get(config.url + '/dm/details/v1', params={'token': set_up_test[5], 'dm_id': set_up_test[2]}).status_code == 403
    requests.delete(config.url + 'clear/v1')