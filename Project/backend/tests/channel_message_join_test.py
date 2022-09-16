
import pytest
from src.auth import auth_register_v2
from src.channel import channel_join_v2, channel_messages_v2, channel_details_v2
from src.channels import channels_create_v2
from src.other import clear_v1
from src.error import InputError
from src.error import AccessError
from src.message import message_send_v2


@pytest.fixture
def input():
    clear_v1()
    # Create  new  test accounts
    global_owner_id = auth_register_v2('vaildmail@gmail.com', '123abc!', 'Obiwan', 'Kenobi')
    global_owner_token = global_owner_id['token']
    global_owner_uid = global_owner_id['auth_user_id']
    owner_id = auth_register_v2('vaildmail2@gmail.com','1122abc!','master', 'Yoda')
    owner_token = owner_id['token']
    owner_uid = owner_id['auth_user_id']
    memeber_id = auth_register_v2('member@gmai.com', '321abc!', 'Anakin', 'Skywalker' )
    memeber_token = memeber_id['token']
    memebr_uid = memeber_id['auth_user_id']
    #Create a private channel
    private_channel = channels_create_v2(owner_token, 'private', False)
    private_channel = private_channel['channel_id']
    #Create a public channel
    public_channel = channels_create_v2(owner_token, 'public', True)
    public_channel = public_channel['channel_id']
    #                   0                   1           2               3               4              5                  6           7
    input_list = [global_owner_token, owner_token, memeber_token, private_channel, public_channel, global_owner_uid, owner_uid, memebr_uid]
    return input_list

def test_message_sent_50(input):
    index = 0
    while index != 51:
        message_send_v2(input[1], input[4], 'test')
        index = index + 1
    assert channel_messages_v2(input[1], input[4], 0)['end'] == 50
    clear_v1()

def test_input_channel_messages_v2(input):
    #start is greater than the total number of messages in the channel
    with pytest.raises(InputError):
        channel_messages_v2(input[1], input[4],1)
    clear_v1()

#Test whether the channel id is valid in channel_messages function(InputError)
def test_channel_valid_messages_v1():
    clear_v1()
    owner_id = auth_register_v2('vaildmail2@gmail.com','1122abc!','master', 'Yoda')
    owner_token = owner_id['token']
    #Create only one channel with unique channel id
    public_channel = channels_create_v2(owner_token, 'public', True)
    public_channel = public_channel['channel_id']
    #test_channel_id is invalid
    test_channel_id = public_channel - 1
    # channel id is not a vaild channel 
    with pytest.raises(InputError):
        channel_messages_v2(owner_token, test_channel_id, 0)
    clear_v1()

def test_access_channel_messages_v2(input):
    #Authorised user is not a member of channel with channel_id
    with pytest.raises(AccessError):
        channel_messages_v2(input[2], input[4], 0)
    clear_v1()

def test_channel_message_successcase1(input):
    #test channel_message with no message in that channel
    assert(channel_messages_v2(input[1], input[4], 0)) == {'messages': [], 'start': 0, 'end': -1}
    clear_v1()


def test_input_channel_join_v2(input):
    channel_join_v2(input[2], input[4])
    assert channel_details_v2(input[1], input[4]) == {
        'name' : 'public',
        'owner_members': [
            {
                'u_id': input[6],
                'name_first': 'master',
                'name_last': 'Yoda',
                'handle' : 'masteryoda',
                'email' : 'vaildmail2@gmail.com',
            }
        ],
        'all_members': [
            {
                'u_id': input[6],
                'name_first': 'master',
                'name_last': 'Yoda',
                'handle' : 'masteryoda',
                'email' : 'vaildmail2@gmail.com',
            }, {
                'u_id': input[7],
                'name_first': 'Anakin',
                'name_last': 'Skywalker',
                'handle' : 'anakinskywalker',
                'email': 'member@gmai.com',

            }
        ],
            
    }
    clear_v1()

#Test whether channel id is valid in channel_join function
def test_channel_valid_join_v1():
    clear_v1()
    owner_id = auth_register_v2('vaildmail2@gmail.com','1122abc!','master', 'Yoda')
    owner_token = owner_id['token']
    memeber_id = auth_register_v2('member@gmai.com', '321abc!', 'Anakin', 'Skywalker' )
    memeber_token = memeber_id['token']
    #Create only one channel with unique channel id
    public_channel = channels_create_v2(owner_token, 'public', True)
    public_channel = public_channel['channel_id']
    #test_channel_id is invalid
    test_channel_id = public_channel - 1
    # channel id is not valid
    with pytest.raises(InputError):
        channel_join_v2(memeber_token, test_channel_id)
    clear_v1()
    


def test_access_channel_join_v2(input):
    #Test non-global owner user to join a private channels 
    with pytest.raises(AccessError):
        channel_join_v2(input[2], input[3])
    
    #Test global owner join a private channels
    channel_join_v2(input[0], input[3])
    assert channel_details_v2(input[1], input[3]) == {
        'name': 'private',
        'owner_members': [
            {
                'u_id': input[6],
                'name_first': 'master',
                'name_last': 'Yoda',
                'handle' : 'masteryoda',
                'email': 'vaildmail2@gmail.com',
            }
        ],
        'all_members': [
            {
                'u_id': input[6],
                'name_first': 'master',
                'name_last': 'Yoda',
                'handle' : 'masteryoda',
                'email': 'vaildmail2@gmail.com',
            }, {
                'u_id': input[5],
                'name_first': 'Obiwan',
                'name_last': 'Kenobi',
                'handle' : 'obiwankenobi',
                'email' : 'vaildmail@gmail.com',
            }

            
        ],
    }
    clear_v1()

 
 
#Test if the user is already a memeber of that channel, channel_join will do nothing
def test_channel_join_duplication(input):
    channel_join_v2(input[1], input[4])
    assert(channel_details_v2(input[1], input[4])) == {
        'name' : 'public',
        'owner_members': [
            {
                'u_id': input[6],
                'name_first': 'master',
                'name_last': 'Yoda',
                'handle' : 'masteryoda',
                'email' : 'vaildmail2@gmail.com',
            }
        ],
        'all_members': [
            {
                'u_id': input[6],
                'name_first': 'master',
                'name_last': 'Yoda',
                'handle' : 'masteryoda',
                'email' : 'vaildmail2@gmail.com',
            }
        ],
            
    }
    clear_v1()
