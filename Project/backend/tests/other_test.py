import pytest
import src.auth
import src.other
import src.message
import src.channel
import src.dm

from src.error import InputError
from src.error import AccessError


@pytest.fixture
def reg_users_data():
    #register three users
    reg_result = [0,0,0]

    reg_result[0] = src.auth.auth_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    reg_result[1] = src.auth.auth_register_v2('yetanother.validemail123@gmail.com', '123abc!@#++', 'Dylan', 'Meringue')
    reg_result[2] = src.auth.auth_register_v2('notthisagain.validemail456@gmail.com', '123abc!@#--', 'Manuel', 'Internetiquette')

    return reg_result


@pytest.fixture
def clear():
    src.other.clear_v1()


def test_users_all_v1(clear, reg_users_data):
    assert(
        src.other.users_all_v1(reg_users_data[0]['token'])['users'] == [
            {
                "u_id" : 0,
                "email" : 'validemail@gmail.com',
                "name_first" : 'Hayden',
                "name_last" : 'Everest',
                "handle_str" : 'haydeneverest',
                'profile_img_url' : '',
            },
            {
                "u_id" : 1,
                "email" : 'yetanother.validemail123@gmail.com',
                "name_first" : 'Dylan',
                "name_last" : 'Meringue',
                "handle_str" : 'dylanmeringue',
                'profile_img_url' : '',
            },
            {
                "u_id" : 2,
                "email" : 'notthisagain.validemail456@gmail.com',
                "name_first" : 'Manuel',
                "name_last" : 'Internetiquette',
                "handle_str" : 'manuelinternetiquett',
                'profile_img_url' : '',
            }
        ]
    )


def test_search_v2(clear, reg_users_data):
    reg_users_data[0]['token']

    channel_id = src.channels.channels_create_v2(reg_users_data[1]['token'], "random channel", True)['channel_id']
    src.channel.channel_join_v2(reg_users_data[1]['token'], channel_id)

    src.message.message_send_v2(reg_users_data[1]['token'], channel_id, "I'm testing this function")
    src.message.message_send_v2(reg_users_data[1]['token'], channel_id, "another message")
    src.message.message_send_v2(reg_users_data[1]['token'], channel_id, "hello there :)")
    src.message.message_send_v2(reg_users_data[1]['token'], channel_id, "this is the last message, testing again")

    assert(len(src.other.search_v2(reg_users_data[1]['token'], "hello")['messages']) == 1)
    assert(src.other.search_v2(reg_users_data[1]['token'], "hello")['messages'][0]['message'] == "hello there :)")

    assert(len(src.other.search_v2(reg_users_data[1]['token'], "tes")['messages']) == 2)
    assert(src.other.search_v2(reg_users_data[1]['token'], "tes")['messages'][0]['message'] in ["I'm testing this function", "this is the last message, testing again"])
    assert(src.other.search_v2(reg_users_data[1]['token'], "tes")['messages'][1]['message'] in ["I'm testing this function", "this is the last message, testing again"])

    assert(len(src.other.search_v2(reg_users_data[1]['token'], "asdasdasdasd")['messages']) == 0)

    channel_id = src.channels.channels_create_v2(reg_users_data[0]['token'], "random channel 2", True)['channel_id']
    # src.channel.channel_join_v2(reg_users_data[0]['token'], channel_id)
    src.message.message_send_v2(reg_users_data[0]['token'], channel_id, "qwerty")
    assert(len(src.other.search_v2(reg_users_data[1]['token'], "qwert")['messages']) == 0)
    
    dm_id = src.dm.dm_create_v1(reg_users_data[0]['token'], [1])['dm_id']
    src.dm.dm_invite_v1(reg_users_data[0]['token'], dm_id, reg_users_data[1]['auth_user_id'])
    
    src.message.message_senddm_v1(reg_users_data[1]['token'], dm_id, "I'm testing this function")
    src.message.message_senddm_v1(reg_users_data[1]['token'], dm_id, "another message")
    src.message.message_senddm_v1(reg_users_data[1]['token'], dm_id, "hello there :) dm here")
    src.message.message_senddm_v1(reg_users_data[1]['token'], dm_id, "this is the last message, testing again")

    assert(len(src.other.search_v2(reg_users_data[1]['token'], "hello")['messages']) == 2)
    assert(src.other.search_v2(reg_users_data[1]['token'], "hello")['messages'][0]['message'] in ["hello there :)", "hello there :) dm here"])
    


def test_search_v2_long(clear, reg_users_data):
    reg_users_data[0]['token']

    channel_id = src.channels.channels_create_v2(reg_users_data[1]['token'], "random channel", True)['channel_id']
    src.channel.channel_join_v2(reg_users_data[1]['token'], channel_id)

    src.message.message_send_v2(reg_users_data[1]['token'], channel_id, "I'm testing this function")
    src.message.message_send_v2(reg_users_data[1]['token'], channel_id, "another message")
    src.message.message_send_v2(reg_users_data[1]['token'], channel_id, "hello there :)")
    src.message.message_send_v2(reg_users_data[1]['token'], channel_id, "this is the last message, testing again")

    long_string = "1" * 1100

    # searching for long string
    with pytest.raises(InputError):
        src.other.search_v2(reg_users_data[1]['token'], long_string)
