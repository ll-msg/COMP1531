import pytest
from src.auth import auth_register_v2
from src.other import clear_v1
from src.user import user_profile_v2, user_profile_setname_v2, user_profile_setemail_v2, user_profile_sethandle_v1
from src.auth import auth_token_to_id 
from src.error import InputError
from src.error import AccessError

@pytest.fixture
def set_up_user():
    clear_v1()    
    global_owner_id = auth_register_v2('validmail@gmail.com', '123abc!', 'Obiwan', 'Kenobi')
    global_owner_token = global_owner_id['token']
    auth_register_v2('val@gmail.com', '123abc!', 'Master', 'Yoda')
    return global_owner_token

def test_user_profile_InputError():
    clear_v1() 
    #testing that an Input Error is raised when given an invalid uid
    global_owner_id = auth_register_v2('validmail@gmail.com', '123abc!', 'Obiwan', 'Kenobi')
    global_owner_token = global_owner_id['token']
    global_owner_token_id = global_owner_id['auth_user_id']
    # user_id is unique for each user
    invalid_user_id = global_owner_token_id - 1

    with pytest.raises(InputError):
        user_profile_v2(global_owner_token, invalid_user_id)   

def test_user_profile(set_up_user):
    #converts token to u_id
    global_owner_token = set_up_user
    global_owner_id = auth_token_to_id(global_owner_token)  
     
    #testing that an Input Error is raised when given an invalid uid
    with pytest.raises(InputError):
        user_profile_v2(global_owner_token, '')
    

    
    assert user_profile_v2(global_owner_token, global_owner_id) == {
        'user': {
            'u_id': 0,
            'email': 'validmail@gmail.com',
            'name_first': 'Obiwan',
            'name_last': 'Kenobi',
            'handle_str': 'obiwankenobi',
            'profile_img_url' : '',
        }
    }
    clear_v1()

def test_user_profile_setname_v2(set_up_user):
    #converts token to u_id
    global_owner_token = set_up_user
    global_owner_id = auth_token_to_id(global_owner_token)
    
    #testing circumstance where no first name is provided
    with pytest.raises(InputError):
        user_profile_setname_v2(global_owner_token, '', 'Pig')
    
    #testing circumstance where no last name is provided
    with pytest.raises(InputError):
        user_profile_setname_v2(global_owner_token, 'Peppa', '')
    
    #testing circumstance where 51 characters for first name is provided
    with pytest.raises(InputError):
        user_profile_setname_v2(global_owner_token, 'Peppapigisthebestihavenothingelsetosayhowamisuppose', 'Pig')
    
    #testing circumstance where 51 characters for last name is provided
    with pytest.raises(InputError):
        user_profile_setname_v2(global_owner_token, 'Peppa', 'Peppapigisthebestihavenothingelsetosayhowamisuppose')

    
    #changing the user's name from Obiwan Kenobi to Peppa Pig
    user_profile_setname_v2(global_owner_token, 'Peppa', 'Pig')
    #checking to see if changes have been made
    assert user_profile_v2(global_owner_token, global_owner_id) == {
        'user': {
            'u_id': 0,
            'email': 'validmail@gmail.com',
            'name_first': 'Peppa',
            'name_last': 'Pig',
            'handle_str': 'obiwankenobi',
            'profile_img_url' : '',
        }
    }
    clear_v1()

def test_user_profile_setemail_v2(set_up_user):
    #converts token to u_id
    global_owner_token = set_up_user
    global_owner_id = auth_token_to_id(global_owner_token)    
    
    #sets up second user 
    auth_register_v2('123@gmail.com', '123abc!', 'Peppa', 'Pig')
    
    #tests that Input Error is raised when invalid email is given
    with pytest.raises(InputError):
        user_profile_setemail_v2(global_owner_token, '') 
    
    #tests that Input Error is raised when email is already being used by another user
    with pytest.raises(InputError):
        user_profile_setemail_v2(global_owner_token, '123@gmail.com') 
   
    #test changing the email of the account
    user_profile_setemail_v2(global_owner_token, 'newemail@gmail.com')
    assert user_profile_v2(global_owner_token, global_owner_id) == {
        'user': {
            'u_id': 0,
            'email': 'newemail@gmail.com',
            'name_first': 'Obiwan',
            'name_last': 'Kenobi',
            'handle_str': 'obiwankenobi',
            'profile_img_url' : '',
        }
    }
    clear_v1()

def test_user_profile_sethandle_v1(set_up_user):
    #converts token to u_id
    global_owner_token = set_up_user
    global_owner_id = auth_token_to_id(global_owner_token)    
    
    #sets up second user 
    auth_register_v2('123@gmail.com', '123abc!', 'Peppa', 'Pig')
    
    #tests that Input Error is raised when handle is below 3 characters
    with pytest.raises(InputError):
        user_profile_sethandle_v1(global_owner_token, 'hi') 
    
    #tests that Input Error is raised when handle is above 20 characters
    with pytest.raises(InputError):
        user_profile_sethandle_v1(global_owner_token, 'ineedtohitabovetwenty') 
    
    #tests that Input Error is raised when handle is in use by another user
    with pytest.raises(InputError):
        user_profile_sethandle_v1(global_owner_token, 'peppapig') 
    
    #testing that an Access Error is raised when given an invalid token
    with pytest.raises(AccessError):
        user_profile_sethandle_v1('', 'kenobiobiwan')
    
    #tests changing handle to another valid handle 
    user_profile_sethandle_v1(global_owner_token, 'kenobiobiwan')
    assert user_profile_v2(global_owner_token, global_owner_id) == {
        'user': {
            'u_id': 0,
            'email': 'validmail@gmail.com',
            'name_first': 'Obiwan',
            'name_last': 'Kenobi',
            'handle_str': 'kenobiobiwan',
            'profile_img_url' : '',
        }
    }
    clear_v1()

