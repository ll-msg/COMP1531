import pytest
from src.error import InputError
from src.error import AccessError
import src.other
from src.auth import auth_register_v2
from src.message import message_send_v2, message_remove_v1, message_edit_v2, message_share_v1, message_senddm_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1, message_sendlater_v1, message_sendlaterdm_v1
from src.channel import channel_messages_v2, channel_join_v2
from src.channels import channels_create_v2
from src.dm import dm_create_v1, dm_messages_v1
from src.other import clear_v1
from datetime import timedelta, datetime, timezone
import time


@pytest.fixture
def no_message_been_sent():
    clear_v1()
    # Create  new  test accounts
    # Global onwer who is the first user in Dream
    global_owner = auth_register_v2('vaildmail@gmail.com', '123abc!', 'Obiwan', 'Kenobi')
    global_owner_token = global_owner['token']
    # User own the channel/dm
    channel_onwer = auth_register_v2('owner@gmail.com', '12312afc!', 'Boba', 'Fett')
    channel_owner_token = channel_onwer['token']
    # User who didnt join the channel/dm
    not_memeber = auth_register_v2('member@gmail.com', '321abc!', 'Anakin', 'Skywalker' )
    not_memeber_token = not_memeber['token']
    # User who joined the channel/dm 
    member_join_channel =  auth_register_v2('joinchannel@gmail.com', 'abc123!', 'Count', 'Dooku')
    member_join_channel_token = member_join_channel['token']
    member_join_channel_uid = member_join_channel['auth_user_id']
    # Use who joined the channel/dm
    memebr_inchannel_sendmessage = auth_register_v2('sendmessage@gmail.com', 'wksj123!', 'Princess', 'Leia')
    memebr_inchannel_sendmessage_token = memebr_inchannel_sendmessage['token']
    member_send_uid = memebr_inchannel_sendmessage['auth_user_id']
    # Create a public channel
    public_channel = channels_create_v2(channel_owner_token, 'public', True)
    public_channel = public_channel['channel_id']
    # Let member_join_channel join in the channel
    channel_join_v2(member_join_channel_token, public_channel)
    channel_join_v2(memebr_inchannel_sendmessage_token, public_channel)
    # create a dm, creator is channel_owner and members are member_join_channel and memebr_inchannel_sendmessage
    dm = dm_create_v1(channel_owner_token,[member_join_channel_uid, member_send_uid])
    dm_id = dm['dm_id']
    #                  gloabl owner|    channel/dm owner |user didnt joined|    user joined channel/dm    |  user joined channel/dm        |public channel id| dm id
    #                      0                     1                2                      3                              4                          5           6
    return_list = [global_owner_token, channel_owner_token, not_memeber_token, member_join_channel_token, memebr_inchannel_sendmessage_token, public_channel, dm_id]
    return return_list

@pytest.fixture
def create_timestamp():
    # converting UTC/GMT time to timestamp
    valid_create_time = datetime.utcnow() + timedelta(seconds = 1)
    valid_timestamp = int(valid_create_time.replace(tzinfo=timezone.utc).timestamp())
    invalid_create_time = datetime.utcnow() - timedelta(seconds = 1)
    invalid_timestamp = int(invalid_create_time.replace(tzinfo=timezone.utc).timestamp())
    return [valid_timestamp, invalid_timestamp]

def test_message_react_InputError_case1(no_message_been_sent):
    # message_id is invalid
    invalid_message_id = -1
    with pytest.raises(InputError):
        message_react_v1(no_message_been_sent[1], invalid_message_id, 1)
    
def test_message_react_InputError_case2(no_message_been_sent):
    # react_id is not a valid React ID. The only valid react ID the frontend has is 1
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    with pytest.raises(InputError):
        message_react_v1(no_message_been_sent[1], test_message_id, -1)

def test_message_react_InputError_case3(no_message_been_sent):
    # message with ID message_id already contains an active React with ID react_id from the authorised user
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    message_react_v1(no_message_been_sent[1], test_message_id, 1)
    with pytest.raises(InputError):
        message_react_v1(no_message_been_sent[1], test_message_id, 1)

