from src.channel_data import channel_data
# import src.auth_data as auth_data
import src.notifications
from src.message_data import message_data
from src.error import InputError
from src.error import AccessError
from src.information_io import write_info
from src.auth import auth_session_verify, auth_token_to_id
from src.admin import admin_verify
import src.admin_data as admin
from src.read_json import read_info
import src.information_io as information_io
from src.user_stats_data import user_stats_data
from datetime import timezone, datetime, timedelta



def channel_invite_v2(token, channel_id, u_id):
    '''
    channel_invite_v2 will invite a user to a channel. If the user is valid, the channel id is valid, and the person who is inviting has a valid id, the user will be automatically added to the channel.

    Arguments:
        <token> (string)          - A tamper-proof string belonging to a valid id encryped with JWT
        <channel_id> (integer)    - The idea of the channel the user is being invited to
        <u_id> (integer)          - The user id of a person who is not a member of the channel but is being invited in
        ...

    Exceptions:
        InputError  - Occurs when the channel_id does not refer to a valid channel.
        InputError  - Occurs when the u_id does not refer to a valid user
        AccessError - Occurs when the authorised user is not already a member of the channel

    Return Value:
        Returns an empty dictionary

    '''

    users_data = read_info("auth_users_data")
    
    user_id_to_email = read_info("auth_user_id_to_email")
    
    # If token is not a valid id
    auth_session_verify(token)
    # read in channel data
    channel_data = read_info("channel_data.json")
    # Check if channel is valid
    check_channel(channel_id)
    # Convert token to user_id
    auth_user_id = auth_token_to_id(token)
    if not check_participate(auth_user_id, channel_id):
        raise AccessError('Authorised user is not a member of the channel!')
    #check if user_id is a participant of this channel 
    #assumption: if the user is already a participant of this channel, the function will do nothing
    if check_participate(u_id, channel_id):
        return {}
    #check if u_id refers to a valid user 
    valid = 0
    for email in users_data:
        if users_data[email]['auth_user_id'] == u_id:
            valid = 1
            break
    if valid == 0:
        raise InputError('User ID does not refer to a valid user!')
    #add the user with u_id to the channel members list in channel_data
    channel_data[str(channel_id)]['channel_members'].append({'u_id': u_id})
    write_info("channel_data.json", channel_data)
    
    # add notification
    src.notifications.add_join_notification(u_id, users_data[
        user_id_to_email[str(auth_user_id)]
    ]['handle'], -1, channel_id)

    channel_user_stats_add(u_id)
    
    return {
    }
    
def channel_join_v2(token, channel_id):
    '''
    Given a channel_id of a channel that the authorised user can join, adds them to that channel

    Arguments:
        <token> (string)          - A tamper-proof string belonging to a valid id encryped with JWT
        <channel_id> (integer)    - The id of a channel as a target to be joined by the input user
        ...

    Exceptions:
        InputError  - Occurs when channel ID is not a valid channel
        AccessError - Occurs when channel_id refers to a channel that is private(when the authorised user is not a global owner)

    Return Value:
        Returns an empty dictionary

    '''
    # If token is not a valid id
    auth_session_verify(token)
    channel_data = read_info("channel_data.json")
    # Check whether the input channel is invalid
    check_channel(channel_id)
    # Convert token to u_id
    u_id = auth_token_to_id(token)
    #check whtether auth_user_id is already in the channel
    #Assumption here, if the user is already in target channel, do nothing
    participate = check_participate(u_id, channel_id)
    if participate:
        return
    
    #the user is a global owner
    if admin_verify(token):
        channel_data[str(channel_id)]['channel_members'].append({'u_id' : u_id})
    #the user is a member of Dream, check the publicity
    else:
        if channel_data[str(channel_id)]['publicity']:
            channel_data[str(channel_id)]['channel_members'].append({'u_id' : u_id})
        else:
            raise AccessError('Can not join in the private chennel')
    write_info("channel_data.json", channel_data)
    
    channel_user_stats_add(u_id)
    
    return {
    }

