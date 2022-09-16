import pytest
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.dm_data import dm_data
from src.dm import dm_details_v1, dm_list_v1, dm_create_v1, dm_remove_v1, dm_invite_v1, dm_leave_v1, dm_messages_v1
from src.other import clear_v1
from src.error import InputError
from src.error import AccessError
from src.message import message_senddm_v1

@pytest.fixture
def input():
    clear_v1()

    # create new test accounts
    global_owner_id = auth_register_v2('vaildmail@gmail.com', '123abc!', 'Obiwan', 'Kenobi')
    global_owner_token = global_owner_id['token']
    global_owner_id = global_owner_id['auth_user_id']
    owner_id = auth_register_v2('vaildmail2@gmail.com','1122abc!','master', 'Yoda')
    owner_token = owner_id['token']
    owner_id = owner_id['auth_user_id']
    member_id_1 = auth_register_v2('member@gmai.com', '321abc!', 'Anakin', 'Skywalker' )
    member_token_1 = member_id_1['token']
    member_id_1 = member_id_1['auth_user_id']
    member_id_2 = auth_register_v2('member2@gmai.com', 'acd3455!', 'Samatoki', 'Aohitsugi' )
    member_token_2 = member_id_2['token']
    member_id_2 = member_id_2['auth_user_id']
    

    # create a dm channel
    dm_channel_1 = dm_create_v1(owner_token, [member_id_1])
    dm_channel_1 = dm_channel_1['dm_id']
    dm_channel_2 = dm_create_v1(owner_token, [member_id_2])
    dm_channel_2 = dm_channel_2['dm_id']

    # return the input list
    input_list = [global_owner_id, owner_token, member_token_1, member_token_2, dm_channel_1, dm_channel_2, owner_id, member_id_1, member_id_2, global_owner_token]
    return input_list

@pytest.fixture
def set_up_user():
    clear_v1()    
    global_owner_id = auth_register_v2('vaildmail@gmail.com', '123abc!', 'Obiwan', 'Kenobi')
    global_owner_token = global_owner_id['token']
    return global_owner_token
    

def test_dm_messages_send_50(input):
    index = 0
    while index != 51:
        message_senddm_v1(input[1],input[4], "test" )
        index = index + 1
    assert dm_messages_v1(input[1],input[4], 0)['end'] == 50
    clear_v1()
    

''' dm_create test '''
def test_dm_create(input):
    
    # right examples
    dm_id = dm_create_v1(input[1], [input[7]])['dm_id']
    deets = dm_details_v1(input[1], dm_id)

    assert input[7] in [memb['u_id'] for memb in deets['members']]
    clear_v1()


def test_dm_create_exception():
    clear_v1()
    # create a new user
    owner_user_id = auth_register_v2("123@mail.com", "passdrow", "Tony", "Stark")
    owner_user_token = owner_user_id['token']
    owner_user_id = owner_user_id['auth_user_id']
    test_id = owner_user_id - 1

    # u_id does not refer to a valid user - the test should have an input error
    with pytest.raises(InputError):
        assert dm_create_v1(owner_user_token, [test_id])
    clear_v1()




def test_dm_list(input):
    # test the list function
    assert input[4] in dm_list_v1(input[2])['dms'][0].values()
    clear_v1()



def test_dm_invite(input):
    # Testing right examples
    dm_invite_v1(input[1], input[4], input[8])
    assert dm_details_v1(input[1], input[4]) == {
        'name': 'anakinskywalker,masteryoda',
        'members': [
                {
                    'email': 'vaildmail2@gmail.com',
                    'u_id': input[6],
                    'name_first': "master",
                    'name_last':"Yoda",
                    'handle': "masteryoda",
                },
               {
                    'email': 'member@gmai.com',
                    'u_id': input[7],
                    'name_first': "Anakin",
                    'name_last': "Skywalker",
                    'handle': "anakinskywalker",
                }, {
                    'email': 'member2@gmai.com',
                    'u_id': input[8],
                    'name_first': "Samatoki",
                    'name_last': "Aohitsugi",
                    'handle': "samatokiaohitsugi",
                }
        ]
    }

    clear_v1()


