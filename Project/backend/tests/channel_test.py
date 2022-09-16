
import pytest
from src.auth import auth_register_v2
from src.channel import channel_details_v2, channel_invite_v2, channel_addowner_v1, channel_removeowner_v1,channel_join_v2, channel_leave_v1
from src.channels import channels_create_v2
from src.other import clear_v1
from src.error import InputError
from src.error import AccessError


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
@pytest.fixture
def channel_set():
    clear_v1()
    # creat a global owner
    global_owner_user_id = auth_register_v2("123@mail.com", "passdrow", "Tony", "Stark")
    global_owner_user_token = global_owner_user_id['token']
    global_owner_uid = global_owner_user_id['auth_user_id']
    # create a user to be a channel owner
    channel_owner = auth_register_v2('member@gmai.com', '321abc!', 'Anakin', 'Skywalker' )
    channel_owner_token = channel_owner['token'] 
    channel_owner_uid = channel_owner['auth_user_id']
    # create a user to join the channel
    participant_user_id = auth_register_v2("456@mail.com", "drowssap", "Steve", "Rogers")
    participant_token = participant_user_id['token']
    participant_id = participant_user_id['auth_user_id']
    # create a public channel
    new_channel_public = channels_create_v2(channel_owner_token, 'public', True)
    new_channel_public = new_channel_public['channel_id']
    channel_join_v2(participant_token, new_channel_public)
    channel_join_v2(global_owner_user_token, new_channel_public)
    not_member = auth_register_v2("iamnotamember@mail.com", "passdrow", "Dead", "pool")
    not_member_token = not_member['token']
    #                       0                    1                  2                   3                   4                  5                6               7
    ret_list = [global_owner_user_token, channel_owner_token, participant_token, new_channel_public, global_owner_uid, channel_owner_uid, participant_id, not_member_token]
    return ret_list

#tests function channel_invite_v2
def test_channel_invite_inputError(set_up):
    #testing invalid channel id (InputError)
    invalid_channel_id = set_up[4] - 1
    with pytest.raises(InputError):
        channel_invite_v2(set_up[0], invalid_channel_id, set_up[2])
    clear_v1()

def test_channel_invite_invalid_user():
    clear_v1()
    owner_user_id = auth_register_v2("123@mail.com", "passdrow", "Tony", "Stark")
    owner_user_token = owner_user_id['token']
    invalid_id = owner_user_id['auth_user_id']  - 1
    new_channel_public = channels_create_v2(owner_user_token, 'public', True)
    new_channel_public = new_channel_public['channel_id']
    #testing invalid user id (InputError)
    with pytest.raises(InputError):
        channel_invite_v2(owner_user_token, new_channel_public, invalid_id)
    clear_v1()
def test_channel_invite_AccessError(set_up):   
    #testing when auth user is not part of the channel (AccessError)
    with pytest.raises(AccessError):
        channel_invite_v2(set_up[3], set_up[4], set_up[2])
    clear_v1()
        
def test_channel_invite_success_case_memeber(set_up):
    #test that the invite function has added the member to the channel
    channel_invite_v2(set_up[0], set_up[4], set_up[2])
    assert channel_details_v2(set_up[0], set_up[4]) == {
        'name': 'public',
        'owner_members': [
                {
                    'email': '123@mail.com',
                    'u_id': set_up[5],
                    'name_first': "Tony",
                    'name_last':"Stark",
                    'handle': "tonystark",
                }
        ],
        'all_members': [
                {
                    'email': '123@mail.com',
                    'u_id': set_up[5],
                    'name_first': "Tony",
                    'name_last': "Stark",
                    'handle': "tonystark",
                }, {
                    'email': '456@mail.com',
                    'u_id': set_up[2],
                    'name_first': "Steve",
                    'name_last': "Rogers",
                    'handle': "steverogers",
                },
        ]
    }
    clear_v1()
def test_channel_invite_global_user(set_up):
    channel_invite_v2(set_up[7], set_up[6], set_up[5])
    assert len(channel_details_v2(set_up[7], set_up[6])['owner_members']) == 1
    clear_v1()


def test_channel_invite_user_in_channel(set_up):
    channel_invite_v2(set_up[0], set_up[4], set_up[5])
    assert len(channel_details_v2(set_up[0], set_up[4])['all_members']) == 1
    clear_v1()


def test_channel_details(set_up):   
    #adds users to channel
    channel_invite_v2(set_up[0], set_up[4], set_up[2])     
    #testing user not being a member of the channel (AccessError)
    with pytest.raises(AccessError):
        channel_details_v2(set_up[3], set_up[4])  
    #testing auth user that is a member getting channel details
    assert channel_details_v2(set_up[0], set_up[4]) == {
            'name': "public",
            'owner_members': [
                {
                    'email': '123@mail.com',
                    'u_id': set_up[5],
                    'name_first': "Tony",
                    'name_last':"Stark",
                    'handle': "tonystark",
                }
            ],
            'all_members': [
                {
                    'email': '123@mail.com',
                    'u_id': set_up[5],
                    'name_first': "Tony",
                    'name_last': "Stark",
                    'handle': "tonystark",
                }, {
                    'email': '456@mail.com',
                    'u_id': set_up[2],
                    'name_first': "Steve",
                    'name_last': "Rogers",
                    'handle': "steverogers",
                },
            ]
        }
    clear_v1()

