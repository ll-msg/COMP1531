import pytest
from src.error import InputError
from src.error import AccessError
import src.other
from src.auth import auth_register_v2
from src.message import message_send_v2, message_remove_v1, message_edit_v2, message_share_v1, message_senddm_v1
from src.channel import channel_messages_v2, channel_join_v2
from src.channels import channels_create_v2
from src.dm import dm_create_v1, dm_messages_v1
from src.other import clear_v1
@pytest.fixture
def input():
    clear_v1()
    # Create  new  test accounts
    # Global onwer who is the first user in Dream
    global_owner = auth_register_v2('vaildmail@gmail.com', '123abc!', 'Obiwan', 'Kenobi')
    global_owner_token = global_owner['token']
    # User own the channel/dm
    channel_onwer = auth_register_v2('owner@gmail.com', '12312afc!', 'Boba', 'Fett')
    channel_owner_token = channel_onwer['token']
    # User who didnt join the channel/dm
    memeber = auth_register_v2('member@gmail.com', '321abc!', 'Anakin', 'Skywalker' )
    memeber_token = memeber['token']
    # User who joined the channel/dm but didnt send any messages
    member_join_channel =  auth_register_v2('joinchannel@gmail.com', 'abc123!', 'Count', 'Dooku')
    member_join_channel_token = member_join_channel['token']
    member_join_channel_uid = member_join_channel['auth_user_id']
    # Use who joined the channel/dm and sent a message
    memebr_inchannel_sendmessage = auth_register_v2('sendmessage@gmail.com', 'wksj123!', 'Princess', 'Leia')
    memebr_inchannel_sendmessage_token = memebr_inchannel_sendmessage['token']
    member_send_uid = memebr_inchannel_sendmessage['auth_user_id']
    # Create a public channel
    public_channel = channels_create_v2(channel_owner_token, 'public', True)
    public_channel = public_channel['channel_id']
    # Let member_join_channel join in the channel
    channel_join_v2(member_join_channel_token, public_channel)
    channel_join_v2(memebr_inchannel_sendmessage_token, public_channel)
    # Messmage is more than 1000 characters
    MESSAGE_TEST_OVER = 't' * 1001
    # Message send in channel
    TEST_MESSAGE_ID = message_send_v2(memebr_inchannel_sendmessage_token, public_channel, '@countdooku Hellooooooooooooooooooooooooooooooooo')
    TEST_MESSAGE_ID = TEST_MESSAGE_ID['message_id']
    # create a dm, creator is channel_owner and members are member_join_channel and memebr_inchannel_sendmessage
    dm = dm_create_v1(channel_owner_token,[member_join_channel_uid, member_send_uid])
    dm_id = dm['dm_id']
    # Message send in dm
    TEST_DM_MESSAGE_ID = message_senddm_v1(memebr_inchannel_sendmessage_token, dm_id, '@bobafett Helloooooooooooooooooooooooooooooooooooooo')
    TEST_DM_MESSAGE_ID = TEST_DM_MESSAGE_ID['message_id']
    #              global onwer |  user not in channel|public channel|invalid message  |  sent message id|  user joined channel/dm no message|user joined channel/dm sent message|user own the channel/dm|dm id(8)|dm_message_id
    #index mark            0                 1             2               3                   4                         5                            6                               7          8                 9
    input_list = [global_owner_token, memeber_token, public_channel, MESSAGE_TEST_OVER, TEST_MESSAGE_ID, member_join_channel_token, memebr_inchannel_sendmessage_token, channel_owner_token, dm_id, TEST_DM_MESSAGE_ID]
    return input_list

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

def test_message_send_emptymessage(no_message_been_sent):
    # send an empty str
    assert (message_send_v2(no_message_been_sent[4], no_message_been_sent[5], '')) == {}
    clear_v1()
    
def test_message_send_InputError(input):
    # Length of message is over 1000 characters
    with pytest.raises(InputError):
        message_send_v2(input[6], input[2], input[3])
        clear_v1()

def test_message_send_AccessError(input):
    # Authorised user has not joined the channel
    with pytest.raises(AccessError):
        message_send_v2(input[1], input[2], 'Hello')
        clear_v1()

def test_message_send_success_case1(input):
    # already sent 2 message, 1 sent to channel and 1 sent to dm
    assert(channel_messages_v2(input[5], input[2], 0)['messages'][0]['message']) == '@countdooku Hellooooooooooooooooooooooooooooooooo'
    clear_v1()
