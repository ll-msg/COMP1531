
# import src.auth_data as auth_data
import src.notifications
from src.dm_data import dm_data
from src.auth import auth_session_verify, auth_token_to_id 
from src.dm_message_data import dm_message_data
from src.error import InputError
from src.error import AccessError
from src.information_io import write_info
from src.read_json import read_info
from src.user_stats_data import user_stats_data
from src.dreams_stats_data import dreams_stats_data
from datetime import timezone, datetime, timedelta
from src.channel import create_reacts_list


'''
    dm_details_v1 will give basic information about the DM that users are part of. If the given token is valid, the dm id is valid, and the person who asks to view is in the dm, the user will receive the basic information.

    Arguments:
        <token>                   - The code which can be decoded to find the user id
        <dm_id> (integer)         - The idea of the dm the user asks to view information
        ...

    Exceptions:
        InputError  - Occurs when the dm_id does not refer to a valid channel.
        AccessError  - Occurs when the given token does not refer to a valid user
        AccessError - Occurs when the authorised user is not already a member of the channel

    Return Value:
        Returns a dictionary (dm_detail) with all the details previously stated.
'''

def dm_details_v1(token, dm_id):
    # check whether the input token refer to a valid user id
    auth_session_verify(token)
    # read channel data
    dm_data = read_info('dm_data.json')

    # check if the given dm_id is a valid DM
    if str(dm_id) not in dm_data:
        raise InputError('Input dm id is invalid!')

    # check if the authorised user is a member of the dm
    if (check_participate(token, dm_id) == False):
        raise AccessError("The authorised user is not a member of DM!")
    
    # creates a dictionary for the dm details
    dm_detail = {
        'name': 'to_be_named',
        'members': [],
    }
    
    # checks the dm in dm_data to get the necessary info
    dm_detail['name'] = dm_data[str(dm_id)]['name']
      
    # sets up a loop to add all members and their details into channel_deets
    for k in range(0, len(dm_data[str(dm_id)]['dm_members'])):
        user_id = dm_data[str(dm_id)]['dm_members'][k]['u_id']
        dm_detail['members'].append(create_user_detail(user_id))
        
        
    return dm_detail



'''
    dm_list_v1 will return the list of DMs that the user is a member of. If the given token is valid, the user will receive the list of DMs
    Arguments:
        <token>                   - The code which can be decoded to find the user id
        ...

    Exceptions:
        AccessError  - Occurs when the given token does not refer to a valid user

    Return Value:
        Returns a dictionary (return_dic) with all the DMs that the user is a member of.
'''
def dm_list_v1(token):
    # check whether the input token refer to a valid user id
    auth_session_verify(token)
    # convert token to user id
    auth_user_id = auth_token_to_id(token)
    # read channel data
    dm_data = read_info('dm_data.json')
    
    dm_list = []
    if len(dm_data) == 0:
        return_dic = {}
        return_dic['dms'] = dm_list
        return return_dic
    # Loop through each channel and check if user
    # is a member/owner of the channel    
    for index in dm_data:
        dm = dm_data[index]
        # If there is a match we will add the channel info
        # to channels_list and skip to the next channel
        for member in dm['dm_members']:
            if (member['u_id'] == auth_user_id):
                detail_dic = {}
                detail_dic['dm_id'] = int(index)
                detail_dic['name'] = dm['name']
                dm_list.append(detail_dic)
                break
    return_dic = {}
    return_dic['dms'] = dm_list
    return return_dic


