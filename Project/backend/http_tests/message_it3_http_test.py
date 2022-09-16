import pytest
import requests
import json
from src import config
from src.error import InputError
from src.error import AccessError
from datetime import timedelta, datetime, timezone
import time

@pytest.fixture
def sent_message():
    requests.delete(config.url + 'clear/v1')
    rsp_global_owner = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmail@gmail.com",
        "password" : "123abc!",
        "name_first" : "Obiwan",
        "name_last" : "Kenobi",
    })
    global_owner = rsp_global_owner.json()
    global_owner_token = global_owner['token']    

    channel_owner = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmaitest@gmail.com",
        "password" : "123abc!",
        "name_first" : "master",
        "name_last" : "Yoda",
    })
    channel_owner = channel_owner.json()
    channel_owner_token = channel_owner['token']

    not_member = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "member@gmai.com",
        "password" : "123abc!",
        "name_first" : "Anakin",
        "name_last" : "Skywalker",
    })
    not_member = not_member.json()
    not_member_token = not_member['token']

    member_join_channel = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "memberjoin@gmai.com",
        "password" : "123abc!",
        "name_first" : "Princess",
        "name_last" : "Leia",
    })
    member_join_channel = member_join_channel.json()
    member_join_channel_token = member_join_channel['token']
    member_join_channel_id = member_join_channel['auth_user_id']

    # create a public channel
    r_channel = requests.post(config.url + '/channels/create/v2', json = {
        "token" : channel_owner_token,
        "name" : "Republic",
        "is_public" : True,
    })
    channel = r_channel.json()
    channel_id = channel['channel_id']

    requests.post(config.url + '/channel/join/v2', json = {
        "token" : member_join_channel_token,
        "channel_id" :channel_id,
    })

    # create a dm
    r = requests.post(config.url + '/dm/create/v1', json = {
        "token" : channel_owner_token,
        "u_ids" :  [member_join_channel_id]
    })
    test_dic = r.json()
    dm_id = test_dic["dm_id"]
    
    # send message to channel
    r = requests.post(config.url + '/message/send/v2', json = {
        "token" : channel_owner_token,
        "channel_id" : channel_id,
        'message' : "hello" ,
    })
    r = r.json()
    channel_message_id = r['message_id']

    # send message to dm
    dm_r = requests.post(config.url + '/message/senddm/v1', json = {
        "token" : channel_owner_token,
        'dm_id' : dm_id,
        'message' : "hello",
    })
    dm_r = dm_r.json()
    dm_message_id = dm_r['message_id']
    #               0                   1                   2                   3                     4         5           6                   7           
    #           gloabl_owner        channel_owner       not_join             memebr               channel       dm      channel_message      dm_message
    return [global_owner_token, channel_owner_token, not_member_token, member_join_channel_token, channel_id, dm_id, channel_message_id, dm_message_id]

@pytest.fixture
def no_message_sent():
    requests.delete(config.url + 'clear/v1')
    rsp_global_owner = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmail@gmail.com",
        "password" : "123abc!",
        "name_first" : "Obiwan",
        "name_last" : "Kenobi",
    })
    global_owner = rsp_global_owner.json()
    global_owner_token = global_owner['token']    

    channel_owner = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmaitest@gmail.com",
        "password" : "123abc!",
        "name_first" : "master",
        "name_last" : "Yoda",
    })
    channel_owner = channel_owner.json()
    channel_owner_token = channel_owner['token']

    not_member = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "member@gmai.com",
        "password" : "123abc!",
        "name_first" : "Anakin",
        "name_last" : "Skywalker",
    })
    not_member = not_member.json()
    not_member_token = not_member['token']

    member_join_channel = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "memberjoin@gmai.com",
        "password" : "123abc!",
        "name_first" : "Princess",
        "name_last" : "Leia",
    })
    member_join_channel = member_join_channel.json()
    member_join_channel_token = member_join_channel['token']
    member_join_channel_id = member_join_channel['auth_user_id']

    # create a public channel
    r_channel = requests.post(config.url + '/channels/create/v2', json = {
        "token" : channel_owner_token,
        "name" : "Republic",
        "is_public" : True,
    })
    channel = r_channel.json()
    channel_id = channel['channel_id']

    requests.post(config.url + '/channel/join/v2', json = {
        "token" : member_join_channel_token,
        "channel_id" :channel_id,
    })

    # create a dm
    r = requests.post(config.url + '/dm/create/v1', json = {
        "token" : channel_owner_token,
        "u_ids" :  [member_join_channel_id]
    })
    test_dic = r.json()
    dm_id = test_dic["dm_id"]
    #               0                   1                   2                   3                      4        5
    #           gloabl_owner        channel_owner       not_join             memebr               channel       dm 
    return [global_owner_token, channel_owner_token, not_member_token, member_join_channel_token, channel_id, dm_id]