def test_message_send_success_case2(no_message_been_sent):
    # no message has been sent yet
    # send a message with tag and the hanndle is not in current channel
    message_send_v2(no_message_been_sent[4], no_message_been_sent[5], '@anakinskywalker hellothere')
    assert(channel_messages_v2(no_message_been_sent[3], no_message_been_sent[5], 0)['messages'][0]['message'] == '@anakinskywalker hellothere')
    clear_v1()


def test_message_remove_InputError(input):
    # remove one message first
    message_remove_v1(input[6], input[4])
    with pytest.raises(InputError):
        #remove the same message twice
        message_remove_v1(input[6], input[4])
    clear_v1()

def test_message_remove_AccessError(input):
    # Message is not sent by the user and the user is not a owner of channel and not a gloabl owner
    with pytest.raises(AccessError):
        message_remove_v1(input[5], input[4])
    clear_v1()
    
def test_message_remove_AccessError_dm(input):
    with pytest.raises(AccessError):
        message_remove_v1(input[5], input[9])
    clear_v1()

def test_message_remove_success_case1_channel(input):
    # Message is removed by the user who sent the message to channel
    message_remove_v1(input[6], input[4])
    assert(channel_messages_v2(input[6], input[2], 0)) == {'messages': [], 'start': 0, 'end': -1,}
    clear_v1()

def test_message_remove_success_case2_channel(input):
    # Message is removed by the user who is the owner of the channel
    message_remove_v1(input[7], input[4])
    assert(channel_messages_v2(input[7], input[2], 0)) == {'messages': [], 'start': 0, 'end': -1,}
    clear_v1()

def test_message_remove_success_case3_channel(input):
    # Message is removed by the global onwer in channel
    message_remove_v1(input[0], input[4])
    assert(channel_messages_v2(input[7], input[2], 0)) == {'messages': [], 'start': 0, 'end': -1}
    clear_v1()

def test_message_remove_success_case1_dm(input):
    # Message is removed by the user who sent the message to dm
    message_remove_v1(input[6], input[9])
    assert(dm_messages_v1(input[6], input[8], 0)) == {'messages': [], 'start': 0, 'end': -1}
    clear_v1()

def test_message_remove_success_case2_dm(input):
    # Message is removed by the user who is the owner of the dm
    message_remove_v1(input[7], input[9])
    assert(dm_messages_v1(input[7], input[8], 0)) == {'messages': [], 'start': 0, 'end': -1}
    clear_v1()

def test_message_remove_success_case3_dm(input):
    # Message is removed by the global onwer in dm
    message_remove_v1(input[0], input[9])
    assert(dm_messages_v1(input[7], input[8], 0)) == {'messages': [], 'start': 0, 'end': -1}
    clear_v1()

def test_message_edit_InputError(input):
    # Length of message is over 1000 characters
    with pytest.raises(InputError):
        message_edit_v2(input[6], input[4], input[3])
    clear_v1()

def test_message_edit_InputError_delete(input):
    # Delete the message
    message_edit_v2(input[6], input[4], '')
    # message_id refers to a deleted message
    with pytest.raises(InputError):
        message_edit_v2(input[6], input[4], 'test')
    clear_v1()

def test_message_edit_AccessError(input):
    # Message is not sent by the user and the user is not a owner of channel and not a global owner
    with pytest.raises(AccessError):
        message_edit_v2(input[5], input[4], 'test')
    clear_v1()

def test_message_edit_AccessError_dm(input):
    # Message is not sent by the user and the user is not a owner of channel and not a global owner
    with pytest.raises(AccessError):
        message_edit_v2(input[5], input[9], 'test')
    clear_v1()

def test_message_edit_success_channel_case1(input):
    # Message is edited by the user who sent the message to channel
    message_edit_v2(input[6], input[4], 'a')
    assert(channel_messages_v2(input[6], input[2], 0))['messages'][0]['message'] == 'a'
    clear_v1()

def test_message_edit_success_channel_case2(input):
    # Message is edited by the user who is the owner of the channel
    message_edit_v2(input[7], input[4], '')
    assert(channel_messages_v2(input[6], input[2], 0)) == {'messages': [], 'start': 0, 'end': -1,}
    clear_v1()

def test_message_edit_success_channel_case3(input):
    # Message is edited by the global onwer in channel
    message_edit_v2(input[0], input[4], '')
    assert(channel_messages_v2(input[6], input[2], 0)) == {'messages': [], 'start': 0, 'end': -1,}
    clear_v1()

def test_message_edit_success_dm_case1(input):
    # Message is edited by the user who sent the message to dm
    message_edit_v2(input[6], input[9], 'a')
    assert(dm_messages_v1(input[6], input[8], 0))['messages'][0]['message'] == 'a'
    clear_v1()