def test_details_channel_id_invalid():
    #testing invalid channel id (InputError)
    clear_v1()
    owner_user_id = auth_register_v2("123@mail.com", "passdrow", "Tony", "Stark")
    owner_user_token = owner_user_id['token']
    invalid_id = owner_user_id['auth_user_id']  - 1
    new_channel_public = channels_create_v2(owner_user_token, 'public', True)
    new_channel_public = new_channel_public['channel_id']
    with pytest.raises(InputError):
        channel_details_v2(owner_user_token, invalid_id)
    clear_v1()
        

def test_addowner(set_up):
    assert len(channel_details_v2(set_up[0], set_up[4])['owner_members']) == 1
    channel_addowner_v1(set_up[0], set_up[4], set_up[2])
    assert len(channel_details_v2(set_up[0], set_up[4])['owner_members']) == 2
    clear_v1()

def test_removeowner(set_up):
    channel_addowner_v1(set_up[0], set_up[4], set_up[2])
    assert len(channel_details_v2(set_up[0], set_up[4])['owner_members']) == 2
    channel_removeowner_v1(set_up[0], set_up[4], set_up[2])
    assert len(channel_details_v2(set_up[0], set_up[4])['owner_members']) == 1
    clear_v1()

def test_addowner_Input_error1(channel_set):
    # Channel ID is not a valid channel
    # channel id is unique for every channel
    invalid_channel_id = channel_set[3] + 1
    with pytest.raises(InputError):
        channel_addowner_v1(channel_set[1], invalid_channel_id, channel_set[6])
    clear_v1()

def test_addowner_Input_error_is_owner(channel_set):
    # When user with user id u_id is already an owner of the channel
    with pytest.raises(InputError):
        channel_addowner_v1(channel_set[1], channel_set[3], channel_set[5])
    clear_v1()

def test_addowner_AccessError_is_memebr(channel_set):
    with pytest.raises(AccessError):
        channel_addowner_v1(channel_set[2], channel_set[3], channel_set[4])
    clear_v1()

def test_addowner_success(channel_set):
    channel_addowner_v1(channel_set[0], channel_set[3], channel_set[6])
    assert len(channel_details_v2(channel_set[0], channel_set[3])['owner_members']) == 2
    clear_v1()

def test_removeowner_InputError_case3(channel_set):
    # The user is currently the only owner
    with pytest.raises(InputError):
        channel_removeowner_v1(channel_set[0], channel_set[3], channel_set[5])
    clear_v1()

def test_removeowner_InputError_case1(channel_set):
    channel_addowner_v1(channel_set[0], channel_set[3], channel_set[6])
    # Channel ID is not a valid channel
    # Channel ID for each channel is unique
    invalid_channel_id = channel_set[3] - 1
    with pytest.raises(InputError):
        channel_removeowner_v1(channel_set[0], invalid_channel_id, channel_set[6])
    clear_v1()

def test_removeowner_InputError_case2(channel_set):
    #When user with user id u_id is not an owner of the channel
    with pytest.raises(InputError):
        channel_removeowner_v1(channel_set[0], channel_set[3], channel_set[6])
    clear_v1()

def test_removeowner_AccessError(channel_set):
    # when the authorised user is not an owner of the **Dreams**, or an owner of this channel
    with pytest.raises(AccessError):
        channel_removeowner_v1(channel_set[2], channel_set[3], channel_set[1])
    clear_v1()

def test_removeowner_success_case(channel_set):
    channel_addowner_v1(channel_set[1], channel_set[3], channel_set[6])
    channel_removeowner_v1(channel_set[1], channel_set[3], channel_set[6])
    assert len(channel_details_v2(channel_set[0], channel_set[3])['owner_members']) == 1
    clear_v1()

def test_leave_InputError(channel_set):
    # Channel ID is not a valid channel
    # Channel ID for each channel is unique
    invalid_channel_id = channel_set[3] - 1
    with pytest.raises(InputError):
        channel_leave_v1(channel_set[1], invalid_channel_id)
    clear_v1()

def test_leave_AccessError(channel_set):
    #Authorised user is not a member of channel with channel_id
    with pytest.raises(AccessError):
        channel_leave_v1(channel_set[7], channel_set[3])
    clear_v1()

def test_leave_success_case(channel_set):
    channel_leave_v1(channel_set[2], channel_set[3])
    assert len(channel_details_v2(channel_set[0], channel_set[3])['all_members']) == 2
    clear_v1()