def test_message_react_AccessError_case1(no_message_been_sent):
    # message_id is not a valid message within a channel that the authorised user has joined
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    with pytest.raises(AccessError):
        message_react_v1(no_message_been_sent[2], test_message_id, 1)

def test_message_react_AccessError_case2(no_message_been_sent):
    # message_id is not a valid message within a DM that the authorised user has joined
    test_message_id = message_senddm_v1(no_message_been_sent[1], no_message_been_sent[6], 'hello')['message_id']
    with pytest.raises(AccessError):
        message_react_v1(no_message_been_sent[2], test_message_id, 1)

def test_message_react_success_case1(no_message_been_sent):
    # message react in channel
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    message_react_v1(no_message_been_sent[1], test_message_id, 1)
    assert channel_messages_v2(no_message_been_sent[1], no_message_been_sent[5], 0)['messages'][0]['reacts'][0]['react_id'] == 1

def test_message_react_success_case2(no_message_been_sent):
    # message react in dm
    test_message_id = message_senddm_v1(no_message_been_sent[1], no_message_been_sent[6], 'hello')['message_id']
    message_react_v1(no_message_been_sent[1], test_message_id, 1)
    assert dm_messages_v1(no_message_been_sent[1], no_message_been_sent[6], 0)['messages'][0]['reacts'][0]['react_id'] == 1

def test_message_unreact_InputError_case1(no_message_been_sent):
    # message id is invalid
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    message_react_v1(no_message_been_sent[1], test_message_id, 1)
    # remove the message with test_message_id which has been reacted before
    message_remove_v1(no_message_been_sent[1], test_message_id)
    with pytest.raises(InputError):
        message_unreact_v1(no_message_been_sent[1], test_message_id, 1)

def test_message_unreact_InputError_case2(no_message_been_sent):
    # react_id is not a valid React ID
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    message_react_v1(no_message_been_sent[1], test_message_id, 1)
    with pytest.raises(InputError):
        message_unreact_v1(no_message_been_sent[1], test_message_id, -1)

def test_message_unreact_InputError_case3(no_message_been_sent):
    # message with ID message_id does not contain an active React with ID react_id from the authorised user
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    message_react_v1(no_message_been_sent[1], test_message_id, 1)
    message_unreact_v1(no_message_been_sent[1], test_message_id, 1)
    with pytest.raises(InputError):
        message_unreact_v1(no_message_been_sent[1], test_message_id, 1)

def test_message_unreact_AccessError_case1(no_message_been_sent):
    # the authorised user is not a member of the channel that the message is within
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    message_react_v1(no_message_been_sent[1], test_message_id, 1)
    with pytest.raises(AccessError):
        message_unreact_v1(no_message_been_sent[2], test_message_id, 1)

def test_message_unreact_AccessError_case2(no_message_been_sent):
    # the authorised user is not a member of the dm that the message is within
    test_message_id = message_senddm_v1(no_message_been_sent[1], no_message_been_sent[6], 'hello')['message_id']
    message_react_v1(no_message_been_sent[1], test_message_id, 1)
    with pytest.raises(AccessError):
        message_unreact_v1(no_message_been_sent[2], test_message_id, 1)

def test_message_unreact_success_case1(no_message_been_sent):
    # unreact message in channel
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    message_react_v1(no_message_been_sent[1], test_message_id, 1)
    message_react_v1(no_message_been_sent[3], test_message_id, 1)
    message_unreact_v1(no_message_been_sent[1], test_message_id, 1)
    assert len(channel_messages_v2(no_message_been_sent[1], no_message_been_sent[5], 0)['messages'][0]['reacts'][0]['u_ids']) == 1

def test_message_unreact_success_case2(no_message_been_sent):
    # unreact message in dm
    test_message_id = message_senddm_v1(no_message_been_sent[1], no_message_been_sent[6], 'hello')['message_id']
    message_react_v1(no_message_been_sent[1], test_message_id, 1)
    message_react_v1(no_message_been_sent[3], test_message_id, 1)
    message_unreact_v1(no_message_been_sent[1], test_message_id, 1)
    assert len(dm_messages_v1(no_message_been_sent[1], no_message_been_sent[6], 0)['messages'][0]['reacts'][0]['u_ids']) == 1

