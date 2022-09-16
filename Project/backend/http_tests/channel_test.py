import pytest
import requests
import json
from src import config
from src.error import InputError
from src.error import AccessError

@pytest.fixture
def set_up_test():
    requests.delete(config.url + 'clear/v1')
    rsp_global_owner = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmail@gmail.com",
        "password" : "123abc!",
        "name_first" : "Obiwan",
        "name_last" : "Kenobi",
    })
    owner = rsp_global_owner.json()
    owner_token = owner['token']
    owner_u_id = owner['auth_user_id']

    rsp_member = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmaitest@gmail.com",
        "password" : "123abc!",
        "name_first" : "master",
        "name_last" : "Yoda",
    })
    member = rsp_member.json()
    member_token = member['token']
    member_u_id = member['auth_user_id']

    rsp_not_member = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "member@gmai.com",
        "password" : "123abc!",
        "name_first" : "Anakin",
        "name_last" : "Skywalker",
    })
    not_member = rsp_not_member.json()
    not_member_token = not_member['token']

    r_channel = requests.post(config.url + '/channels/create/v2', json = {
        "token" : owner_token,
        "name" : "Republic",
        "is_public" : True,
    })
    channel = r_channel.json()
    channel_id = channel['channel_id']

    r_channel_pri = requests.post(config.url + '/channels/create/v2', json = {
        "token" : owner_token,
        "name" : "Empire",
        "is_public" : False,
    })
    channel_pri = r_channel_pri.json()
    channel_pri_id = channel_pri['channel_id']
    #             0              1            2             3              4            5                6
    r_list = [owner_token, member_token, channel_id, member_u_id, channel_pri_id, not_member_token, owner_u_id]
    return r_list

@pytest.fixture
def invalid_channel():
    requests.delete(config.url + 'clear/v1')
    rsp_global_owner = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmail@gmail.com",
        "password" : "123abc!",
        "name_first" : "Obiwan",
        "name_last" : "Kenobi",
    })
    
    owner = rsp_global_owner.json()
    owner_token = owner['token']
    rsp_member = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmaitest@gmail.com",
        "password" : "123abc!",
        "name_first" : "master",
        "name_last" : "Yoda",
    })
    member = rsp_member.json()
    member_u_id = member['auth_user_id']

    r_channel = requests.post(config.url + '/channels/create/v2', json = {
        "token" : owner_token,
        "name" : "Republic",
        "is_public" : True,
    })
    channel = r_channel.json()
    channel_id = channel['channel_id']

    invalid_channel_id = channel_id - 1
    #               0               1               2
    re_list = [owner_token, invalid_channel_id, member_u_id]
    return re_list

def test_addowner_input_error_1(invalid_channel):
    # channel id is invalid
    assert requests.post(config.url + '/channel/addowner/v1', json = {
        "token": invalid_channel[0],
        "channel_id" : invalid_channel[1],
        "u_id": invalid_channel[2],
    }).status_code == 400

def test_addowner_input_error_2(set_up_test):
    # owner tries to assign himself as owner
    assert requests.post(config.url + '/channel/addowner/v1', json = {
        "token": set_up_test[0],
        "channel_id": set_up_test[2],
        "u_id": set_up_test[6],
    }).status_code == 400

def test_addowner_access_error(set_up_test):
    #user is not authorised 
    assert requests.post(config.url + '/channel/addowner/v1', json = {
        "token": set_up_test[1],
        "channel_id": set_up_test[2],
        "u_id": set_up_test[3],
    }).status_code == 403

def test_addowner_success(set_up_test):
    requests.post(config.url + '/channel/addowner/v1', json = {
        "token": set_up_test[0],
        "channel_id": set_up_test[2],
        "u_id": set_up_test[3],
    })
    detail_res = requests.get(config.url + '/channel/details/v2', params = {
        "token" : set_up_test[0],
        "channel_id" : set_up_test[2],
    })
    detail = detail_res.json()
    print(detail)
    assert len(detail['owner_members']) == 2

def test_removeowner_input_error_1(invalid_channel):
    # channel id is invalid
    assert requests.post(config.url + '/channel/removeowner/v1', json = {
        "token": invalid_channel[0],
        "channel_id": invalid_channel[1],
        "u_id": invalid_channel[2],
    }).status_code == 400

def test_removeowner_input_error_2(set_up_test):
    # user is not an owner of the channel
    assert requests.post(config.url + '/channel/removeowner/v1', json = {
        "token": set_up_test[0],
        "channel_id": set_up_test[2],
        "u_id": set_up_test[3],
    }).status_code == 400

def test_removeowner_input_error_3(set_up_test):
    # sole owner tries to remove themselves
    assert requests.post(config.url + '/channel/removeowner/v1', json = {
        "token": set_up_test[0],
        "channel_id": set_up_test[2],
        "u_id": set_up_test[6],
    }).status_code == 400

def test_removeowner_success(set_up_test):
    # make member an owner
    requests.post(config.url + '/channel/addowner/v1', json = {
        "token": set_up_test[0],
        "channel_id": set_up_test[2],
        "u_id": set_up_test[3],
    })

    detail_res = requests.get(config.url + '/channel/details/v2', params = {
        "token" : set_up_test[0],
        "channel_id" : set_up_test[2],
    })
    detail = detail_res.json()
    assert len(detail['owner_members']) == 2

    # remove member as owner
    requests.post(config.url + '/channel/removeowner/v1', json = {
        "token": set_up_test[0],
        "channel_id": set_up_test[2],
        "u_id": set_up_test[3],
    })

    detail_res = requests.get(config.url + '/channel/details/v2', params = {
        "token" : set_up_test[0],
        "channel_id" : set_up_test[2],
    })
    detail = detail_res.json()
    assert len(detail['owner_members']) == 1

def test_leave_input_error(invalid_channel):
    # channel id is invalid
    assert requests.post(config.url + '/channel/leave/v1', json = {
        "token": invalid_channel[0],
        "channel_id": invalid_channel[1],
    }).status_code == 400

def test_leave_access_error(set_up_test):
    assert requests.post(config.url + '/channel/leave/v1', json = {
        "token": set_up_test[5],
        "channel_id": set_up_test[2],
    }).status_code == 403

def test_leave_success(set_up_test):
    requests.post(config.url + '/channel/leave/v1', json = {
        "token" : set_up_test[1],
        "channel_id" : set_up_test[2],
    })

    detail_res = requests.get(config.url + '/channel/details/v2', params = {
        "token" : set_up_test[0],
        "channel_id" : set_up_test[2],
    })
    detail = detail_res.json()
    assert len(detail['all_members']) == 1
    requests.delete(config.url + 'clear/v1')