'''
    dm_create_v1 will create a new dm. If the given token is valid, and given u_id(s) refer to valid user, the new dm will be created
    Arguments:
        <token>                   - The code which can be decoded to find the user id
        <u_id> (list)             - A list of user id(s) who will be added to the new dm
        ...

    Exceptions:
        AccessError  - Occurs when the given token does not refer to a valid user
        InputError   - Occurs when any of the given user id does not refer to a valid user

    Return Value:
        Returns a dictionary with new dm id and dm name.
'''
def dm_create_v1(token, u_id):
    # check whether the input token refer to a valid user id
    auth_session_verify(token)
    # convert token to user id
    auth_user_id = auth_token_to_id(token)
    # read channel data
    dm_data = read_info('dm_data.json')

    users_data = read_info("auth_users_data")

    # check if any of the u_id does not refer to a valid user
    check_uid = False
    for user in u_id:
        for email in users_data:
            if users_data[email]['auth_user_id'] == user:
                check_uid = True
    if check_uid == False:
        raise InputError('User ID does not refer to a valid user!')

    # update the dm_id
    dm_id = len(dm_data)

    # main part
    dm_data[str(dm_id)] = {
        'name': "", # handle of all the members including the owner
        'dm_owners' : [
                {'u_id': auth_user_id}
            ],
        'dm_members' : [
            ]
    }
    # update the name of dm
    name_list = []
    name_list.append(create_user_detail(auth_user_id)['handle'])
    for user in u_id:
        name_list.append(create_user_detail(user)['handle'])
    name_list.sort() 
    dm_data[str(dm_id)]['name'] = ",".join(name_list)

    # update the members id
    dm_data[str(dm_id)]['dm_members'].append({'u_id': auth_user_id})
    for users in u_id:
        member_id = {'u_id': users}
        dm_data[str(dm_id)]['dm_members'].append(member_id)

    write_info("dm_data.json", dm_data)
    
    dm_user_stats_add(auth_user_id)
    for users in u_id:
        dm_user_stats_add(users)
    
    dm_dreams_stats_add(auth_user_id)

    return {
        'dm_id': dm_id,
        'dm_name': dm_data[str(dm_id)]['name'],
    }



'''
    dm_remove_v1 will remove an existed dm. If the given token is valid and refers only to the original creator of the dm, and given dm_id refers to a valid dm, this dm will be removed
    Arguments:
        <token>                      - The code which can be decoded to find the user id
        <dm_id> (integer)            - The idea of the dm the user asks to remove
        ...

    Exceptions:
        AccessError  - Occurs when the given token does not refer to a valid user
        AccessError  - Occurs when the given token does not refer to the original creator
        InputError   - Occurs when the given dm_id does not refer to a valid dm

    Return Value:
        Returns an empty dictionary
'''
def dm_remove_v1(token, dm_id):
    # check whether the input token refer to a valid user id
    auth_session_verify(token)
    # convert token to user id
    auth_user_id = auth_token_to_id(token)
    # read dm data
    dm_data = read_info('dm_data.json')

    # check if dm_id refers to an existing DM - InputError
    if str(dm_id) not in dm_data:
        raise InputError('Input dm id is invalid!')
    # check if the user is the original DM creator - AccessError
    if dm_data[str(dm_id)]['dm_owners'][0]['u_id'] != auth_user_id:
        raise AccessError('Input user id is not the original creator!')

    del dm_data[str(dm_id)]
    write_info("dm_data.json", dm_data)

    dm_user_stats_delete(auth_user_id)
    dm_dreams_stats_delete(auth_user_id)
    
    return {
    }



'''
    dm_invite_v1 will invite a user to a dm. If the given token is valid, the dm id is valid, and the person who is invited has a valid id, the user will be automatically added to the dm.

    Arguments:
        <tokens>                  - The user id of an authorised user who is a member of the dm
        <dm_id> (integer)         - The idea of the dm the user is being invited to
        <u_id> (integer)          - The user id of a person who is not a member of the dm but is being invited in
        ...

    Exceptions:
        InputError  - Occurs when the dm_id does not refer to a valid channel.
        InputError  - Occurs when the u_id does not refer to a valid user
        AccessError - Occurs when the authorised user is not already a member of the dm

    Return Value:
        Returns an empty dictionary

'''
def dm_invite_v1(token, dm_id, u_id):
    # check whether the input token refer to a valid user id
    auth_session_verify(token)
    # convert token to user id
    # auth_user_id = auth_token_to_id(token)
    # read channel data
    dm_data = read_info('dm_data.json')

    users_data = read_info("auth_users_data")
    
    user_id_to_email = read_info("auth_user_id_to_email")
       
    # check if dm_id refers to an existing dm - InputError
    if str(dm_id) not in dm_data:
        raise InputError('Input dm id is invalid!')
    # check if u_id refers to a valid user - InputError
    valid = 0
    for email in users_data:
        if users_data[email]['auth_user_id'] == u_id:
            valid = 1
    if valid == 0:
        raise InputError('User ID does not refer to a valid user!')
    # check if the authorised user is a member of DM - AccessError
    if (check_participate(token, dm_id) == False):
        raise AccessError("The authorised user is not a member of DM!")
    # main part
    dm_data[str(dm_id)]['dm_members'].append({'u_id': u_id})
    
    write_info("dm_data.json", dm_data)

    # add notification
    src.notifications.add_join_notification(u_id, users_data[
        user_id_to_email[str(auth_token_to_id(token))]
    ]['handle'], dm_id, -1)

    dm_user_stats_add(u_id)

    return {
    }



