
import pytest

from src.channels import channels_create_v2, channels_listall_v2, channels_list_v2
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1
from src.auth import auth_register_v2, auth_token_to_id 
from src.channel import channel_join_v2
from src.dm import dm_list_v1

@pytest.fixture
def set_up_user():
    clear_v1()    
    global_owner_id = auth_register_v2('vaildmail@gmail.com', '123abc!', 'Obiwan', 'Kenobi')
    global_owner_token = global_owner_id['token']
    return global_owner_token

def test_channels_list_empty_data(set_up_user):
    assert channels_list_v2(set_up_user) == {'channels' : []}
    clear_v1()

def test_channels_list_success_case(set_up_user):
    # Create a public channel
    user_id = auth_register_v2('acdmail@gmail.com', '123abc!', 'Obiwan', 'Kenobi')
    user_token = user_id['token']
    channel_id = channels_create_v2(set_up_user, 'Galacitic Republic', True)
    channel_id = channel_id['channel_id']
    channel_id_new = channels_create_v2(user_token, 'Galacitic Republic', True)['channel_id']
    # the code below only mean to pass pylint
    channel_id_new = channel_id_new + channel_id_new
    channel_join_v2(user_token, channel_id)
    assert channels_list_v2(set_up_user) == {'channels' : [{'channel_id' : channel_id, 'name' : 'Galacitic Republic'}]}
    clear_v1()

def test_channels_listall_v2(set_up_user):
    #create two channels to test 
    test_channel_one = channels_create_v2(set_up_user, 'test_channel_one', True)
    test_channel_one = test_channel_one['channel_id']
    test_channel_two = channels_create_v2(set_up_user, 'test_channel_two', False)
    test_channel_two = test_channel_two['channel_id']

    assert channels_listall_v2(set_up_user) ==  {'channels': [{'channel_id': 0, 'name': 'test_channel_one'}, {'channel_id': 1, 'name': 'test_channel_two'}]}
    clear_v1()


def test_channels_create_v2(set_up_user):
    # right examples
    # Create  new  test accounts
    assert channels_create_v2(set_up_user, "channel1", True) == {'channel_id': 0}
    assert channels_create_v2(set_up_user, "channel2", False) == {'channel_id': 1}
    assert channels_create_v2(set_up_user, "channel3", True) == {'channel_id': 2}
    clear_v1()


def test_channels_create_v2_except(set_up_user):
    # channel name is more than 20 characters long - the test should has an input error
    with pytest.raises(InputError):
        assert channels_create_v2(set_up_user, "channelisreallytoolong", True) 
    clear_v1()

