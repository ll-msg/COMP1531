import pytest
from src.admin import admin_verify
from src.admin import user_permission_change_v1
from src.admin import user_remove_v1
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.channel import channel_join_v2
from src.dm import dm_create_v1
from src.other import clear_v1
from src.message import message_send_v2
from src.message import message_senddm_v1

from src.error import InputError
from src.error import AccessError

@pytest.fixture
def rr():
    clear_v1()

    #register three users
    reg_result = [0,0,0]

    reg_result[0] = auth_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    reg_result[1] = auth_register_v2('yetanother.validemail123@gmail.com', '123abc!@#++', 'Dylan', 'Meringue')
    reg_result[2] = auth_register_v2('notthisagain.validemail456@gmail.com', '123abc!@#--', 'Manuel', 'Internetiquette')
    
    return reg_result

def test_first_owner(rr):
    # check if the first user to register is a DREAMS owner and the others are not

    assert (    admin_verify(rr[0]['token']))
    assert (not admin_verify(rr[1]['token']))
    assert (not admin_verify(rr[2]['token']))


def test_permission_change(rr):
    
    # 0 makes 1 an admin then 1 makes 2 an admin
    user_permission_change_v1(rr[0]['token'], rr[1]['auth_user_id'], 1)
    user_permission_change_v1(rr[1]['token'], rr[2]['auth_user_id'], 1)

    assert (admin_verify(rr[0]['token']))
    assert (admin_verify(rr[1]['token']))
    assert (admin_verify(rr[2]['token']))

    # 2 removes 0 as admin then 1 removes 2 as admin
    user_permission_change_v1(rr[2]['token'], rr[0]['auth_user_id'], 2)
    user_permission_change_v1(rr[1]['token'], rr[2]['auth_user_id'], 2)

    assert (not admin_verify(rr[0]['token']))
    assert (    admin_verify(rr[1]['token']))
    assert (not admin_verify(rr[2]['token']))


def test_permission_change_fail(rr):
    
    # non admin 1 tries to makes 2 an admin
    with pytest.raises(AccessError):
        user_permission_change_v1(rr[1]['token'], rr[2]['auth_user_id'], 1)
    
    # 0 tries to remove themselves as admin (but is the only admin)
    with pytest.raises(InputError):
        user_permission_change_v1(rr[0]['token'], rr[0]['auth_user_id'], 2)
    
    # invalid permission id
    with pytest.raises(InputError):
        user_permission_change_v1(rr[0]['token'], rr[1]['auth_user_id'], 3)
    
    # 0 tries to change permission of auth_user_id 5 (invalid id)
    with pytest.raises(InputError):
        user_permission_change_v1(rr[0]['token'], 5, 2)



def test_remove(rr):

    m = [0,0,0,0]
    d = [0,0,0,0]

    # 0 makes 1 an admin
    user_permission_change_v1(rr[0]['token'], rr[1]['auth_user_id'], 1)

    random_channel = channels_create_v2(rr[1]['token'], "random channel", True)
    channel_id = random_channel['channel_id']
    channel_join_v2(rr[1]['token'], channel_id)

    m[0] = message_send_v2(rr[1]['token'], channel_id, "I'm testing this function")
    m[1] = message_send_v2(rr[1]['token'], channel_id, "another message")
    m[2] = message_send_v2(rr[1]['token'], channel_id, "hello there :)")
    m[3] = message_send_v2(rr[1]['token'], channel_id, "this is the last message, testing again")

    random_dm = dm_create_v1(rr[1]['token'], [rr[1]['auth_user_id'], rr[2]['auth_user_id']])
    dm_id = random_dm['dm_id']

    d[0] = message_senddm_v1(rr[1]['token'], dm_id, "I'm testing this function")
    d[1] = message_senddm_v1(rr[1]['token'], dm_id, "another message")
    d[2] = message_senddm_v1(rr[1]['token'], dm_id, "hello there :")
    d[3] = message_senddm_v1(rr[1]['token'], dm_id, "this is the last message, testing again")
    
    # 1 removes 2
    user_remove_v1(rr[1]['token'], rr[2]['auth_user_id'])
    
    # 0 removes 1
    user_remove_v1(rr[0]['token'], rr[1]['auth_user_id'])


def test_remove_fail(rr):
    
    # non admin 1 tries to remove 2
    with pytest.raises(AccessError):
        user_remove_v1(rr[1]['token'], rr[2]['auth_user_id'])
    
    # 0 tries to remove themselves (but is the only admin)
    with pytest.raises(InputError):
        user_remove_v1(rr[0]['token'], rr[0]['auth_user_id'])
    
    # 0 tries to remove auth_user_id 5 (invalid id)
    with pytest.raises(InputError):
        user_remove_v1(rr[0]['token'], 5)


