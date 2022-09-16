import pytest
import requests
import json
from src import config
import src.other
from src.error import InputError
from src.error import AccessError
from datetime import timezone, datetime, timedelta
import time


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



''' test standup start function'''
def test_standup_start_input_1(set_up_test):
    # channel id is invalid
    assert requests.post(config.url + '/standup/start/v1', json= {
        "token": set_up_test[0],
        "channel_id": set_up_test[2] - 10,
        "length": "10"
    }).status_code == 400

def test_standup_start_input_2(set_up_test):
    # there is already a standup in the channel
    requests.post(config.url + '/standup/start/v1', json= {
        "token": set_up_test[0],
        "channel_id": set_up_test[2],
        "length": 10
    }) 
    assert requests.post(config.url + '/standup/start/v1', json= {
        "token": set_up_test[0],
        "channel_id": set_up_test[2],
        "length": 10
    }).status_code == 400

def test_standup_start_access(set_up_test):
    # the authorised user is not already a member of the channel
    assert requests.post(config.url + '/standup/start/v1', json= {
        "token": set_up_test[5],
        "channel_id": set_up_test[2],
        "length": "10"
    }).status_code == 403



def test_standup_start_success(set_up_test):
    create_time = datetime.utcnow() + timedelta(seconds=10)
    time_finish = int(create_time.replace(tzinfo=timezone.utc).timestamp())
    time = requests.post(config.url + '/standup/start/v1', json= {
        "token": set_up_test[0],
        "channel_id": set_up_test[2],
        "length": 10
    }) 
    time_data = time.json()
    assert time_data == {"time_finish": time_finish}




''' test standup active function'''
def test_active_input(set_up_test):
    # channel id is invalid
    assert requests.get(config.url + '/standup/active/v1', params= {
        "token": set_up_test[1],
        "channel_id": set_up_test[2] - 10,
    }).status_code == 400


def test_active_success(set_up_test):
    requests.post(config.url + '/standup/start/v1', json= {
        "token": set_up_test[0],
        "channel_id": set_up_test[2],
        "length": 10
    })
    assert requests.get(config.url + '/standup/active/v1', params= {
        "token": set_up_test[1],
        "channel_id": set_up_test[2],
    }).status_code == 200
  


''' test standup send function'''
def test_send_input_1(invalid_channel):
    # channel id is invalid
    assert requests.post(config.url + '/standup/send/v1', json= {
        "token": invalid_channel[0],
        "channel_id": invalid_channel[1],
        "message": "hello"
    }).status_code == 400
  

def test_send_input_2(set_up_test):
    # when the message is more than 1000 characters
    assert requests.post(config.url + '/standup/send/v1', json= {
        "token": set_up_test[1],
        "channel_id": set_up_test[2],
        "message": "hello" * 5000
    }).status_code == 400


def test_send_input_3(set_up_test):
    # when there is no standup in the channel
    assert requests.post(config.url + '/standup/send/v1', json= {
        "token": set_up_test[0],
        "channel_id": set_up_test[2],
        "message": "hello"
    }).status_code == 400



def test_send_access(set_up_test):
    # the authorised user is not already a member of the channel
    assert requests.post(config.url + '/standup/send/v1', json= {
        "token": set_up_test[5],
        "channel_id": set_up_test[2],
        "message": "hello"
    }).status_code == 403
    requests.delete(config.url + 'clear/v1')


def test_send_success(set_up_test):
    requests.post(config.url + '/standup/start/v1', json= {
        "token": set_up_test[0],
        "channel_id": set_up_test[2],
        "length": 2
    })
    assert requests.post(config.url + '/standup/send/v1', json= {
        "token": set_up_test[0],
        "channel_id": set_up_test[2],
        "message": "hello"
    }).status_code == 200
    requests.delete(config.url + 'clear/v1')    


