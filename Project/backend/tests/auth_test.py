import pytest
import src.auth
import src.other

from src.error import InputError
from src.error import AccessError


@pytest.fixture
def reg_login():
    #register three users
    reg_result =   [0,0,0,0]
    login_result = [0,0,0,0]

    reg_result[0] = src.auth.auth_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    reg_result[1] = src.auth.auth_register_v2('yetanother.validemail123@gmail.com', '123abc!@#++', 'Dylan', 'Meringue')
    reg_result[2] = src.auth.auth_register_v2('notthisagain.validemail456@gmail.com', '123abc!@#--', 'Manuel', 'Internetiquette')
    reg_result[3] = src.auth.auth_register_v2('thisisavalidemail@gmail.com', '!@#$%^&*()', 'Jim', 'J Thompson')
    
    login_result[0] = src.auth.auth_login_v2('validemail@gmail.com', '123abc!@#')
    login_result[1] = src.auth.auth_login_v2('yetanother.validemail123@gmail.com', '123abc!@#++')
    login_result[2] = src.auth.auth_login_v2('notthisagain.validemail456@gmail.com', '123abc!@#--')
    login_result[3] = src.auth.auth_login_v2('thisisavalidemail@gmail.com', '!@#$%^&*()')

    return {
        "reg_result": reg_result,
        "login_result": login_result,
    }


@pytest.fixture
def clear():
    src.other.clear_v1()

def test_login(clear, reg_login):
    # tests to determine if auth_login_v2 works correctly

    rr = reg_login['reg_result']
    lr = reg_login['login_result']

    # check if token is valid and correct auth_user_id has been returned
    for i in range (0, len(rr)):
        assert (src.auth.auth_token_to_id(rr[i]['token']) == src.auth.auth_token_to_id(lr[i]['token']))
        assert src.auth.auth_session_verify(rr[i]['token'])
        assert src.auth.auth_session_verify(lr[i]['token'])
        assert lr[i]['auth_user_id'] == rr[i]['auth_user_id']


def test_wrong_login(clear, reg_login):
    # invalid login attempts using wrong password

    with pytest.raises(InputError):
        src.auth.auth_login_v2('validemail@gmail.com', '__123abc!@#')

    with pytest.raises(InputError):
        src.auth.auth_login_v2('yetanother.validemail123@gmail.com', '__123abc!@#++')
    
    with pytest.raises(InputError):
        src.auth.auth_login_v2('notthisagain.validemail456@gmail.com', '__123abc!@#--')
    
    # test unregistered email
    with pytest.raises(InputError):
        src.auth.auth_login_v2('unregistered@bmail.com', '__123abc!@#--')