def channel_messages_v2(token, channel_id, start):
    '''
    Use users who are members of this channel, the channel name and the starting point of the chat message are used as input
    and return the all chat messages, the start point of message and the last end point of the message

    Arguments:
        <token> (string)          - A tamper-proof string belonging to a valid id encryped with JWT
        <channel_id> (integer)    - The id of a channel that has been created
        <start> (integer) - <index which indicate the start point of message>

    Exceptions:
        InputError  - Occurs when channel ID is not valid, start is greater than the total number of messages
        AccessError - Occurs when authorised user is not a member of channel with channel_id

    Return Value:
        Returns a dictionary of all messages details and the start and end points

    
    '''
    # If token is not a valid id
    auth_session_verify(token)
    #read in message_data from message_data.json
    message_data = read_info("message_data.json")
    # read in pin_data and react_data
    pin_data = read_info('pin_data.json')
    react_data = read_info("react_data.json")
    #check whether channel ID is a valid channel
    check_channel(channel_id)
    # Convert token to u_id
    u_id = auth_token_to_id(token)
    #check whether the user is part of the channel
    participate = check_participate(u_id, channel_id)
    if not participate:
        raise AccessError("User is not a member of the channel!")
    #check the length of the message
    if str(channel_id) not in message_data.keys():
        message_len = 0
    else:
        message_len = len(message_data[str(channel_id)])
    if start > message_len:
        raise InputError("Start is greater than the total number of messages in the channel!")
    message_return = {}
    message_return['messages'] = []
    if start == message_len:
        message_return['start'] = start
        message_return['end'] = -1
        return message_return
    #change end if reach the  least recent messages
    end = start + 50
    if end >= message_len:
        for index in range(start, message_len):
            # message basic detail
            return_dict = message_data[str(channel_id)][index]
            message_id = message_data[str(channel_id)][index]['message_id']
            # message pin detail
            return_dict['is_pinned'] = pin_data[str(message_id)]
            # message react detail
            react_list = create_reacts_list(react_data, u_id, message_id)
            return_dict['reacts'] = react_list
            message_return['messages'].append(return_dict)
        end = -1
    else:
        for index in range(start, end):
            return_dict = message_data[str(channel_id)][index]
            message_id = message_data[str(channel_id)][index]['message_id']
            return_dict['is_pinned'] = pin_data[str(message_id)]
            react_list = create_reacts_list(react_data, u_id, message_id)
            return_dict['reacts'] = react_list
            message_return['messages'].append(return_dict)
    message_return['start'] = start
    message_return['end'] = end
    return message_return

def channel_details_v2(token, channel_id):
    '''
    channel_details_v1 will, when given a valid auth_user_id and channel_id, return all the details about the channel; it's name, it's current owners and all of its members.

    Arguments:
        <auth_user_id> (integer)    - The user id of an authorised user who is a member of the channel
        <channel_id> (integer)    - The idea of the channel the user is being invited to

        ...

    Exceptions:
        InputError  - Occurs when the channel ID is not a valid channel
        AccessError - Occurs when the authorised user is not a member of channel with channel_id

    Return Value:
        Returns a dictionary (channel_deets) with all the details previously stated.

    '''
    # If token is not a valid id
    auth_session_verify(token)
    channel_data = read_info("channel_data.json")
    #check if the given channel_id is a valid channel, if not, raise InputError
    check_channel(channel_id)
    # Convert token to u_id
    u_id = auth_token_to_id(token)
    #check if the given auth_user_id is a member of the channel
    if not check_participate(u_id, channel_id):
        raise AccessError('Authorised user is not a member of channel!')
    
    #creates a dictionary for the channel details
    channel_deets = {
        'name': 'to_be_named',
        'owner_members': [],
        'all_members': [],
    }
    
    #checks the channel in channel_data to get the necessary info
    channel_deets['name'] = channel_data[str(channel_id)]['name']
    
    #sets up a loop to add all owners and their details into channel_deets
    
    for j in range(0,len(channel_data[str(channel_id)]['channel_owners'])):
        owner_id = channel_data[str(channel_id)]['channel_owners'][j]['u_id']
        channel_deets['owner_members'].append(create_user_detail(owner_id))
        
    #sets up a loop to add all members and their details into channel_deets
    
    for k in range(0, len(channel_data[str(channel_id)]['channel_members'])):
        user_id = channel_data[str(channel_id)]['channel_members'][k]['u_id']
        channel_deets['all_members'].append(create_user_detail(user_id))  
    return channel_deets

