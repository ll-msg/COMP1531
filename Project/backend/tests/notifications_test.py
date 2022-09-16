import pytest
from src.admin import admin_verify, user_permission_change_v1, user_remove_v1
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.channel import channel_join_v2, channel_invite_v2
from src.dm import dm_create_v1
from src.other import clear_v1
from src.message import message_send_v2, message_senddm_v1

from src.notifications import notification_message_get_v1

from src.error import InputError
from src.error import AccessError


@pytest.fixture
def rr():
    clear_v1()

    #register two users
    reg_result = []

    reg_result.append(auth_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest'))
    reg_result.append(auth_register_v2('yetanother.validemail123@gmail.com', '123abc!@#++', 'Dylan', 'Meringue'))

    # create a private channel, invite user 1, both users ping each other a bunch of times
    random_channel = channels_create_v2(reg_result[0]['token'], "random channel", False)
    channel_id = random_channel['channel_id']
    channel_join_v2(reg_result[0]['token'], channel_id)
    channel_invite_v2(reg_result[0]['token'], channel_id, reg_result[1]['auth_user_id'])

    for i in range (0, 5):
        message_send_v2(reg_result[0]['token'], channel_id, f"@dylanmeringue {i}")
    
    for i in range (0, 15):
        message_send_v2(reg_result[1]['token'], channel_id, f"@haydeneverest {i}")

    # create a dm, both users ping each other a bunch of times
    random_dm = dm_create_v1(reg_result[0]['token'], [reg_result[1]['auth_user_id']])
    dm_id = random_dm['dm_id']

    for i in range (0, 5):
        message_senddm_v1(reg_result[0]['token'], dm_id, f"@dylanmeringue {i}")
    
    for i in range (0, 15):
        message_senddm_v1(reg_result[1]['token'], dm_id, f"@haydeneverest {i}")

    return reg_result

def test_get_notifs_none():
    clear_v1()
    reg_result = auth_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    # user has no notifications
    assert(notification_message_get_v1(reg_result['token'])['notifications'] == [])

def test_get_notifs_regular(rr):
    # get notifications for both
    notifs_0 = []
    for notification in notification_message_get_v1(rr[0]['token'])['notifications']:
        notifs_0.append(notification['notification_message'])
    
    notifs_1 = []
    for notification in notification_message_get_v1(rr[1]['token'])['notifications']:
        notifs_1.append(notification['notification_message'])

    # assert number of notifications
    assert(len(notifs_0) == 20)
    assert(len(notifs_1) == 11)

    assert(isinstance(notifs_0, list))

    # assert edge cases of notifications
    assert ("dylanmeringue tagged you in random channel: @haydeneverest 0" not in notifs_0)
    assert ("dylanmeringue tagged you in random channel: @haydeneverest 9" not in notifs_0)
    assert ("dylanmeringue tagged you in random channel: @haydeneverest 10" in notifs_0)
    assert ("dylanmeringue tagged you in dylanmeringue,haydeneverest: @haydeneverest 0" in notifs_0)
    assert ("dylanmeringue tagged you in dylanmeringue,haydeneverest: @haydeneverest 14" in notifs_0)

    assert ("haydeneverest tagged you in random channel: @dylanmeringue 0" in notifs_1)
    assert ("haydeneverest tagged you in random channel: @dylanmeringue 4" in notifs_1)
    assert ("haydeneverest tagged you in dylanmeringue,haydeneverest: @dylanmeringue 0" in notifs_1)
    assert ("haydeneverest tagged you in dylanmeringue,haydeneverest: @dylanmeringue 4" in notifs_1)