def test_message_pin_InputError_case1(no_message_been_sent):
    # message_id is not a valid message
    # no message has been sent yet
    invalid_message_id = -1
    with pytest.raises(InputError):
        message_pin_v1(no_message_been_sent[1], invalid_message_id)

def test_message_pin_InputError_case2(no_message_been_sent):
    # message with ID message_id is already pinned
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    message_pin_v1(no_message_been_sent[1], test_message_id)
    with pytest.raises(InputError):
        message_pin_v1(no_message_been_sent[1], test_message_id)

def test_message_pin_AccessError_case1(no_message_been_sent):
    # the authorised user is not a member of the channel that the message is within
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    with pytest.raises(AccessError):
        message_pin_v1(no_message_been_sent[2], test_message_id)

def test_message_pin_AccessError_case2(no_message_been_sent):
    # the authorised user is not an owner of the channel or DM
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    with pytest.raises(AccessError):
        message_pin_v1(no_message_been_sent[4], test_message_id)

def test_message_pin_AccessError_case3(no_message_been_sent):
    # the authorised user is not a member of the DM that the message is within
    test_message_id = message_senddm_v1(no_message_been_sent[1], no_message_been_sent[6], 'hello')['message_id']
    with pytest.raises(AccessError):
        message_pin_v1(no_message_been_sent[2], test_message_id)

def test_message_pin_success_case1(no_message_been_sent):
    # pin message in channel
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    message_pin_v1(no_message_been_sent[1], test_message_id)
    assert channel_messages_v2(no_message_been_sent[1], no_message_been_sent[5], 0)['messages'][0]['is_pinned'] == True

def test_message_pin_success_case2(no_message_been_sent):
    # pin message in dm
    test_message_id = message_senddm_v1(no_message_been_sent[1], no_message_been_sent[6], 'hello')['message_id']
    message_pin_v1(no_message_been_sent[1], test_message_id)
    assert dm_messages_v1(no_message_been_sent[1], no_message_been_sent[6], 0)['messages'][0]['is_pinned'] == True

def test_message_unpin_InputError_case1(no_message_been_sent):
    # message_id is not a valid message
    # no message has been sent yet
    invalid_message_id = -1
    with pytest.raises(InputError):
        message_unpin_v1(no_message_been_sent[1], invalid_message_id)

def test_message_unpin_InputError_case2(no_message_been_sent):
    # message with ID message_id is already unpinned
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    message_pin_v1(no_message_been_sent[1], test_message_id)
    # unpin the message
    message_unpin_v1(no_message_been_sent[1], test_message_id)
    with pytest.raises(InputError):
        message_unpin_v1(no_message_been_sent[1], test_message_id)

def test_message_unpin_AccessError_case1(no_message_been_sent):
    # the authorised user is not a member of the channel that the message is within
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    message_pin_v1(no_message_been_sent[1], test_message_id)
    with pytest.raises(AccessError):
        message_unpin_v1(no_message_been_sent[2], test_message_id)

def test_message_unpin_AccessError_case2(no_message_been_sent):
    # the authorised user is not an owner of the channel or DM
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    message_pin_v1(no_message_been_sent[1], test_message_id)
    with pytest.raises(AccessError):
        message_unpin_v1(no_message_been_sent[4], test_message_id)

def test_message_unpin_AccessError_case3(no_message_been_sent):
    # the authorised user is not a member of the DM that the message is within
    test_message_id = message_senddm_v1(no_message_been_sent[1], no_message_been_sent[6], 'hello')['message_id']
    message_pin_v1(no_message_been_sent[1], test_message_id)
    with pytest.raises(AccessError):
        message_unpin_v1(no_message_been_sent[2], test_message_id)

def test_message_unpin_success_case1(no_message_been_sent):
    # unpin the message in channel
    test_message_id = message_send_v2(no_message_been_sent[1], no_message_been_sent[5], 'hello')['message_id']
    message_pin_v1(no_message_been_sent[1], test_message_id)
    message_unpin_v1(no_message_been_sent[1], test_message_id)
    assert channel_messages_v2(no_message_been_sent[1], no_message_been_sent[5], 0)['messages'][0]['is_pinned'] == False