def test_dm_invite_exception():
    clear_v1()
    #create new members
    owner_user_id = auth_register_v2("123@mail.com", "passdrow", "Tony", "Stark")
    owner_user_token = owner_user_id['token']
    owner_user_id = owner_user_id['auth_user_id']
    participant_user_id = auth_register_v2("456@mail.com", "drowssap", "Steve", "Rogers")
    participant_user_id = participant_user_id['auth_user_id']
    participant_user_id_1 = auth_register_v2("789@mail.com", "drowssapp", "Steeve", "Roggers")
    participant_user_id_1 = participant_user_id_1['auth_user_id']
    participant_user_id_2 = auth_register_v2("1011@mail.com", "drowssappp", "Steeeve", "Rogggers")
    participant_user_token_2 = participant_user_id_2['token']
    participant_user_id_2 = participant_user_id_2['auth_user_id']

    # set up test dm channel
    new_dm_public = dm_create_v1(owner_user_token, [participant_user_id])
    new_dm_public = new_dm_public['dm_id']
    # the authorised user is not already a member of DM - the test should have an AccessError
    with pytest.raises(AccessError):
        dm_invite_v1(participant_user_token_2, new_dm_public, participant_user_id_1)
    clear_v1()

def test_dm_invite_dmid():
    clear_v1()
    #create new members
    owner_user_id = auth_register_v2("123@mail.com", "passdrow", "Tony", "Stark")
    owner_user_token = owner_user_id['token']
    owner_user_id = owner_user_id['auth_user_id']
    participant_user_id = auth_register_v2("456@mail.com", "drowssap", "Steve", "Rogers")
    participant_user_id = participant_user_id['auth_user_id']

    # set up test dm channel
    new_dm_public = dm_create_v1(owner_user_token, [participant_user_id])
    new_dm_public = new_dm_public['dm_id']
    test_dm_id = new_dm_public - 1
    # the dm is not an exsited DM channel - the test should have an InputError
    with pytest.raises(InputError):
        dm_invite_v1(owner_user_token, test_dm_id, participant_user_id)
    clear_v1()

def test_dm_invite_uid():
    clear_v1()
    #create new members
    owner_user_id = auth_register_v2("123@mail.com", "passdrow", "Tony", "Stark")
    owner_user_token = owner_user_id['token']
    owner_user_id = owner_user_id['auth_user_id']
    participant_user_id = auth_register_v2("456@mail.com", "drowssap", "Steve", "Rogers")
    participant_user_id = participant_user_id['auth_user_id']

    # set up test dm channel
    new_dm_public = dm_create_v1(owner_user_token, [participant_user_id])
    new_dm_public = new_dm_public['dm_id']
    test_id = participant_user_id - 10
    # the user id is not valid - raise an InputError
    with pytest.raises(InputError):
        dm_invite_v1(owner_user_token, new_dm_public, test_id)
    clear_v1()




def test_dm_leave(input):
    # Testing right examples
    dm_leave_v1(input[2], input[4])
    assert dm_details_v1(input[1], input[4]) == {
        'name': 'anakinskywalker,masteryoda', 
        'members': [
                {
                    'email': 'vaildmail2@gmail.com',
                    'u_id': input[6],
                    'name_first': "master",
                    'name_last':"Yoda",
                    'handle': "masteryoda",
                }
        ]
    }
    clear_v1()


def test_dm_leave_dmid():
    # the dm is not an exsited DM channel - the test should have an InputError
    clear_v1()
    owner_user_id = auth_register_v2("123@mail.com", "passdrow", "Tony", "Stark")
    owner_user_token = owner_user_id['token']
    owner_user_id = owner_user_id['auth_user_id']
    participant_user_id = auth_register_v2("456@mail.com", "drowssap", "Steve", "Rogers")
    participant_user_token = participant_user_id['token']
    participant_user_id = participant_user_id['auth_user_id']
    # create only one dm with unique dm id
    new_dm = dm_create_v1(owner_user_token, [participant_user_id])
    new_dm = new_dm['dm_id']
    # test_dm_id is invalid
    test_dm_id = new_dm - 1
    # dm id is not a vaild channel 
    with pytest.raises(InputError):
        dm_leave_v1(participant_user_token, test_dm_id)


def test_dm_leave_participate(input):
    # the authorised user is not a member of DM - the test should have an AccessError
    with pytest.raises(AccessError):
        dm_leave_v1(input[2], input[5])

    clear_v1()





def test_dm_remove(input):
    
    # Testing right examples
    dm_remove_v1(input[1], input[5])
    assert dm_list_v1(input[1]) == {'dms': [{'dm_id': 0, 'name': 'anakinskywalker,masteryoda'}]}
    
    clear_v1()


