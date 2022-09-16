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
def message_sent():
    # clear funciton at the top of fixture
    requests.delete(config.url + 'clear/v1')
    # create a global user
    rsp_global_owner = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmail@gmail.com",
        "password" : "123abc!",
        "name_first" : "Obiwan",
        "name_last" : "Kenobi",
    })
    owner = rsp_global_owner.json()
    owner_token = owner['token']
    # create a user who will joined the channel later
    rsp_member = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmaitest@gmail.com",
        "password" : "123abc!",
        "name_first" : "master",
        "name_last" : "Yoda",
    })
    member = rsp_member.json()
    member_token = member['token']
    # create a public channel
    r_channel = requests.post(config.url + '/channels/create/v2', json = {
        "token" : owner_token,
        "name" : "Republic",
        "is_public" : True,
    })
    channel = r_channel.json()
    channel_id = channel['channel_id']
    # let the owner of channel send a message
    message = requests.post(config.url + '/message/send/v2', json = {
        "token" : owner_token,
        "channel_id" :channel_id,
        'message' : "test" ,
    })
    message = message.json()
    message_id = message['message_id']
    # let the memebr join the channel
    requests.post(config.url + '/channel/join/v2', json = {
        "token" : member_token,
        "channel_id" :channel_id,
    })
    
    rsp_both_member = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "member@gmai.com",
        "password" : "123abc!",
        "name_first" : "Anakin",
        "name_last" : "Skywalker",
    })
    both_member = rsp_both_member.json()
    both_member_token = both_member['token']
    both_member_id= both_member['auth_user_id']
    # create a public channel
    r_channel_new = requests.post(config.url + '/channels/create/v2', json = {
        "token" : both_member_token,
        "name" : "New Republic",
        "is_public" : True,
    })
    channel = r_channel_new.json()
    new_channel_id = channel['channel_id']
    requests.post(config.url + '/channel/join/v2', json = {
        "token" : both_member_token,
        "channel_id" :channel_id,
    })
    #             0             1           2           3               4               5                   6
    r_list = [owner_token, channel_id, message_id, member_token, both_member_token, new_channel_id, both_member_id]
    return r_list

@pytest.fixture
def dm_set():
    # clear funciton at the top of fixture
    requests.delete(config.url + 'clear/v1')
    # create a global user
    rsp_global_owner = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmail@gmail.com",
        "password" : "123abc!",
        "name_first" : "Obiwan",
        "name_last" : "Kenobi",
    })
    owner = rsp_global_owner.json()
    owner_token = owner['token']
    # create a user who will joined the channel later
    rsp_member = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmaitest@gmail.com",
        "password" : "123abc!",
        "name_first" : "master",
        "name_last" : "Yoda",
    })
    member = rsp_member.json()
    member_token = member['token']
    memeber_uid = member['auth_user_id']

    rsp_not_member = requests.post(config.url + '/auth/register/v2', json = {
    "email" : "member@gmai.com",
    "password" : "123abc!",
    "name_first" : "Anakin",
    "name_last" : "Skywalker",
    })
    not_member = rsp_not_member.json()
    not_member_token = not_member['token']
    
    r = requests.post(config.url + '/dm/create/v1', json = {
        "token" : owner_token,
        "u_ids" :  [memeber_uid]
    })
    test_dic = r.json()
    dm_id = test_dic["dm_id"]
#                   0           1               2               3   
    rec_list = [owner_token, member_token, not_member_token, dm_id]
    return rec_list

def test_message_sent_Accesserror(set_up_test):
    assert requests.post(config.url + '/message/send/v2', json = {
        "token" : set_up_test[5],
        "channel_id" :set_up_test[2],
        'message' : "test",
    }).status_code == 403
    requests.delete(config.url + 'clear/v1')
    
def test_message_sent_InputError(set_up_test):
    assert requests.post(config.url + '/message/send/v2', json = {
        "token" : set_up_test[0],
        "channel_id" :set_up_test[2],
        'message' : "test" * 1000,
    }).status_code == 400
    requests.delete(config.url + 'clear/v1')

def test_message_sent_success(set_up_test):
    requests.post(config.url + '/message/send/v2', json = {
        "token" : set_up_test[0],
        "channel_id" :set_up_test[2],
        'message' : "test" ,
    })
    check = requests.get(config.url + '/channel/messages/v2', params = {
        "token" : set_up_test[0],
        "channel_id" : set_up_test[2],
        "start" : 0,
    })
    check_dic = check.json()
    assert check_dic['messages'][0]['message'] == "test"
    requests.delete(config.url + 'clear/v1')

def test_message_edit_InputError_1(message_sent):
    assert requests.put(config.url + '/message/edit/v2', json = {
        'token' : message_sent[0],
        'message_id' : message_sent[2],
        'message' : 'may the force be with you' * 1000,
    }).status_code == 400
    requests.delete(config.url + 'clear/v1')
    