def channel_addowner_v1(token, channel_id, u_id):
    """
    channel_addowner_v1 will make the user with user id 'u_id' an owner of the channel with channel id 'channel_id'

    Arguments:
        <token> (string)          - A tamper-proof string belonging to a valid id encryped with JWT
        <channel_id> (integer)    - The id of the channel the user will become an owner of
        <u_id> (integer)          - The id of the user to become an owner 

        ...

    Exceptions:
        InputError  - Occurs when the channel ID is not a valid channel
                    - Occurs when the user with 'u_id' is already an owner of the channel
        AccessError - Occurs when the authorised user is not a global owner or owner of the channel

    Return Value:
        Returns an empty dictionary

    """
    # If token is not a valid id
    auth_session_verify(token)
    # read in channel_data from channel_data.json
    channel_data = read_info("channel_data.json")
    # check if the given channel_id is a valid channel
    check_channel(channel_id)

    # check if the authorised user is a global owner or channel owner
    if admin_verify(token) == False:
        auth_user_id = auth_token_to_id(token)
        if check_owner(auth_user_id, channel_id) == False:
            raise AccessError("Authorised user is not a global or channel owner!")

    # check if the user with 'u_id' is already a member/owner of the channel with 'channel_id'

    if check_participate(u_id, channel_id) == True: #Is a member
        if check_owner(u_id, channel_id) == True: #Also an owner
            raise InputError("User is already an owner of this channel!")
        #Not an owner but already a member so make him an owner
        else:
            channel_data[str(channel_id)]['channel_owners'].append({'u_id' : u_id})
    else:
        # Not a member or owner of the channel, add him as both.
        channel_data[str(channel_id)]['channel_owners'].append({'u_id' : u_id})
        channel_data[str(channel_id)]['channel_members'].append({'u_id' : u_id})
        # Update channel_data and dump to channel_data.json
    write_info("channel_data.json", channel_data)
    return {

    }
def channel_removeowner_v1(token, channel_id, u_id):
    """
    channel_addowner_v1 will remove the user with user id 'u_id' as an owner of the channel with channel id 'channel_id'

    Arguments:
        <token> (string)          - A tamper-proof string belonging to a valid id encryped with JWT
        <channel_id> (integer)    - The id of the channel the user will become an owner of
        <u_id> (integer)          - The id of the user to become an owner 

        ...

    Exceptions:
        InputError  - Occurs when the channel ID is not a valid channel
                    - Occurs when the user with 'u_id' is not an owner of the channel
                    - Occurs when the user is currently the only owner
        AccessError - Occurs when the authorised user is not a global owner or owner of the channel

    Return Value:
        Returns an empty dictionary

    """
    # If token is not a valid id
    auth_session_verify(token)
    # read in channel_data from channel_data.json
    channel_data = read_info("channel_data.json")
    # check if the given channel_id is a valid channel
    check_channel(channel_id)
    

    # check if the authorised user is a global owner or channel owner
    if admin_verify(token) == False:
        auth_user_id = auth_token_to_id(token)
        if check_owner(auth_user_id, channel_id) == False:
            raise AccessError("Authorised user is not a global or channel owner!")

    # check if user is an owner of channel
    if check_owner(u_id, channel_id) == False:
        raise InputError("User is not an owner of this channel!")
    
    # check if user is the only owner of channel
    if len(channel_data[str(channel_id)]['channel_owners']) == 1:
        raise InputError("User is the only owner of this channel!")
    
    # remove user as an owner
    channel_data[str(channel_id)]['channel_owners'].remove({'u_id' : u_id})
    # Update channel_data and dump to channel_data.json
    write_info("channel_data.json", channel_data)
    return {

    }
    
