import pytest
from src.auth import auth_register_v2
from src.standup import standup_start_v1, standup_active_v1, standup_send_v1
from src.channels import channels_create_v2
from src.other import clear_v1
from datetime import timezone, datetime, timedelta
from src.error import InputError
from src.error import AccessError
import time
from src.channel import channel_messages_v2


@pytest.fixture
def set_up():
    clear_v1()
    #create new members
    owner_user_id = auth_register_v2("123@mail.com", "passdrow", "Tony", "Stark")
    owner_user_token = owner_user_id['token']
    owner_user_id = owner_user_id['auth_user_id']
    participant_user_id = auth_register_v2("456@mail.com", "drowssap", "Steve", "Rogers")
    participant_token = participant_user_id['token']
    participant_user_id = participant_user_id['auth_user_id']
    non_participant_user_id = auth_register_v2("789@mail.com", "ssapword", "Natasha", "Romanov")
    non_participant_user_token = non_participant_user_id['token']
    new_channel_public = channels_create_v2(owner_user_token, 'public', True)
    new_channel_public = new_channel_public['channel_id']
    another_owner = auth_register_v2('member@gmai.com', '321abc!', 'Anakin', 'Skywalker' )
    another_owner_token = another_owner['token']
    another_channel = channels_create_v2(another_owner_token, 'StarWars', True)
    another_channel = another_channel['channel_id']
    #                     0                  1                  2                        3                        4                 5              6                7
    return_list = [owner_user_token, participant_token, participant_user_id, non_participant_user_token, new_channel_public, owner_user_id, another_channel, another_owner_token]
    return return_list


''' standup start function '''
def test_standup_start_input_1(set_up): 
    # test invalid channel_id
    invalid_channel_id = set_up[4] - 1
    with pytest.raises(InputError):
        standup_start_v1(set_up[0], invalid_channel_id, 1)
    clear_v1()

def test_standup_start_input_2(set_up):
    # an active standup is currently running in the channel
    with pytest.raises(InputError):
        standup_start_v1(set_up[0], set_up[4], 2)
        standup_start_v1(set_up[0], set_up[4], 1)
    clear_v1()

def test_standup_start_access(set_up):
    # test the user is not a member of the channel
    with pytest.raises(AccessError):
        standup_start_v1(set_up[3], set_up[4], 1)
    clear_v1()

def test_standup_start_success(set_up):
    create_time = datetime.utcnow() + timedelta(seconds=1)
    time_finish = int(create_time.replace(tzinfo=timezone.utc).timestamp())
    assert standup_start_v1(set_up[0], set_up[4], 1) == {"time_finish": time_finish}
    clear_v1()


''' standup active function '''
def test_standup_active_input(set_up):
    standup_start_v1(set_up[0], set_up[4], 1)
    # test invalid channel_id
    invalid_channel_id = set_up[4] - 1
    with pytest.raises(InputError):
        standup_active_v1(set_up[0], invalid_channel_id)
    clear_v1()

def test_standup_active_none(set_up):
    assert standup_active_v1(set_up[0], set_up[4])['time_finish'] == None
    clear_v1()

def test_standup_active_success(set_up):
    time_finish = standup_start_v1(set_up[0], set_up[4], 1)
    assert standup_active_v1(set_up[0], set_up[4]) == {"is_active": True, "time_finish": time_finish['time_finish']}
    clear_v1()


''' standup send function '''
def test_standup_send_input_1(set_up):
    standup_start_v1(set_up[0], set_up[4], 1)
    # invalid channel id
    invalid_channel_id = set_up[4] - 1
    with pytest.raises(InputError):
        standup_send_v1(set_up[0], invalid_channel_id, "hello")
    clear_v1()

def test_standup_send_input_2(set_up):
    standup_start_v1(set_up[0], set_up[4], 1)
    # message is more than 1000 characters long
    with pytest.raises(InputError):
        standup_send_v1(set_up[0], set_up[4], "hello" * 2000)
    clear_v1()

def test_standup_send_input_3(set_up):
    # there is no active standup in the channel
    with pytest.raises(InputError):
        standup_send_v1(set_up[0], set_up[4], "hello")
    clear_v1()

def test_standup_send_access(set_up):
    standup_start_v1(set_up[0], set_up[4], 1)
    # user is not a member of the channel
    with pytest.raises(AccessError):
        standup_send_v1(set_up[3], set_up[4], "hello")
    clear_v1()

def test_standup_send_empty(set_up):
    standup_start_v1(set_up[0], set_up[4], 1)
    standup_send_v1(set_up[0], set_up[4], "")
    time.sleep(3)
    assert len(channel_messages_v2(set_up[0], set_up[4], 0)['messages']) == 0
    clear_v1()

def test_standup_send_success(set_up):
    standup_start_v1(set_up[0], set_up[4], 1)
    standup_send_v1(set_up[0], set_up[4], "hello")
    time.sleep(3)
    assert len(channel_messages_v2(set_up[0], set_up[4], 0)['messages']) == 1
    clear_v1()


    