def test_message_edit_InputError_2(message_sent):
    # delete the message
    requests.put(config.url + '/message/edit/v2', json = {
        'token' : message_sent[0],
        'message_id' : message_sent[2],
        'message' : '',
    })
    # raise input error

    assert requests.put(config.url + '/message/edit/v2', json = {
        'token' : message_sent[0],
        'message_id' : message_sent[2],
        'message' : 'may the force be with you',
    }).status_code == 400
    requests.delete(config.url + 'clear/v1')

def test_message_edit_AccessError(message_sent):
    assert requests.put(config.url + '/message/edit/v2', json = {
        'token' : message_sent[3],
        'message_id' : message_sent[2],
        'message' : 'may the force be with you',
    }).status_code == 403
    requests.delete(config.url + 'clear/v1')

def test_message_edit_success_case(message_sent):
    requests.put(config.url + '/message/edit/v2', json = {
        'token' : message_sent[0],
        'message_id' : message_sent[2],
        'message' : 'may the force be with you',
    })
    check = requests.get(config.url + '/channel/messages/v2', params = {
        "token" : message_sent[0],
        "channel_id" : message_sent[1],
        "start" : 0,
    })
    check = check.json()
    assert check['messages'][0]['message'] == 'may the force be with you'
    requests.delete(config.url + 'clear/v1')

def test_message_remove_InputError(message_sent):
    requests.delete(config.url + '/message/remove/v1', json = {
        'token' : message_sent[0],
        'message_id' : message_sent[2],
    })
    assert requests.delete(config.url + '/message/remove/v1', json = {
        'token' : message_sent[0],
        'message_id' : message_sent[2],
    }).status_code == 400
    requests.delete(config.url + 'clear/v1')

def test_message_remove_AccessError(message_sent):
    assert requests.delete(config.url + '/message/remove/v1', json = {
        'token' : message_sent[3],
        'message_id' : message_sent[2],
    }).status_code == 403
    requests.delete(config.url + 'clear/v1')

def test_message_remove_success(message_sent):
    requests.delete(config.url + '/message/remove/v1', json = {
        'token' : message_sent[0],
        'message_id' : message_sent[2],
    })

    check = requests.get(config.url + '/channel/messages/v2', params = {
        "token" : message_sent[0],
        "channel_id" : message_sent[1],
        "start" : 0,
    })
    check = check.json()
    assert len(check['messages']) == 0
    requests.delete(config.url + 'clear/v1')

def test_message_share_AccessError_message(message_sent):
    assert requests.post(config.url + '/message/share/v1', json = {
        "token" : message_sent[0],
        "og_message_id" : message_sent[2],
        'message' : "test",
        'channel_id' : message_sent[5],
        'dm_id' : -1
    }).status_code == 403
    requests.delete(config.url + 'clear/v1')
def test_message_share_success_share_dm(message_sent):
    r = requests.post(config.url + '/dm/create/v1', json = {
        "token" : message_sent[0],
        "u_ids" : [message_sent[6]],
    })
    test_dic = r.json()
    dm_id = test_dic["dm_id"]
    requests.post(config.url + '/message/share/v1', json = {
        "token" : message_sent[0],
        "og_message_id" : message_sent[2],
        'message' : "share",
        'channel_id' : -1,
        'dm_id' : dm_id
    })
    resp = requests.get(config.url + '/dm/messages/v1', params={
        'token': message_sent[0],
        'dm_id': dm_id, 
        'start': 0,
        })
    resp_data = resp.json()
    assert len(resp_data['messages']) == 1
    requests.delete(config.url + 'clear/v1')


def test_message_share_success(message_sent):
    requests.post(config.url + '/message/share/v1', json = {
        "token" : message_sent[4],
        "og_message_id" : message_sent[2],
        'message' : "share",
        'channel_id' : message_sent[5],
        'dm_id' : -1
    })
    ret_dic = requests.get(config.url + '/channel/messages/v2', params = {
        "token" : message_sent[4],
        "channel_id" : message_sent[5],
        "start" : 0,
    })
    ret_dic = ret_dic.json()
    assert len(ret_dic['messages']) == 1
    requests.delete(config.url + 'clear/v1')

def test_message_senddm_InputError(dm_set):
    assert requests.post(config.url + '/message/senddm/v1', json = {
        "token" : dm_set[0],
        'dm_id' : dm_set[3],
        'message' : "share" * 10001,
    }).status_code == 400
    requests.delete(config.url + 'clear/v1')

def test_message_senddm_AccessError(dm_set):
    assert requests.post(config.url + '/message/senddm/v1', json = {
        "token" : dm_set[2],
        'dm_id' : dm_set[3],
        'message' : "share" ,
    }).status_code == 403
    requests.delete(config.url + 'clear/v1')

def test_message_senddm_success_case(dm_set):
    requests.post(config.url + '/message/senddm/v1', json = {
        "token" : dm_set[0],
        'dm_id' : dm_set[3],
        'message' : "share",
    })
    resp = requests.get(config.url + '/dm/messages/v1', params={
        'token': dm_set[0],
        'dm_id': dm_set[3], 
        'start': 0,
        })
    resp_data = resp.json()
    assert resp_data['messages'][0]['message'] == 'share'
    requests.delete(config.url + 'clear/v1')