@pytest.fixture
def create_timestamp():
    # converting UTC/GMT time to timestamp
    valid_create_time = datetime.utcnow() + timedelta(seconds = 1)
    valid_timestamp = int(valid_create_time.replace(tzinfo=timezone.utc).timestamp())
    invalid_create_time = datetime.utcnow() - timedelta(seconds = 1)
    invalid_timestamp = int(invalid_create_time.replace(tzinfo=timezone.utc).timestamp())
    return [valid_timestamp, invalid_timestamp]


def test_message_send_later_InputError_case1(create_timestamp):
    requests.delete(config.url + 'clear/v1')
    rsp_global_owner = requests.post(config.url + '/auth/register/v2', json = {
    "email" : "vaildmail@gmail.com",
    "password" : "123abc!",
    "name_first" : "Obiwan",
    "name_last" : "Kenobi",
    })
    global_owner = rsp_global_owner.json()
    global_owner_token = global_owner['token']
    invalid_channel_id = -1
    assert requests.post(config.url + '/message/sendlater/v1', json = {
        "token" : global_owner_token,
        "channel_id" :invalid_channel_id,
        'message' : "test",
        'time_sent' : create_timestamp[0],
    }).status_code == 400

def test_message_send_later_InputError_case2(no_message_sent, create_timestamp):
    message = 'hello' * 1000
    assert requests.post(config.url + '/message/sendlater/v1', json = {
        "token" : no_message_sent[1],
        "channel_id" :no_message_sent[4],
        'message' : message,
        'time_sent' : create_timestamp[0],
    }).status_code == 400

def test_message_send_later_InputError_case3(no_message_sent, create_timestamp):
    assert requests.post(config.url + '/message/sendlater/v1', json = {
        "token" : no_message_sent[1],
        "channel_id" :no_message_sent[4],
        'message' : 'hello',
        'time_sent' : create_timestamp[1],
    }).status_code == 400

def test_message_send_later_AccessError_case(no_message_sent, create_timestamp):
    assert requests.post(config.url + '/message/sendlater/v1', json = {
        "token" : no_message_sent[2],
        "channel_id" :no_message_sent[4],
        'message' : 'hello',
        'time_sent' : create_timestamp[0],
    }).status_code == 403

def test_message_send_later_success_case(no_message_sent, create_timestamp):
    requests.post(config.url + '/message/sendlater/v1', json = {
        "token" : no_message_sent[1],
        "channel_id" :no_message_sent[4],
        'message' : 'hello',
        'time_sent' : create_timestamp[0],
    })
    check = requests.get(config.url + '/channel/messages/v2', params = {
        "token" : no_message_sent[1],
        "channel_id" : no_message_sent[4],
        "start" : 0,
    })
    check_idct = check.json()
    assert len(check_idct['messages']) == 1
    