def test_dm_remove_exception():
    # the dm is not an exsited DM channel - the test should have an InputError
    clear_v1()
    owner_user_id = auth_register_v2("123@mail.com", "passdrow", "Tony", "Stark")
    owner_user_token = owner_user_id['token']
    owner_user_id = owner_user_id['auth_user_id']
    participant_user_id = auth_register_v2("456@mail.com", "drowssap", "Steve", "Rogers")
    participant_user_id = participant_user_id['auth_user_id']
    # create only one dm with unique dm id
    new_dm = dm_create_v1(owner_user_token, [participant_user_id])
    new_dm = new_dm['dm_id']
    # test_dm_id is invalid
    test_dm_id = new_dm - 1
    # dm id is not a vaild channel 
    with pytest.raises(InputError):
        dm_remove_v1(owner_user_token, test_dm_id)

def test_dm_remove_creator(input):
    # the user is not the original dm creator - the test should have an AccessError
    with pytest.raises(AccessError):
        dm_remove_v1(input[2], input[4])

    clear_v1()




def test_dm_details(input):
    # test right examples
    assert dm_details_v1(input[2], input[4]) == {
            'name': 'anakinskywalker,masteryoda',
        'members': [
                {
                    'email': 'vaildmail2@gmail.com',
                    'u_id': input[6],
                    'name_first': "master",
                    'name_last':"Yoda",
                    'handle': "masteryoda",
                },
                {
                    'email': 'member@gmai.com',
                    'u_id': input[7],
                    'name_first': "Anakin",
                    'name_last': "Skywalker",
                    'handle': "anakinskywalker",
                }
        ]
    }
    clear_v1()
          

def test_dm_details_dmid():
    
    # the dm is not an exsited DM channel - the test should have an InputError  
    clear_v1()
    owner_user_id = auth_register_v2("123@mail.com", "passdrow", "Tony", "Stark")
    owner_user_token = owner_user_id['token']
    owner_user_id = owner_user_id['auth_user_id']
    participant_user_id = auth_register_v2("456@mail.com", "drowssap", "Steve", "Rogers")
    participant_user_id = participant_user_id['auth_user_id']
    # create only one dm with unique dm id
    new_dm = dm_create_v1(owner_user_token, [participant_user_id])
    new_dm = new_dm['dm_id']
    # test_dm_id is invalid
    test_dm_id = new_dm - 1
    # dm id is not a vaild channel 
    with pytest.raises(InputError):
        dm_details_v1(owner_user_token, test_dm_id)
    clear_v1()

def test_dm_participate(input):
    # the authorised user is not a member of this DM with dm_id
    with pytest.raises(AccessError):
        dm_details_v1(input[2], input[5])
    clear_v1()




def test_dm_messages(input):
    # test right examples
    assert(dm_messages_v1(input[1], input[4], 0)) == {'messages': [], 'start': 0, 'end': -1}
    clear_v1()

    
def test_dm_messages_number(input):
    # start is greater than total number of messages in the dm
    with pytest.raises(InputError):
        dm_messages_v1(input[1], input[4], 1)
    clear_v1()

def test_dm_messages_dmid():
    # test if dm_id is a valid dm
    clear_v1()
    owner_user_id = auth_register_v2("123@mail.com", "passdrow", "Tony", "Stark")
    owner_user_token = owner_user_id['token']
    owner_user_id = owner_user_id['auth_user_id']
    participant_user_id = auth_register_v2("456@mail.com", "drowssap", "Steve", "Rogers")
    participant_user_id = participant_user_id['auth_user_id']
    # create only one dm with unique dm id
    new_dm = dm_create_v1(owner_user_token, [participant_user_id])
    new_dm = new_dm['dm_id']
    # test_dm_id is invalid
    test_dm_id = new_dm - 1
    # dm id is not a vaild channel 
    with pytest.raises(InputError):
        dm_messages_v1(owner_user_token, test_dm_id, 0)
    clear_v1()
def test_dm_messages_user(input):
    # test if the authorised user is a member of DM
    with pytest.raises(AccessError):
        dm_messages_v1(input[3], input[4], 0)
    clear_v1()
    
def test_dm_list_empty(set_up_user):
    assert dm_list_v1(set_up_user) == {'dms' : []}
    clear_v1()