def test_message_unpin_success_case2(no_message_been_sent):
    # unpin the message in dm
    test_message_id = message_senddm_v1(no_message_been_sent[1], no_message_been_sent[6], 'hello')['message_id']
    message_pin_v1(no_message_been_sent[1], test_message_id)
    message_unpin_v1(no_message_been_sent[1], test_message_id)
    assert dm_messages_v1(no_message_been_sent[1], no_message_been_sent[6], 0)['messages'][0]['is_pinned'] == False


def test_message_sendlater_InputError_case1(create_timestamp):
    clear_v1()
    # Create  new  test accounts
    # Global onwer who is the first user in Dream
    global_owner = auth_register_v2('vaildmail@gmail.com', '123abc!', 'Obiwan', 'Kenobi')
    global_owner_token = global_owner['token']
    # Channel ID is not a valid channel
    # currently Dream doesnt have any channel
    invalid_channel_id = -1
    with pytest.raises(InputError):
        message_sendlater_v1(global_owner_token, invalid_channel_id, 'hello', create_timestamp[0])
    
def test_message_sendlater_InputError_case2(no_message_been_sent, create_timestamp):
    
    # message is more than 1000
    message = 'hello' * 1000
    with pytest.raises(InputError):
        message_sendlater_v1(no_message_been_sent[1], no_message_been_sent[5], message, create_timestamp[0])

def test_message_sendlater_InputError_case3(no_message_been_sent, create_timestamp):
    # time sent is a time in the past
    with pytest.raises(InputError):
        message_sendlater_v1(no_message_been_sent[1], no_message_been_sent[5], 'hello', create_timestamp[1])

def test_message_sendlater_AccessError_case(no_message_been_sent, create_timestamp):
    # when: the authorised user has not joined the channel they are trying to post to
    with pytest.raises(AccessError):
        message_sendlater_v1(no_message_been_sent[2], no_message_been_sent[5], 'hello', create_timestamp[0])

def test_message_sendlater_success_case(no_message_been_sent, create_timestamp):
    test = message_sendlater_v1(no_message_been_sent[1], no_message_been_sent[5], 'hello', create_timestamp[0])
    time.sleep(1)
    assert len(test) == 1

def test_message_senddmlater_InputError_case1(create_timestamp):
    clear_v1()
    # Create  new  test accounts
    # Global onwer who is the first user in Dream
    global_owner = auth_register_v2('vaildmail@gmail.com', '123abc!', 'Obiwan', 'Kenobi')
    global_owner_token = global_owner['token']
    # Channel ID is not a valid channel
    # currently Dream doesnt have any DM
    invalid_dm_id = -1
    with pytest.raises(InputError):
        message_sendlaterdm_v1(global_owner_token, invalid_dm_id, 'hello', create_timestamp[0])

def test_message_senddmlater_InputError_case2(no_message_been_sent, create_timestamp):
    # message is more than 1000
    message = 'hello' * 1000
    with pytest.raises(InputError):
        message_sendlaterdm_v1(no_message_been_sent[1], no_message_been_sent[6], message, create_timestamp[0])

def test_message_senddmlater_InputError_case3(no_message_been_sent, create_timestamp):
    # Time sent is a time in the past
    with pytest.raises(InputError):
        message_sendlaterdm_v1(no_message_been_sent[1], no_message_been_sent[6], 'hello', create_timestamp[1])

def test_message_senddmlater_AccessError_case(no_message_been_sent, create_timestamp):
    # when: the authorised user has not joined the channel they are trying to post to
    with pytest.raises(AccessError):
        message_sendlaterdm_v1(no_message_been_sent[2], no_message_been_sent[6], 'hello', create_timestamp[0])

def test_message_sendlaterdm_success_case(no_message_been_sent, create_timestamp):
    assert len(message_sendlaterdm_v1(no_message_been_sent[1], no_message_been_sent[6], 'hello', create_timestamp[0])) == 1
    clear_v1()