'''
    dm_leave_v1 will let a user leave the dm. If the given token is valid, the dm id is valid, the user will be automatically leave the dm.

    Arguments:
        <token>                   - The user id of an authorised user who is a member of the dm
        <dm_id> (integer)         - The idea of the dm the user is leaving
        ...

    Exceptions:
        InputError  - Occurs when the dm_id does not refer to a valid dm
        AccessError - Occurs when input token does not refer to a valid user id
        AccessError - Occurs when the authorised user is not already a member of the dm

    Return Value:
        Returns an empty dictionary

'''
def dm_leave_v1(token, dm_id):
    # check whether the input token refer to a valid user id
    auth_session_verify(token)
    # convert token to user id
    auth_user_id = auth_token_to_id(token)
    # read channel data
    dm_data = read_info('dm_data.json')


    # check if dm_id refers to an existing dm - InputError
    if str(dm_id) not in dm_data:
        raise InputError('Input dm id is invalid!')
    # check if the authorised user is a member of DM - AccessError
    if (check_participate(token, dm_id) == False):
        raise AccessError("The authorised user is not a member of DM!")

    # main part
    dm_data[str(dm_id)]['dm_members'].remove({'u_id': auth_user_id})

    write_info("dm_data.json", dm_data)

    dm_user_stats_delete(str(auth_user_id))

    return {
    }



'''
    Use users who are members of this channel, the channel name and the starting point of the chat message are used as input
    and return the all chat messages, the start point of message and the last end point of the message

    Arguments:
        <token>                   - The id of a authorised user who is member of the channel
        <dm_id> (integer)         - The id of a dm
        <start> (integer)         - <index which indicate the start point of message>

    Exceptions:
        InputError  - Occurs when dm ID is not valid, start is greater than the total number of messages
        AccessError - Occurs when given token does not refer to a valid user id
        AccessError - Occurs when authorised user is not a member of dm with dm_id

    Return Value:
        Returns a dictionary of all messages details and the start and end points

    
'''
def dm_messages_v1(token, dm_id, start):
    # check whether the input token refer to a valid user id
    auth_session_verify(token)
    # read channel data
    pin_data = read_info('pin_data.json')
    react_data = read_info("react_data.json")
    dm_data = read_info('dm_data.json')
    dm_message_data = read_info('dm_message_data.json')
    # given dm_id is an invalid id
    u_id = auth_token_to_id(token)
    if str(dm_id) not in dm_data:
        raise InputError('Input dm id is invalid!')
    # check if the authorised user is a member of DM - AccessError
    if (check_participate(token, dm_id) == False):
        raise AccessError("The authorised user is not a member of DM!")

    if str(dm_id) not in dm_message_data.keys():
        dm_message_len = 0
    else:
        dm_message_len = len(dm_message_data[str(dm_id)])
    # start is greater than total number of messages in the dm
    if start > dm_message_len:
        raise InputError("start is greater than the total number of messages in the dm!")
    # main part
    message_return = {}
    message_return['messages'] = []

    if start == dm_message_len:
        message_return['start'] = start
        message_return['end'] = -1
        return message_return
    # change end if reach the least recent messages
    end = start + 50
    if end >= dm_message_len:
        for index in range(start, dm_message_len):
            # message basic detail
            return_dict = dm_message_data[str(dm_id)][index]
            message_id = dm_message_data[str(dm_id)][index]['message_id']
            # message pin detail
            return_dict['is_pinned'] = pin_data[str(message_id)]
            # message react detail
            react_list = create_reacts_list(react_data, u_id, message_id)
            return_dict['reacts'] = react_list
            message_return['messages'].append(return_dict)
        end = -1
    else:
        for index in range(start, end):
            return_dict = dm_message_data[str(dm_id)][index]
            message_id = dm_message_data[str(dm_id)][index]['message_id']
            return_dict['is_pinned'] = pin_data[str(message_id)]
            react_list = create_reacts_list(react_data, u_id, message_id)
            return_dict['reacts'] = react_list
            message_return['messages'].append(return_dict)
    message_return['start'] = start
    message_return['end'] = end

    return message_return



