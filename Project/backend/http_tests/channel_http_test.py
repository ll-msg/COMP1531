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
    #             0              1            2             3              4            5
    r_list = [owner_token, member_token, channel_id, member_u_id, channel_pri_id, not_member_token]
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
def test_channel_message_input_error_1(invalid_channel):
    # channnel id is unique
    assert requests.get(config.url + '/channel/messages/v2', params = {
        "token" : invalid_channel[0],
        "channel_id" : invalid_channel[1],
        "start" : 0,
    }).status_code == 400

def test_channel_message_input_error_2(set_up_test):
    #start is greater than the total number of messages in the channel
    assert requests.get(config.url + '/channel/messages/v2', params = {
        'token' : set_up_test[0],
        'channel_id' : set_up_test[2],
        'start' : 1,
    }).status_code == 400

def test_channel_message_access_errpr(set_up_test):
    #Authorised user is not a member of channel with channel_id
    assert requests.get(config.url + '/channel/messages/v2', params = {
        "token" : set_up_test[1],
        "channel_id" : set_up_test[2],
        "start" : 0,
    }).status_code == 403

def test_channel_message_success(set_up_test):
    check = requests.get(config.url + '/channel/messages/v2', params = {
        "token" : set_up_test[0],
        "channel_id" : set_up_test[2],
        "start" : 0,
    })
    check = check.json()
    assert check == {'messages': [], 'start': 0, 'end': -1,}

def test_channel_join_InputError(invalid_channel):
    #Channel ID is not a valid channel
    assert requests.post(config.url + '/channel/join/v2', json = {
        "token" : invalid_channel[0],
        "channel_id" :invalid_channel[1],
    }).status_code == 400

def test_channel_join_AccessError(set_up_test):
    assert requests.post(config.url + '/channel/join/v2', json = {
        "token" : set_up_test[1],
        "channel_id" :set_up_test[4],
    }).status_code == 403

def test_channel_join_success(set_up_test):
    # Don't need to check details success case again
    requests.post(config.url + '/channel/join/v2', json = {
        "token" : set_up_test[1],
        "channel_id" :set_up_test[2],
    })
    detail_res = requests.get(config.url + '/channel/details/v2', params = {
        "token" : set_up_test[0],
        "channel_id" : set_up_test[2],
    })
    detail = detail_res.json()
    assert len(detail['all_members']) == 2

def test_channel_details_InputError(invalid_channel):
    #Channel ID is not a valid channel
    assert requests.get(config.url + '/channel/details/v2', params = {
        "token" : invalid_channel[0],
        "channel_id" : invalid_channel[1],
    }).status_code == 400

def test_channel_details_AccessError(set_up_test):
    assert requests.get(config.url + '/channel/details/v2', params = {
        "token" : set_up_test[1],
        "channel_id" : set_up_test[2],
    }).status_code == 403

def test_channel_invite_InputError(invalid_channel):
    assert requests.post(config.url + '/channel/invite/v2', json = {
        "token" : invalid_channel[0],
        "channel_id" :invalid_channel[1],
        'u_id' : invalid_channel[2],
    }).status_code == 400

def test_channel_invite_InputError_u_id():
    requests.delete(config.url + 'clear/v1')
    rsp_global_owner = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmail@gmail.com",
        "password" : "123abc!",
        "name_first" : "Obiwan",
        "name_last" : "Kenobi",
    })
    
    owner = rsp_global_owner.json()
    owner_token = owner['token']
    owner_id = owner['auth_user_id']
    r_channel = requests.post(config.url + '/channels/create/v2', json = {
        "token" : owner_token,
        "name" : "Republic",
        "is_public" : True,
    })
    channel = r_channel.json()
    channel_id = channel['channel_id']
    # user id is unique
    invalid_u_id = owner_id -1
    assert requests.post(config.url + '/channel/invite/v2', json = {
        "token" : owner_token,
        "channel_id" :channel_id,
        'u_id' : invalid_u_id,
    }).status_code == 400

def test_channel_invite_AccessError(set_up_test):
    assert requests.post(config.url + '/channel/invite/v2', json = {
        "token" : set_up_test[5],
        "channel_id" :set_up_test[2],
        'u_id' : set_up_test[3],
    }).status_code == 403
    
def test_channel_invite_success(set_up_test):
    requests.post(config.url + '/channel/invite/v2', json = {
        "token" : set_up_test[0],
        "channel_id" :set_up_test[2],
        'u_id' : set_up_test[3],
    })
    detail_res = requests.get(config.url + '/channel/details/v2', params = {
        "token" : set_up_test[0],
        "channel_id" : set_up_test[2],
    })
    detail = detail_res.json()
    assert len(detail['all_members']) == 2
    requests.delete(config.url + 'clear/v1')