def test_message_edit_success_dm_case2(input):
    # Message is edited by the user who is the owner of the dm
    message_edit_v2(input[7], input[9], '')
    assert(dm_messages_v1(input[6], input[8], 0)) == {'messages': [], 'start': 0, 'end': -1}
    clear_v1()

def test_message_edit_success_dm_case3(input):
    # Message is edited by the global onwer in dm
    message_edit_v2(input[0], input[9], '')
    assert(dm_messages_v1(input[6], input[8], 0)) == {'messages': [], 'start': 0, 'end': -1}
    clear_v1()

def test_message_share_AccessError(input):
    # the authorised user has not joined the channel or DM they are trying to share the message to
    # test user not in channel
    with pytest.raises(AccessError):
        message_share_v1(input[1], input[4], '', input[2], -1)
    # test user not in dm
    with pytest.raises(AccessError):
        message_share_v1(input[1], input[4], '', -1, input[8])
    clear_v1()

def test_message_share_seccess_channel(no_message_been_sent):
    # test message share to channel
    # white box
    # og message in dm and send to channel
    og_message_id = message_senddm_v1(no_message_been_sent[4], no_message_been_sent[6],'@bobafett')['message_id']
    message_share_v1(no_message_been_sent[4], og_message_id, 'comment', no_message_been_sent[5], -1)
    assert(channel_messages_v2(no_message_been_sent[3], no_message_been_sent[5], 0)['messages'][0]['message']) == 'comment--@bobafett' 
    clear_v1()
    
def test_message_share_seccess_dm(no_message_been_sent):   
    # test message share to dm
    # white box
    # og message in channel and send to dm
    og_message_id = message_send_v2(no_message_been_sent[4], no_message_been_sent[5], '@bobafett')['message_id']
    message_share_v1(no_message_been_sent[4], og_message_id, 'comment', -1, no_message_been_sent[6])
    assert(dm_messages_v1(no_message_been_sent[4], no_message_been_sent[6],0)['messages'][0]['message']) == 'comment--@bobafett' 
    clear_v1()

def test_message_share_seccess(no_message_been_sent):
    og_message_id_1 = message_senddm_v1(no_message_been_sent[4], no_message_been_sent[6],'test')['message_id']
    og_message_id_2 = message_send_v2(no_message_been_sent[4], no_message_been_sent[5], 'test')['message_id']
    message_share_v1(no_message_been_sent[4], og_message_id_1, 'comment', no_message_been_sent[5], -1)
    message_share_v1(no_message_been_sent[4], og_message_id_2, 'comment', -1, no_message_been_sent[6])
    assert(len(dm_messages_v1(no_message_been_sent[4], no_message_been_sent[6],0)['messages'])) == 2
    clear_v1()

def test_message_senddm_InputError(input):
    # Message is more than 1000 characters
    with pytest.raises(InputError):
        message_senddm_v1(input[5], input[8], input[3])
    clear_v1()

def test_message_semddm_AccessError(input):
    # the authorised user is not a member of the DM they are trying to post to
    with pytest.raises(AccessError):
        message_senddm_v1(input[1], input[8], 'hello')
    clear_v1()

def test_message_senddm_success_case1(input):
    # already sent 2 message, 1 sent to channel and 1 sent to dm
    assert(dm_messages_v1(input[5], input[8], 0)['messages'][0]['message']) == '@bobafett Helloooooooooooooooooooooooooooooooooooooo'
    clear_v1()

def test_message_senddm_success_case2(no_message_been_sent):
    # no message has been sent yet, and handle not in dm    
    # send a message with tag and the hanndle is not in current dm
    message_senddm_v1(no_message_been_sent[4], no_message_been_sent[6], '@anakinskywalker hellothere')
    assert(dm_messages_v1(no_message_been_sent[3], no_message_been_sent[6], 0)['messages'][0]['message']) == '@anakinskywalker hellothere'
    clear_v1()
def test_message_senddm_empty_case(no_message_been_sent):
    # send an empty str
    assert (message_senddm_v1(no_message_been_sent[4], no_message_been_sent[6], '')) == {}
    clear_v1()
 
def test_message_senddm_coverage(no_message_been_sent):
    message_senddm_v1(no_message_been_sent[4], no_message_been_sent[6],'@countdooku hi')
    assert(len(dm_messages_v1(no_message_been_sent[4], no_message_been_sent[6],0)['messages'])) == 1

def test_message_send_coverage(no_message_been_sent):
    message_send_v2(no_message_been_sent[4], no_message_been_sent[5], '@bobafett hello')
    assert len(channel_messages_v2(no_message_been_sent[4],  no_message_been_sent[5], 0)['messages']) == 1