def channel_leave_v1(token, channel_id):
    """
    channel_leave_v1 will remove the user with user id 'u_id' from the channel with channel id 'channel_id'

    Arguments:
        <token> (string)          - A tamper-proof string belonging to a valid id encryped with JWT
        <channel_id> (integer)    - The id of the channel the user will become an owner of

        ...

    Exceptions:
        InputError  - Occurs when the channel ID is not a valid channel
        AccessError - Occurs when the authorised user is not a member of channel with 'channel_id'

    Return Value:
        Returns an empty dictionary

    """

    # If token is not a valid id
    auth_session_verify(token)
    # read in channel_data from channel_data.json
    channel_data = information_io.read_info("channel_data.json")
    
    # check if the given channel_id is a valid channel
    check_channel(channel_id)

    # check if user is a member of the channel
    u_id = auth_token_to_id(token)
    if check_participate(u_id, channel_id) == False:
        raise AccessError("User is not a member of channel!")
    
    channel_data[str(channel_id)]['channel_members'].remove({'u_id':u_id})
    
    write_info("channel_data.json", channel_data)
    
    channel_user_stats_delete(u_id)

    return {
    }




def check_participate(auth_user_id, channel_id):
    '''
    check whether the input user is a member of the input channel id
    Arguments:
        auth_user_id (int)
        channel_id (int)
    Return Value:
        True (bool) if the user is a member of the channel
        False (bool) if the user is not a memeber
    '''
    # read in channel_data.json file
    channel_data = read_info("channel_data.json")
    # unlock the code below after using json
    # channel_data = read_info('channel_data.json')
    for i in range(0,len(channel_data[str(channel_id)]['channel_members'])):
        if channel_data[str(channel_id)]['channel_members'][i]['u_id'] == auth_user_id:
            return True
    return False


def check_channel(channel_id):
    '''
    check whether the input channel is invalid
    Arguments:
        channel_id (int)
    Return Value:
        raise InputError if the channel_id is invalid

    '''
    # read in channel_data.json file
    channel_data = read_info("channel_data.json")
    channel_id = str(channel_id)
    if channel_id not in channel_data:
        raise InputError('Input channel id is invalid!')
   
#generates a dictionary of all the user details     
def create_user_detail(user_id):
    users_data = read_info("auth_users_data")
    
    user_id_to_email = read_info("auth_user_id_to_email")
    
    user_deets = {}
    email = user_id_to_email[str(user_id)]
    user_deets['name_first'] = users_data[email]['first_name']
    user_deets['name_last'] = users_data[email]['last_name']
    user_deets['email'] = email
    user_deets['u_id'] = users_data[email]['auth_user_id']
    user_deets['handle'] = users_data[email]['handle']
    return user_deets

#check whether the auth_user_id is an owner of input channel
def check_owner(auth_user_id, channel_id):
    channel_data = read_info("channel_data.json")
    # unlock the code below after using json
    # channel_data = read_info('channel_data.json')
    for i in range(0,len(channel_data[str(channel_id)]['channel_owners'])):
        if channel_data[str(channel_id)]['channel_members'][i]['u_id'] == auth_user_id:
            return True
    return False



def channel_user_stats_delete(user_id):
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
            num = user_stats_data[str(user_id)]["channels_joined"][-1]["num_channels_joined"] - 1
            append_dic = {
                "num_channels_joined" : num,
                "time_stamp" : time_finish
            }
            user_stats_data[str(user_id)]["channels_joined"].append(append_dic)
    write_info('user_stats_data.json', user_stats_data)


def channel_user_stats_add(user_id):
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
            num = user_stats_data[str(user_id)]["channels_joined"][-1]["num_channels_joined"] + 1
            append_dic = {
                "num_channels_joined" : num,
                "time_stamp" : time_finish
            }
            user_stats_data[str(user_id)]["channels_joined"].append(append_dic)
    write_info('user_stats_data.json', user_stats_data)
def create_reacts_list(react_data, user_id, message_id):
    '''
    create a list of dict contains the reacts detail of the given message
    Arguments:
        react_data (dict)
        user_id (int)
        message_id (int)
    Return Values:
        react_list (list)
    '''
    react_list = []
    for react_id in react_data[str(message_id)]:
        # check whetehr the given user is already in u_ids
        is_react = False
        if user_id in react_data[str(message_id)][react_id]:
            is_react = True
        react_dict = {
            'react_id' : int(react_id),
            'u_ids' : react_data[str(message_id)][react_id],
            'is_this_user_reacted' : is_react,
        }
        react_list.append(react_dict)
    return react_list
