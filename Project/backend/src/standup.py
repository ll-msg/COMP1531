from src.channel_data import channel_data
import src.auth_data as auth_data
from src.auth import auth_session_verify, auth_token_to_id 
from src.message_data import message_data
from src.message import message_send_v2
import src.notifications
from src.error import InputError
from src.error import AccessError
from src.information_io import write_info
from src.read_json import read_info
from datetime import timezone, datetime, timedelta
from threading import Thread
import threading
import time



def standup_start_v1(token, channel_id, length):
    '''
    standup_start_v1 will start the standup period whereby for the next "length" seconds if someone calls "standup_send" with a message, it will be packged and sent after specific length of time.
    Arguments:
        <token>                        - The code which can be decoded to find the user id
        <channel_id> (integer)         - The idea of the channel the user starts standup in
        <length> (integer)             - The length of time of the standup period

    Exceptions:
        InputError   - Occurs when the channel_id does not refer to a valid channel.
        InputError   - Occurs when an active standup is currently running in the channel
        AccessError  - Occurs when the authorised user is not already a member of the channel

    Return Value:
        Returns a unix timestamp (time_finish) which is the finish time of the standup
    '''
    # read channel data
    channel_data = read_info('channel_data.json')
    # read standup data
    standup_data = read_info('standup_data.json')

    # check if the given channel_id is a valid channel
    if str(channel_id) not in channel_data:
        raise InputError(description='Input channel id is invalid!')
    # check if the authirised user is not already a member of the channel
    if check_participate(token, channel_id) == False:
        raise AccessError(description="The authorised user is not a member of the channel!")
    # check if an active standup is currently running in the channel
    if standup_data[str(channel_id)]['is_active'] == True:
        raise InputError(description='There is already a standup here!')


    is_active = True
    # change the token to user id
    auth_user_id = auth_token_to_id(token)
    # create the timestamp of the finish time
    create_time = datetime.utcnow() + timedelta(seconds=length)
    time_finish = int(create_time.replace(tzinfo=timezone.utc).timestamp())
    standup_data[str(channel_id)]['is_active'] = is_active
    standup_data[str(channel_id)]['length'] = length
    standup_data[str(channel_id)]['time_finish'] = time_finish
    standup_data[str(channel_id)]['creator'] = auth_user_id
    standup_data[str(channel_id)]['message'] = []
    
    
    write_info("standup_data.json", standup_data)
    
    cancel = threading.Timer(length, send_message, [token, channel_id])
    cancel.start()
    
    return {"time_finish": time_finish}


def standup_active_v1(token, channel_id):
    '''
    standup_active_v1 will return if a standup is active in the channel and the time it finishes
    Arguments:
        <token>                        - The code which can be decoded to find the user id
        <channel_id> (integer)         - The idea of the channel the user starts standup in

    Exceptions:
        InputError   - Occurs when the channel_id does not refer to a valid channel.

    Return Value:
        Returns a bool(is_active) and a unix timestamp (time_finish) which is the finish time of the standup
    '''
    # check whether the input token refer to a valid user id - 
    auth_session_verify(token)
    # read channel data
    channel_data = read_info('channel_data.json')
    # read standup data
    standup_data = read_info('standup_data.json')
    # check if the given channel_id is a valid channel
    if str(channel_id) not in channel_data:
        raise InputError(description='Input channel id is invalid!')
    
    # main part
    is_active = standup_data[str(channel_id)]['is_active']
    time_finish = standup_data[str(channel_id)]['time_finish']

    if not is_active:
        return {
        "is_active": is_active,
        "time_finish": None,
    }
 
    standup = {
        "is_active": is_active,
        "time_finish": time_finish
    }

    return standup


def standup_send_v1(token, channel_id, message):
    '''
    standup_send_v1 will send a message to the standup queue, assume the standup is active
    Arguments:
        <token>                        - The code which can be decoded to find the user id
        <channel_id> (integer)         - The idea of the channel the user starts standup in
        <message> (string)             - The message sent to get buffered in the standup queue

    Exceptions:
        InputError   - Occurs when the channel_id does not refer to a valid channel.
        InputError   - Occurs when the message is more than 1000 characters (not including the username and colon)
        InputError   - Occurs when an active standup is not currently running in this channel
        AccessError  - Occurs when the authorised user is not a member of the channel that the message is within

    Return Value:
        Returns an empty dictionary
    '''
    # read channel data
    channel_data = read_info('channel_data.json')
    # read standup data
    standup_data = read_info('standup_data.json')
    # change the token to user id
    auth_user_id = auth_token_to_id(token)
    # check if the given channel_id is a valid channel
    if str(channel_id) not in channel_data:
        raise InputError(description='Input channel id is invalid!')
    # check if the message is more than 1000 characters - /* contains the user name? */
    if (len(message) >= 1000):
        raise InputError(description='The message is more than 1000 characters!')
    # check if the authorised user is not a member of the channel
    if (check_participate(token, channel_id) == False):
        raise AccessError(description="The authorised user is not a member of the channel!")
    # check if there is an active standup currently running in the channel
    if (standup_data[str(channel_id)]['is_active'] == False):
        raise InputError(description='There is no active standup!')


    # update message in standup data 
    message_dict = {'u_id': auth_user_id, 'message' : message}
    standup_data[str(channel_id)]['message'].append(message_dict)

    write_info("standup_data.json", standup_data)

    return {}



# helper functions
def check_participate(token, channel_id):
    '''
    Check if the user is the member of the channel with channel_id

    Arguments:
        <token>                             - The user id of an authorised user
        <channel_id> (integer)              - The id of a channel

    Return Value:
        Returns bool to determine if the user is the member of the channel
  
    '''
    channel_data = read_info('channel_data.json')
    # test if is one of the members
    auth_user_id = auth_token_to_id(token)
    for i in range(0,len(channel_data[str(channel_id)]['channel_members'])):
        if channel_data[str(channel_id)]['channel_members'][i]['u_id'] == auth_user_id:
            return True
    return False

def print_message(channel_id):
    '''
    Print all the message in the standup data

    Arguments:
        <channel_id> (integer)              - The id of a channel

    Return Value:
        Return a list with all the messages
  
    '''
    standup_data = read_info('standup_data.json')

    message_list = []
    standup_msg = ""
    for messages in standup_data[str(channel_id)]['message']:
        if (messages['message'] != ""):
            u_id = messages['u_id']
            standup_msg = id_to_handle(u_id) + ": " + messages['message']
            message_list.append(standup_msg)
    standup_message = "\n".join(message_list)
    return standup_message

def id_to_handle(user_id):
    '''
    Find user handle through a known user id

    Arguments:
        <user_id>                             - The user id of an authorised user

    Return Value:
        Return the handle of the user
  
    '''
    handle = ""
    users_data = read_info("auth_users_data")
    user_id_to_email = read_info("auth_user_id_to_email")
    email = user_id_to_email[str(user_id)]

    for emails in users_data:
        if emails == email:
            handle = users_data[emails]["handle"]
    return handle

def send_message(token, channel_id):
    # read standup data
    standup_data = read_info('standup_data.json')
    message = print_message(channel_id)
    message_send_v2(token, channel_id, message)
    standup_data[str(channel_id)]['is_active'] = False
    write_info('standup_data.json', standup_data)
