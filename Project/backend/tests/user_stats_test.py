import pytest
from src.error import InputError
from src.error import AccessError
import src.other
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.message import message_send_v2
from src.dm import dm_create_v1
from src.other import clear_v1
from src.user_stats import user_stats_v1, users_stats_v1



@pytest.fixture
def input():
    clear_v1()
    # create a channel owner
    channel_owner = auth_register_v2('vaildmail@gmail.com', '123abc!', 'Obiwan', 'Kenobi')
    channel_owner_token = channel_owner['token']
    # create a channel member
    member = auth_register_v2('member@gmail.com', '321abc!', 'Anakin', 'Skywalker' )
    member_token = member['token']
    member_id = member['auth_user_id']
    # create a not channel member
    not_member = auth_register_v2('owner@gmail.com', '12312afc!', 'Boba', 'Fett')
    not_member_token = not_member['token']
    
    # Create a public channel
    public_channel = channels_create_v2(channel_owner_token, 'public', True)
    public_channel = public_channel['channel_id']
    # Create a dm channel
    dm = dm_create_v1(channel_owner_token,[member_id])
    dm_id = dm['dm_id']

    #                    0                   1              2               4           5
    return_list = [channel_owner_token, member_token, not_member_token, public_channel, dm_id]
    return return_list


@pytest.fixture
def only_user():
    clear_v1()
    # create a channel member
    member = auth_register_v2('member@gmail.com', '321abc!', 'Anakin', 'Skywalker' )
    member_token = member['token']

    return_list = [member_token]
    return return_list


def test_user_stats(input):

    assert user_stats_v1(input[0])["user_stats"]["channels_joined"][-1]["num_channels_joined"] == 1
    assert user_stats_v1(input[0])["user_stats"]["dms_joined"][-1]["num_dms_joined"] == 1
    assert user_stats_v1(input[0])["user_stats"]["messages_sent"][-1]["num_messages_sent"] == 0

def test_user_stats_message(input):
    message_send_v2(input[0], input[4], "hello")
    assert user_stats_v1(input[0])["user_stats"]["messages_sent"][-1]["num_messages_sent"] == 1

def test_user_stats_empty(only_user):
    assert user_stats_v1(only_user[0])["user_stats"]["involvement_rate"] == 0


def test_users_stats(input):
    assert users_stats_v1(input[0])["dreams_stats"]["channels_exist"][-1]["num_channels_exist"] == 1