def test_dm_send_later_InputError_case1(create_timestamp):
    requests.delete(config.url + 'clear/v1')
    rsp_global_owner = requests.post(config.url + '/auth/register/v2', json = {
    "email" : "vaildmail@gmail.com",
    "password" : "123abc!",
    "name_first" : "Obiwan",
    "name_last" : "Kenobi",
    })
    global_owner = rsp_global_owner.json()
    global_owner_token = global_owner['token']
    invalid_dm_id = -1
    assert requests.post(config.url + '/message/sendlaterdm/v1', json = {
        "token" : global_owner_token,
        "dm_id" :invalid_dm_id,
        'message' : "test",
        'time_sent' : create_timestamp[0],
    }).status_code == 400

def test_dm_send_later_InputError_case2(no_message_sent, create_timestamp):
    message = 'hello' * 1000
    assert requests.post(config.url + '/message/sendlaterdm/v1', json = {
        "token" : no_message_sent[1],
        "dm_id" :no_message_sent[5],
        'message' : message,
        'time_sent' : create_timestamp[0],
    }).status_code == 400

def test_dm_send_later_InputError_case3(no_message_sent, create_timestamp):
    assert requests.post(config.url + '/message/sendlaterdm/v1', json = {
        "token" : no_message_sent[1],
        "dm_id" :no_message_sent[5],
        'message' : 'hello',
        'time_sent' : create_timestamp[1],
    }).status_code == 400

def test_dm_send_later_AccessError_case(no_message_sent, create_timestamp):
    assert requests.post(config.url + '/message/sendlaterdm/v1', json = {
        "token" : no_message_sent[2],
        "dm_id" :no_message_sent[5],
        'message' : 'hello',
        'time_sent' : create_timestamp[0],
    }).status_code == 403

def test_dm_send_later_Success_case(no_message_sent, create_timestamp):
    requests.post(config.url + '/message/sendlaterdm/v1', json = {
        "token" : no_message_sent[1],
        "dm_id" :no_message_sent[5],
        'message' : 'hello',
        'time_sent' : create_timestamp[0],
    })
    check = requests.get(config.url + '/dm/messages/v1', params = {
        "token" : no_message_sent[1],
        "dm_id" : no_message_sent[5],
        "start" : 0,
    })
    check_idct = check.json()
    assert len(check_idct['messages']) == 1

def test_message_pin_InputError_case1(no_message_sent):
    invalid_message_id = -1
    assert requests.post(config.url + '/message/pin/v1', json = {
        "token" : no_message_sent[1],
        "message_id": invalid_message_id,
    }).status_code == 400

def test_message_pin_InputError_case2(sent_message):
    requests.post(config.url + '/message/pin/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
    })
    assert requests.post(config.url + '/message/pin/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
    }).status_code == 400

def test_message_pin_AccessError_case1(sent_message):
    assert requests.post(config.url + '/message/pin/v1', json = {
        "token" : sent_message[2],
        "message_id": sent_message[6],
    }).status_code == 403

def test_message_pin_AccessError_case2(sent_message):
    assert requests.post(config.url + '/message/pin/v1', json = {
        "token" : sent_message[3],
        "message_id": sent_message[6],
    }).status_code == 403

def test_message_pin_Success_case(sent_message):
    requests.post(config.url + '/message/pin/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
    })
    check = requests.get(config.url + '/channel/messages/v2', params = {
        "token" : sent_message[1],
        "channel_id" : sent_message[4],
        "start" : 0,
    })
    check_dict = check.json()
    assert check_dict['messages'][0]['is_pinned'] == True

def test_message_unpin_InputError_case1(no_message_sent):
    invalid_message_id = -1
    assert requests.post(config.url + '/message/unpin/v1', json = {
        "token" : no_message_sent[1],
        "message_id": invalid_message_id,
    }).status_code == 400

def test_message_unpin_InputError_case2(sent_message):
    requests.post(config.url + '/message/pin/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
    })
    requests.post(config.url + '/message/unpin/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
    })
    assert requests.post(config.url + '/message/unpin/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
    }).status_code == 400