# helper functions
'''
    Create a dictionary of user details with a valid user_id

    Arguments:
        <user_id> (integer)                   - The user id 

    Return Value:
        Returns a dictionary of user details with a valid user_id

    
'''
# get the user details
def create_user_detail(user_id):

    user_id_to_email = read_info("auth_user_id_to_email")
    
    users_data = read_info("auth_users_data")
    
    user_deets = {}

    email = user_id_to_email[str(user_id)]
    user_deets['name_first'] = users_data[email]['first_name']
    user_deets['name_last'] = users_data[email]['last_name']
    user_deets['email'] = email
    user_deets['handle'] = users_data[email]['handle']
    user_deets['u_id'] = users_data[email]['auth_user_id']

    return user_deets


'''
    Check if the user is the member of the dm with dm_id

    Arguments:
        <token>                        - The user id of an authorised user
        <dm_id> (integer)              - The id of a dm 

    Return Value:
        Returns bool to determine if the user is the member of the dm
  
'''
def check_participate(token, dm_id):
    dm_data = read_info('dm_data.json')
    # test if is one of the members
    auth_user_id = auth_token_to_id(token)
    for i in range(0,len(dm_data[str(dm_id)]['dm_members'])):
        if dm_data[str(dm_id)]['dm_members'][i]['u_id'] == auth_user_id:
            return True
    return False

def dm_user_stats_delete(user_id):
    '''
    Update the user statistics

    Arguments:
        <user_id>

    Return Value:
        N/A
    '''
    user_stats_data = read_info('user_stats_data.json')
    for users in user_stats_data:
        if users == str(user_id):
            create_time = datetime.utcnow()
            time_finish = int(create_time.replace(tzinfo=timezone.utc).timestamp())
            num = user_stats_data[str(user_id)]["dms_joined"][-1]["num_dms_joined"] - 1
            append_dic = {
                "num_dms_joined" : num,
                "time_stamp" : time_finish
            }
            user_stats_data[str(user_id)]["dms_joined"].append(append_dic)
    write_info('user_stats_data.json', user_stats_data)

def dm_user_stats_add(user_id):
    '''
    Update the user statistics

    Arguments:
        <user_id>

    Return Value:
        N/A
    '''
    user_stats_data = read_info('user_stats_data.json')
    for users in user_stats_data:
        if users == str(user_id):
            create_time = datetime.utcnow()
            time_finish = int(create_time.replace(tzinfo=timezone.utc).timestamp())
            num = user_stats_data[str(user_id)]["dms_joined"][-1]["num_dms_joined"] + 1
            append_dic = {
                "num_dms_joined" : num,
                "time_stamp" : time_finish
            }
            user_stats_data[str(user_id)]["dms_joined"].append(append_dic)
    write_info('user_stats_data.json', user_stats_data)

def dm_dreams_stats_add(user_id):
    '''
    Update the user statistics

    Arguments:
        <user_id>

    Return Value:
        N/A
    '''
    dreams_stats_data = read_info('dreams_stats_data.json')
    create_time = datetime.utcnow()
    time_finish = int(create_time.replace(tzinfo=timezone.utc).timestamp())
    num = dreams_stats_data["dms_exist"][-1]["num_dms_exist"] + 1
    append_dic = {
        "num_dms_exist" : num,
        "time_stamp" : time_finish
    }
    dreams_stats_data["dms_exist"].append(append_dic)
    write_info('dreams_stats_data.json', dreams_stats_data)

def dm_dreams_stats_delete(user_id):
    '''
    Update the user statistics

    Arguments:
        <user_id>

    Return Value:
        N/A
    '''
    dreams_stats_data = read_info('dreams_stats_data.json')
    create_time = datetime.utcnow()
    time_finish = int(create_time.replace(tzinfo=timezone.utc).timestamp())
    num = dreams_stats_data["dms_exist"][-1]["num_dms_exist"] - 1
    append_dic = {
        "num_dms_exist" : num,
        "time_stamp" : time_finish
    }
    dreams_stats_data["dms_exist"].append(append_dic)
    write_info('dreams_stats_data.json', dreams_stats_data)