def test_wrong_register(clear):
    # tests to determine if auth_register_v2 works correctly

    # email not valid
    with pytest.raises(InputError):
        src.auth.auth_register_v2('_invalidemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    
    # repeated email used to register
    src.auth.auth_register_v2('thisisavalidemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    with pytest.raises(InputError):
        src.auth.auth_register_v2('thisisavalidemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    
    # passwords too short
    with pytest.raises(InputError):
        src.auth.auth_register_v2('herewehave.validemail123@gmail.com', '123ab', 'Dylan', 'Meringue')
    
    # first/last name not valid (not between 1 and 50 chars in length)
    with pytest.raises(InputError):
        src.auth.auth_register_v2('herewehaveagain.validemail456@gmail.com', '123abc!@#--', '', 'Internetiquette')
    
    with pytest.raises(InputError):
        src.auth.auth_register_v2('andagain.validemail456@gmail.com', '123abc!@#--', 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz', 'Internetiquette')

    with pytest.raises(InputError):
        src.auth.auth_register_v2('thelast.validemail456@gmail.com', '123abc!@#--', 'Manuel', '')
    
    with pytest.raises(InputError):
        src.auth.auth_register_v2('theverylast.validemail456@gmail.com', '123abc!@#--', 'Manuel', 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz')


def test_handle(clear):
    # tests for multiple valid registrations but with the same names

    reg_result = [0,0,0]
    login_result = [0,0,0]

    reg_result[0] = src.auth.auth_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    reg_result[1] = src.auth.auth_register_v2('yetanother.validemail123@gmail.com', '123abc!@#++', 'Hayden', 'Everest')
    reg_result[2] = src.auth.auth_register_v2('notthisagain.validemail456@gmail.com', '123abc!@#--', 'Hayden', 'Everest')

    login_result[0] = src.auth.auth_login_v2('validemail@gmail.com', '123abc!@#')
    login_result[1] = src.auth.auth_login_v2('yetanother.validemail123@gmail.com', '123abc!@#++')
    login_result[2] = src.auth.auth_login_v2('notthisagain.validemail456@gmail.com', '123abc!@#--')

    # check if token is valid and correct auth_user_id has been returned
    for i in range (0, len(reg_result)):
        assert (src.auth.auth_token_to_id(reg_result[i]['token']) == src.auth.auth_token_to_id(login_result[i]['token']))
        assert src.auth.auth_session_verify(reg_result[i]['token'])
        assert login_result[i]['auth_user_id'] == reg_result[i]['auth_user_id']


def test_sessions(clear):
    # tests for multiple sessions    

    login_result = []
    reg_result = src.auth.auth_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')

    # test for 10 sessions of this user
    for i in range (0, 10):
        login_result.append(src.auth.auth_login_v2('validemail@gmail.com', '123abc!@#'))

    # check if token is valid and correct auth_user_id has been returned
    for i in range (0, len(login_result)):
        assert (src.auth.auth_token_to_id(reg_result['token']) == src.auth.auth_token_to_id(login_result[i]['token']))
        assert src.auth.auth_session_verify(reg_result['token'])
        assert login_result[i]["auth_user_id"] == reg_result["auth_user_id"]


def test_sessions2(clear):
    # tests for multiple sessions    

    login_result = []
    reg_result = src.auth.auth_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')

    # test for 10 more sessions of this user
    for i in range (0, 10):
        login_result.append(src.auth.auth_login_v2('validemail@gmail.com', '123abc!@#'))

    # log out 5 sessions
    for i in range (0,5):
        src.auth.auth_logout_v2(login_result[0]['token'])
        login_result.pop(0)
    
    # test for 5 more sessions of this user
    for i in range (0, 10):
        login_result.append(src.auth.auth_login_v2('validemail@gmail.com', '123abc!@#'))
    
    # conduct checks
    for i in range (0, len(login_result)):
        assert (src.auth.auth_token_to_id(reg_result['token']) == src.auth.auth_token_to_id(login_result[i]['token']))
        assert src.auth.auth_session_verify(reg_result['token'])
        assert login_result[i]["auth_user_id"] == reg_result["auth_user_id"]
    
    #try to logout using an invalid token
    random_token = login_result[0]['token']
    with pytest.raises(AccessError):
        src.auth.auth_logout_v2(random_token)
        src.auth.auth_logout_v2(random_token)

def test_logout(clear, reg_login):
    # test logging out sessions

    login_result = []
    
    # test for 10 more sessions of this user
    for i in range (0, 10):
        login_result.append(src.auth.auth_login_v2('validemail@gmail.com', '123abc!@#'))

    # check if token is valid and correct auth_user_id has been returned
    for i in range (0, len(login_result)):
        assert src.auth.auth_session_verify(login_result[i]['token'])
        assert src.auth.auth_logout_v2(login_result[i]['token'])['is_success']

    # try logging out using the same (logged out) tokens
    for i in range(0, len(login_result)):
        with pytest.raises(AccessError):
            src.auth.auth_logout_v2(login_result[i]['token'])


def test_wrong_logout(clear, reg_login):
    # test logging out with invalid token
    with pytest.raises(AccessError):
        src.auth.auth_logout_v2('this_is_an_invalid_token')


def test_password_reset(clear, reg_login):
    # reset password for user 0
    my_reset_code = src.auth.auth_passwordreset_request_v1('validemail@gmail.com')
    src.auth.auth_passwordreset_reset_v1(my_reset_code, 'mynewpassword:)')

    # try logging in with old password
    with pytest.raises(InputError):
            src.auth.auth_login_v2('validemail@gmail.com', '123abc!@#')

    # try logging in with new password
    src.auth.auth_login_v2('validemail@gmail.com', 'mynewpassword:)')
   