def test_message_unpin_Accesserror_case1(sent_message):
    requests.post(config.url + '/message/pin/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
    })
    assert requests.post(config.url + '/message/unpin/v1', json = {
        "token" : sent_message[2],
        "message_id": sent_message[6],
    }).status_code == 403

def test_message_unpin_Accesserror_case2(sent_message):
    requests.post(config.url + '/message/pin/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
    })
    assert requests.post(config.url + '/message/unpin/v1', json = {
        "token" : sent_message[3],
        "message_id": sent_message[6],
    }).status_code == 403

def test_message_unpin_success_case(sent_message):
    requests.post(config.url + '/message/pin/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
    })
    requests.post(config.url + '/message/unpin/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
    })
    check = requests.get(config.url + '/channel/messages/v2', params = {
        "token" : sent_message[1],
        "channel_id" : sent_message[4],
        "start" : 0,
    })
    check_dict = check.json()
    assert check_dict['messages'][0]['is_pinned'] == False

def test_message_react_InputError_case1(no_message_sent):
    invalid_message_id = -1
    assert requests.post(config.url + '/message/react/v1', json = {
        "token" : no_message_sent[1],
        "message_id": invalid_message_id,
        "react_id" : 1,
    }).status_code == 400

def test_message_react_InputError_case2(sent_message):
    assert requests.post(config.url + '/message/react/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
        "react_id" : 2,
    }).status_code == 400

def test_message_react_InputError_case3(sent_message):
    requests.post(config.url + '/message/react/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
        "react_id" : 1,
    })
    assert requests.post(config.url + '/message/react/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
        "react_id" : 1,
    }).status_code == 400

def test_message_react_AccessError_case(sent_message):
    assert requests.post(config.url + '/message/react/v1', json = {
        "token" : sent_message[2],
        "message_id": sent_message[6],
        "react_id" : 1,
    }).status_code == 403

def test_message_react_Success_case(sent_message):
    requests.post(config.url + '/message/react/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
        "react_id" : 1,
    })
    check = requests.get(config.url + '/channel/messages/v2', params = {
        "token" : sent_message[1],
        "channel_id" : sent_message[4],
        "start" : 0,
    })
    check_dict = check.json()
    assert len(check_dict['messages'][0]['reacts'][0]['u_ids']) == 1

def test_message_unreact_InputError_case1(no_message_sent):
    invalid_message_id = -1
    assert requests.post(config.url + '/message/unreact/v1', json = {
        "token" : no_message_sent[1],
        "message_id": invalid_message_id,
        "react_id" : 1,
    }).status_code == 400

def test_message_unreact_InputError_case2(sent_message):
    assert requests.post(config.url + '/message/unreact/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
        "react_id" : 2,
    }).status_code == 400

def test_message_unreact_InputError_case3(sent_message):
    requests.post(config.url + '/message/react/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
        "react_id" : 1,
    })
    requests.post(config.url + '/message/unreact/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
        "react_id" : 1
    })
    assert requests.post(config.url + '/message/unreact/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
        "react_id" : 1
    }).status_code == 400

def test_message_unreact_AccessError_case1(sent_message):
    assert requests.post(config.url + '/message/unreact/v1', json = {
        "token" : sent_message[2],
        "message_id": sent_message[7],
        "react_id" : 1
    }).status_code == 403

def test_message_unreact_success_case1(sent_message):
    requests.post(config.url + '/message/react/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
        "react_id" : 1,
    })
    requests.post(config.url + '/message/react/v1', json = {
        "token" : sent_message[3],
        "message_id": sent_message[6],
        "react_id" : 1,
    })
    requests.post(config.url + '/message/unreact/v1', json = {
        "token" : sent_message[1],
        "message_id": sent_message[6],
        "react_id" : 1
    })
    check = requests.get(config.url + '/channel/messages/v2', params = {
        "token" : sent_message[1],
        "channel_id" : sent_message[4],
        "start" : 0,
    })
    check_dict = check.json()
    assert len(check_dict['messages'][0]['reacts'][0]['u_ids']) == 1