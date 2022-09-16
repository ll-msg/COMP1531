from src.information_io import write_info
from src.error import InputError
from src.error import AccessError
from src.auth import auth_session_verify, auth_token_to_id
from src.admin import admin_verify
import src.notifications
from datetime import timezone, datetime
from src.user_stats_data import user_stats_data
from src.dreams_stats_data import dreams_stats_data
# import src.auth_data as auth_data
from src.read_json import read_info
import threading
import time
from src.notifications import add_tag_notification
def message_send_v2(token, channel_id, message):
    '''
    Send a message from authorised_user to the channel specified by channel_id

    Arguments:
        token       <string>        - a tamper proof string belong to a valid id by using JWT    
        channel_id  <integer>       - the id of an valid channel
        message     <string>        - the string sent by the user with the given token

    Exceptions:
        InputError  - Occurs when message is more than 1000 characters
        AccessError - Occurs when the authorised user has not joined the channel they are trying to post to

    Return Value:
        Returns a dictionary with string 'message_id' as key and integer message_id as value

    '''
    # if token passed in is not a valid id.
    auth_session_verify(token)
    # convert token to user_id
    user_id = auth_token_to_id(token)
    # raise InputError when message is more than 1000 characters
    message_len = len(message)
    check_message_len(message_len)
    # read in data
    # if there is no such json file exist, return empty dic, and update afterwards
    dm_message_data = read_info('dm_message_data.json')
    # if there is no such json file exist, return empty dic, and update afterwards
    message_data = read_info('message_data.json')
    
    # raise AccessError when the authorised user has not joined the channel they are trying to post to
    if not check_channel_participate(user_id, channel_id):
        raise AccessError('User has not joined the channel!')
    # assumption: Message_send funtion doesn't send message with empty string.
    if message == '':
        return {}
    # message notification in channel
    message_notification(user_id, message, True, False, channel_id, -1)
    
    # update message data
    message_id = do_send_message(user_id, channel_id, -1, message, message_data, dm_message_data, True, False)
    return {
        'message_id': message_id,
    }

def message_remove_v1(token, message_id):
    '''
    Given a message_id for a message, this message is removed from the channel/DM

    Arguments:
        token           <string>         - a tamper proof string belong to a valid id by using JWT 
        message_id      <integer>        - a valid message id

    Exceptions:
        InputError  - Occurs when message (based on ID) no longer exists
        AccessError - Occurs when none of the following are true:
            Message with message_id was sent by the authorised user making this request
            The authorised user is an owner of this channel (if it was sent to a channel) or the **Dreams*

    Return Value:
        None
    '''
    # check the token passed in is not a valid id
    auth_session_verify(token)
    # convert token to user_id
    user_id = auth_token_to_id(token)
    # check whether given token belongs to an owner of DREAM, is_global_owner is true if the user is an owner of DREAM
    is_global_owner = admin_verify(token)
    # read in data
    channel_data = read_info('channel_data.json')
    # assumption: The delete function can only be used after dream has sent at least one message
    dm_message_data = read_info('dm_message_data.json')
    message_data = read_info('message_data.json')
    dm_data = read_info('dm_data.json')
    # find input message with the given message id and modify it
    modify_message(True, False, message_data, dm_message_data, message_id, "", is_global_owner, user_id, channel_data, dm_data)
    message_dreams_stats_delete(user_id)
    return {
    }

def message_edit_v2(token, message_id, message):
    '''
    Given a message, update its text with new text. If the new message is an empty string, the message is deleted.
    
    Arguments:
        token           <string>         - a tamper proof string belong to a valid id by using JWT 
        message_id      <integer>        - a valid message id
        message         <string>         - string of edited message   

    Exceptions:
        InputError  - message_id refers to a deleted message
                    - Length of message is over 1000 characters
        
        AccessError - Occurs when none of the following are true:
            Message with message_id was sent by the authorised user making this request
            The authorised user is an owner of this channel (if it was sent to a channel) or the **Dreams*

    Return Value:
        None
    '''
     # check the token passed in is not a valid id
    auth_session_verify(token)
    # convert token to user_id
    user_id = auth_token_to_id(token)
    # check whether given token belongs to an owner of DREAM, is_global_owner is true if the user is an owner of DREAM
    is_global_owner = admin_verify(token)
    # raise InputError when message is more than 1000 characters
    message_len = len(message)
    check_message_len(message_len)
    # get data file
    channel_data = read_info('channel_data.json')
    dm_message_data = read_info('dm_message_data.json')
    message_data = read_info('message_data.json')
    dm_data = read_info('dm_data.json')
    # check if the message str is empty, if this message is empty, remove_message is true, and we will remove this message
    if message == '':
        is_remove = True
        is_edit = False
    else:
        is_remove = False
        is_edit = True
    # find input message with the given message id and modify it
    modify_message(is_remove, is_edit, message_data, dm_message_data, message_id, message, is_global_owner, user_id, channel_data, dm_data)
    return {
    }

def message_senddm_v1(token, dm_id, message):
    '''
    Send a message from authorised_user to the channel specified by channel_id

    Arguments:
        token       <string>        - a tamper proof string belong to a valid id by using JWT    
        dm_id       <integer>       - the id of a valid dm
        message     <string>        - the string sent by the user with the given token

    Exceptions:
        InputError  - Occurs when message is more than 1000 characters
        AccessError - Occurs when the authorised user is not a member of the DM they are trying to post to

    Return Value:
        Returns a dictionary with string 'message_id' as key and integer message_id as value
    '''
    # check if token passed in is not a valid id.
    auth_session_verify(token)
    # convert token to user_id
    user_id = auth_token_to_id(token)
    # raise InputError when message is more than 1000 characters
    message_len = len(message)
    check_message_len(message_len)
    # if there is no such json file exist, return empty dic, and update afterwards
    dm_message_data = read_info('dm_message_data.json')
    # if there is no such json file exist, return empty dic, and update afterwards
    message_data = read_info('message_data.json')
    
    # raise AccessError when authorised user has not joined the dm they are trying to post message to
    if not check_dm_participate(user_id, dm_id):
        raise AccessError('User has not joined the dm!')
    # assumption: Message_send funtion doesn't send message with empty string.
    if message == '':
        return {}
    # message notification in DM
    message_notification(user_id, message, False, True, -1, dm_id)
    # update message data
    message_id = do_send_message(user_id, -1, dm_id, message, message_data, dm_message_data, False, True)

    return {
        'message_id': message_id,
    }
def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    og_message_id is the original message. channel_id is the channel that the message is being shared to, and is -1 if it is being sent to a DM. dm_id is the DM that the message is being shared to, 
    and is -1 if it is being sent to a channel. message is the optional message in addition to the shared message, and will be an empty string '' if no message is given

    Arguments:
        token           <string>        - a tamper proof string belong to a valid id by using JWT
        og_message_id   <integer>       - the origin message id which will be shared
        dm_id           <integer>       - the id of a valid dm
        channel_id      <integer>       - the id of a valid channel
        message         <string>        - the string sent by the user with the given token

    Exceptions:
        AccessError - Occurs when the authorised user has not joined the channel or DM they are trying to share the message to

    Return Value:
        Returns a dictionary with string 'message_id' as key and integer message_id as value
    '''
    # if token passed in is not a valid id.
    auth_session_verify(token)
    # convert token to user_id
    user_id = auth_token_to_id(token)
    # read in data
    dm_message_data = read_info('dm_message_data.json')
    message_data = read_info('message_data.json')
    # find the og_message
    og_message = ''
    message_location = find_message(og_message_id, message_data, dm_message_data)
    # message is found in channels
    if message_location['in_channel']:
        channel = message_location['channel_id']
        index = message_location['index']
        og_message = message_data[channel][index]['message']
    # message is found in dms
    if message_location['in_dm']:
        dm = message_location['dm_id']
        index = message_location['index']
        og_message = dm_message_data[dm][index]['message']
    format_og_message = '--' + og_message
    # check where this message is shared to

    # send to dm
    sent_message = message + format_og_message
    if channel_id == -1:
        # check if the input user joined in that dm
        if not check_dm_participate(user_id, dm_id):
            raise AccessError('User has not joined the dm!')
        # message notification in DM
        message_notification(user_id, message, False, True, -1, dm_id)
        message_id = do_send_message(user_id, -1, dm_id, sent_message, message_data, dm_message_data, False, True)

    # send to channel
    if dm_id == -1:
        #check if the input user joined in that channel
        if not check_channel_participate(user_id, channel_id):
            raise AccessError('User has not joined the channel!')
        # message notification in channel
        message_notification(user_id, message, True, False, channel_id, -1)
        message_id = do_send_message(user_id, channel_id, -1, sent_message, message_data, dm_message_data, True, False)
    return {
        'shared_message_id' : message_id
    }

def message_react_v1(token, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, add a "react" to that particular message
    Arguments:
        token                   <string>            - a tamper proof string belong to a valid id by using JWT
        message_id              <int>               - the id of a valid channel
        react_id                <int>               - the id of a valid reaction
    Exceptions:
        InputError  -   message_id is not a valid message within a channel or DM that the authorised user has joined
                    -   react_id is not a valid React ID. The only valid react ID the frontend has is 1
                    -   Message with ID message_id already contains an active React with ID react_id from the authorised user
        AccessError -   token is invalid
                    -   The authorised user is not a member of the channel or DM that the message is within
    Return value:
        empty dict
    '''
    # check token passed in is not a valid id.
    auth_session_verify(token)
    # convert token to user_id
    user_id = auth_token_to_id(token)
    # check the validation of react_id
    check_react_id(react_id)
    # read in data
    react_data = read_info("react_data.json")
    message_data = read_info('message_data.json')
    dm_message_data = read_info('dm_message_data.json')
    # check whether the input message_id is valid
    message_location = find_message(message_id, message_data, dm_message_data)
    if message_location == False:
        raise InputError('Input message id is not valid!')
    # check whether auth user is alredy in the users list of react_id
    if check_react_list(user_id, react_id, message_id, react_data):
        raise InputError('You have already reacted to this message with this type of reaction!')
    # check whether the user is in the same channel or dm of the input message
    if message_location['in_channel']:
        if not check_channel_participate(user_id, int(message_location['channel_id'])):
            raise AccessError('User is not a memebr of the channel the message is within!')
    if message_location['in_dm']:
        if not check_dm_participate(user_id, int(message_location['dm_id'])):
            raise AccessError('User is not a memebr of the dm the message is within!')
    # append the user_id to the users list of input react_id of input message
    if len(react_data[str(message_id)]) == 0:
        react_data[str(message_id)][str(react_id)] = []
    react_data[str(message_id)][str(react_id)].append(user_id)
    # update the json file
    write_info("react_data.json", react_data)
    return {}

def message_unreact_v1(token, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, remove a "react" to that particular message
    Arguments:
        token                   <string>            - a tamper proof string belong to a valid id by using JWT
        message_id              <int>               - the id of a valid channel
        react_id                <int>               - the id of a valid reaction
    Exceptions:
        InputError  -   message_id is not a valid message within a channel or DM that the authorised user has joined
                    -   react_id is not a valid React ID. The only valid react ID the frontend has is 1
                    -   Message with ID message_id does not contain an active React with ID react_id from the authorised user
        AccessError -   token is invalid
                    -   The authorised user is not a member of the channel or DM that the message is within
    Return value:
        empty dict
    '''
    # check token passed in is not a valid id.
    auth_session_verify(token)
    # convert token to user_id
    user_id = auth_token_to_id(token)
    # check the validation of react_id
    check_react_id(react_id)
    # read in data
    react_data = read_info("react_data.json")
    message_data = read_info('message_data.json')
    dm_message_data = read_info('dm_message_data.json')
    # check whether the input message_id is valid
    message_location = find_message(message_id, message_data, dm_message_data)
    if message_location == False:
        raise InputError('Input message id is not valid!')
    # check whether the user is in the same channel or dm of the input message
    if message_location['in_channel']:
        if not check_channel_participate(user_id, int(message_location['channel_id'])):
            raise AccessError('User is not a memebr of the channel the message is within!')
    if message_location['in_dm']:
        if not check_dm_participate(user_id, int(message_location['dm_id'])):
            raise AccessError('User is not a memebr of the dm the message is within!')
    # check whether auth user is alredy in the users list of react_id         
    if not check_react_list(user_id, react_id, message_id, react_data):
        raise InputError('You havent reacted to this message with this type of reaction!')
    # delete the input user_id in the users list of react_id of input message
    react_data[str(message_id)][str(react_id)].remove(user_id)
    # update the json file
    write_info("react_data.json", react_data)
    return {}

def message_pin_v1(token, message_id):
    '''
    Given a message within a channel or DM, mark it as "pinned" to be given special display treatment by the frontend
    Arguments:
        token                   <string>            - a tamper proof string belong to a valid id by using JWT
        message_id              <int>               - the id of a valid channel
    Exceptions:
        InputError  -   message_id is not a valid message
                    -   Message with ID message_id is already pinned
        AccessError -   token is invalid
                    -   The authorised user is not a member of the channel or DM that the message is within
                    -   The authorised user is not an owner of the channel or DM
    Return value:
        empty dict
    '''
    # check token passed in is not a valid id.
    auth_session_verify(token)
    # convert token to user_id
    user_id = auth_token_to_id(token)
    # check whether given token belongs to an owner of DREAM, is_global_owner is true if the user is an owner of DREAM
    is_global_owner = admin_verify(token)
    # read in data
    message_data = read_info('message_data.json')
    dm_message_data = read_info('dm_message_data.json')
    pin_data = read_info('pin_data.json')
    channel_data = read_info('channel_data.json')
    dm_data = read_info('dm_data.json')
    # check whether the input message_id is valid
    message_location = find_message(message_id, message_data, dm_message_data)
    if message_location == False:
        raise InputError('Input message id is not valid!')
    # check whether the user is in the same channel or dm of the input message
    is_owner = False
    if message_location['in_channel']:
        if not check_channel_participate(user_id, int(message_location['channel_id'])):
            raise AccessError('User is not a memebr of the channel the message is within!')
        # check whether the user is the owner of the channel or of this message is within
        is_owner = check_owner(message_location['channel_id'], '-1', channel_data, dm_data, True, False, user_id)
    if message_location['in_dm']:
        if not check_dm_participate(user_id, int(message_location['dm_id'])):
            raise AccessError('User is not a memebr of the dm the message is within!')
        # check whether the user is the owner of the dm or of this message is within    
        is_owner = check_owner('-1', message_location['dm_id'], channel_data, dm_data, False, True, user_id)
    # check the pinning status of input message
    if pin_data[str(message_id)]:
        raise InputError('Input message is already pinned!')
    if is_global_owner or is_owner:
        # pin the input message
        pin_data[str(message_id)] = True
    else:
        raise AccessError('User does not have permission to pin the message')
    # update json file
    write_info("pin_data.json", pin_data)
    return {}

def message_unpin_v1(token, message_id):
    '''
    Given a message within a channel or DM, remove it's mark as unpinned
    Arguments:
        token                   <string>            - a tamper proof string belong to a valid id by using JWT
        message_id              <int>               - the id of a valid channel
    Exceptions:
        InputError  -   message_id is not a valid message
                    -   Message with ID message_id is already unpinned
        AccessError -   token is invalid
                    -   The authorised user is not a member of the channel or DM that the message is within
                    -   The authorised user is not an owner of the channel or DM
    Return value:
        empty dict
    '''
    # check token passed in is not a valid id.
    auth_session_verify(token)
    # convert token to user_id
    user_id = auth_token_to_id(token)
    # check whether given token belongs to an owner of DREAM, is_global_owner is true if the user is an owner of DREAM
    is_global_owner = admin_verify(token)
    # read in data
    message_data = read_info('message_data.json')
    dm_message_data = read_info('dm_message_data.json')
    pin_data = read_info('pin_data.json')
    channel_data = read_info('channel_data.json')
    dm_data = read_info('dm_data.json')
    # check whether the input message_id is valid
    message_location = find_message(message_id, message_data, dm_message_data)
    if message_location == False:
        raise InputError('Input message id is not valid!')
    # check whether the user is in the same channel or dm of the input message
    is_owner = False
    if message_location['in_channel']:
        if not check_channel_participate(user_id, int(message_location['channel_id'])):
            raise AccessError('User is not a memebr of the channel the message is within!')
        # check whether the user is the owner of the channel or of this message is within
        is_owner = check_owner(message_location['channel_id'], '-1', channel_data, dm_data, True, False, user_id)
    if message_location['in_dm']:
        if not check_dm_participate(user_id, int(message_location['dm_id'])):
            raise AccessError('User is not a memebr of the dm the message is within!')
        # check whether the user is the owner of the dm or of this message is within    
        is_owner = check_owner('-1', message_location['dm_id'], channel_data, dm_data, False, True, user_id)
    # check the pinning status of input message
    if not pin_data[str(message_id)]:
        raise InputError('Input message is already unpinned!')
    if is_global_owner or is_owner:
        # pin the input message
        pin_data[str(message_id)] = False
    else:
        raise AccessError('User does not have permission to pin the message')
    # update json file
    write_info("pin_data.json", pin_data)
    return {}

def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    Send a message from authorised_user to the channel specified by channel_id automatically at a specified time in the future
    Arguments:
        token           <str>       -   A tamper proof string belong to a valid id by using JWT
        channel_id      <int>       -   The id of a channel as a target to be joined by the input user
        message         <str>       -   The string sent by the user with the given token
        time_sent       <int>       -   The preset timestamp of the sent message
    Excepetions:
        InputError      -   Channel ID is not a valid channel
                        -   Message is more than 1000 characters
                        -   Time sent is a time in the past
        AccessError     -   The authorised user has not joined the channel they are trying to post to
                        -   token is invalid
    Return Value:
        message_id      <dict>
    '''
    # check token passed in is not a valid id.
    auth_session_verify(token)
    # convert token to user_id
    user_id = auth_token_to_id(token)
    wait_second = time_sent - create_timestamp()

    # check the input timestamp
    if wait_second < 0:
        raise InputError('Time sent is a time in the past!')
    # Execute after the required time
    time.sleep(wait_second)
    # read in json data
    dm_message_data = read_info('dm_message_data.json')
    message_data = read_info('message_data.json')
    channel_data = read_info('channel_data.json')

    # check the validation of channel_id
    if str(channel_id) not in channel_data:
        raise InputError('Channel ID is not a valid channel!')

    # message len cant greater than 1000
    message_len = len(message)
    check_message_len(message_len)

    # check whetehr the user has joined the input channel
    if not check_channel_participate(user_id, channel_id):
        raise AccessError('User has not joined the channel!')
    # message notification in channel
    message_notification(user_id, message, True, False, channel_id, -1)
    # update message data
    message_id = do_send_message(user_id, channel_id, -1, message, message_data, dm_message_data, True, False)
    return {
        'message_id': message_id,
    }

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    # check token passed in is not a valid id.
    auth_session_verify(token)
    # convert token to user_id
    user_id = auth_token_to_id(token)
    wait_second = time_sent - create_timestamp()

    # check the input timestamp
    if wait_second < 0:
        raise InputError('Time sent is a time in the past!')
    # Execute after the required time
    time.sleep(wait_second)
    # read in json data
    dm_message_data = read_info('dm_message_data.json')
    message_data = read_info('message_data.json')
    dm_data = read_info('dm_data.json')

    # check the validation of channel_id
    if str(dm_id) not in dm_data:
        raise InputError('Channel ID is not a valid channel!')

    # message len cant greater than 1000
    message_len = len(message)
    check_message_len(message_len)

    # check whetehr the user has joined the input channel
    if not check_dm_participate(user_id, dm_id):
        raise AccessError('User has not joined the DM!')
    # message notification in DM
    message_notification(user_id, message, False, True, -1, dm_id)
    # update message data
    message_id = do_send_message(user_id, -1, dm_id, message, message_data, dm_message_data, False, True)
    return {
        'message_id': message_id,
    }


#////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////
#///////////////         help functions          ////////////////////////
#////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////

def check_channel_participate(auth_user_id, channel_id):
    '''
    check whether the input user is a member of the input channel id
    Arguments:
        auth_user_id (int)
        channel_id (int)
    Return Value:
        True (bool) if the user is a member of the channel
        False (bool) if the user is not a memeber
    '''
    channel_data = read_info('channel_data.json')
    for i in range(0,len(channel_data[str(channel_id)]['channel_members'])):
        if channel_data[str(channel_id)]['channel_members'][i]['u_id'] == auth_user_id:
            return True
        
    return False

def check_dm_participate(auth_user_id, dm_id):
    '''
    check whether the input user is a member of the input dm id
    Arguments:
        auth_user_id (int)
        dm_id (int)
    Return Value:
        True (bool) if the user is a member of the dm
        False (bool) if the user is not a memeber
    '''
    dm_data = read_info('dm_data.json')
    for i in range(0,len(dm_data[str(dm_id)]['dm_members'])):
        if dm_data[str(dm_id)]['dm_members'][i]['u_id'] == auth_user_id:
            return True
    return False


def do_send_message(user_id, channel_id, dm_id, message, message_data, dm_message_data, in_channel, in_dm):
    '''
    send input message str to the channel with input channel_id and return the id of that message
    Arguments:
        user_id (int)
        channel_id (int)
        dm_id (int)
        message (str)
        message_data (dict)
        dm_message_data (dict)
        in_channel (bool)
        in_dm (bool)
    Return Value:
        message_id (int)
    '''
    # read in pin_data and react_data
    pin_data = read_info('pin_data.json')
    react_data = read_info("react_data.json")
    # get num of messages and message index
    message_detail = get_new_message_detail(message_data, dm_message_data)
    message_id = message_detail[0]
    incoming_number_of_messages = message_detail[1]
    # update number of messages in dm and channel message data after the message sent
    return_message_num = incoming_number_of_messages + 1
    return_message_index = message_id + 1
    message_data['message_index'] = return_message_index
    dm_message_data['message_index'] = return_message_index
    message_data['number_of_messages'] = return_message_num
    dm_message_data['number_of_messages'] = return_message_num
    # update pin_data and react_data
    pin_data[str(message_id)] = False
    react_data[str(message_id)] = {}
    write_info("pin_data.json", pin_data)
    write_info("react_data.json", react_data)
    # set different data variable based on the input
    if in_channel:
        data = message_data
        target_id = channel_id
    if in_dm:
        data = dm_message_data
        target_id = dm_id
    # Create timestamp
    timestamp = create_timestamp()
    # update message data and dump to messsage_data.json
    if str(target_id) not in data.keys():
        data[str(target_id)] = []
    message_dic = {
        'message_id' : message_id,
        'u_id' : user_id,
        'message': message,
        'time_created': timestamp,
    }
    data[str(target_id)].insert(0, message_dic)
    if in_channel:   
        write_info("message_data.json", data)
        write_info("dm_message_data.json", dm_message_data)
    if in_dm:
        write_info("message_data.json", message_data)
        write_info("dm_message_data.json", data)
    
    message_user_stats_add(user_id)
    message_dreams_stats_add(user_id)

    return message_id

def get_new_message_detail(message_data, dm_message_data):
    '''
    check message_data and dm_message_data and return a list cotaining the id of the message 
    to be sent and number_of_messages in DREAM
    Arguments:
        message_data (dict)
        dm_message_data (dict)
    Return Value
        list containing message detail
    '''
    if len(message_data) == 0 and len(dm_message_data) == 0:
        incoming_number_of_messages = 0
        # message id start form 0
        message_id = 0  
    else:
        # num of messages in channel_mesaage and dm_message is same
        incoming_number_of_messages = message_data['number_of_messages']
        message_id = message_data['message_index']
    return [message_id, incoming_number_of_messages]

def create_timestamp():
    '''
    create a timestamp based on the current UTC time
    Arguments:
        NONE
    Return Value:
        timestamp (int)
    '''
    # converting UTC/GMT time to timestamp
    create_time = datetime.utcnow()
    timestamp = int(create_time.replace(tzinfo=timezone.utc).timestamp())
    return timestamp

def check_message_len(message_len):
    '''
    check the length of message and raise InputError if message_len is greater than 1000
    Arguments:
        message_len (int)
    '''
    # raise InputError when message is more than 1000 characters
    if message_len > 1000:
        raise InputError('Message is more than 1000 characters')

def del_message(channel_id, dm_id, message_data, dm_message_data, index, in_channel, in_dm):
    '''
    remove the message based on the given channel_id and message_data or dm_id and dm_message_data
    dm_message_data ane the index of message
    Arguments:
        channel_id (str)
        dm_id (str)
        message_data (dict)
        dm_message_data (dict)
        index (int)
        in_channel (bool)
        in_dm (bool)
    '''
    # target message is in channel
    if in_channel:
        del(message_data[channel_id][index])
    # target message is in dm
    if in_dm:
        del(dm_message_data[dm_id][index])
    # update message detail
    message_data['number_of_messages'] = message_data['number_of_messages'] - 1
    dm_message_data['number_of_messages'] = dm_message_data['number_of_messages'] - 1
    # overwrite json data file
    write_info("message_data.json", message_data)
    write_info("dm_message_data.json", dm_message_data)

def check_owner(channel_id, dm_id, channel_data, dm_data, in_channel, in_dm, user_id):
    '''
    check whetehr the given user_id is the owner of the given dm or channel
    Arguments:
        channel_id (str)
        dm_id (str)
        channel_data (dict)
        dm_data (dict)
        in_channel (bool)
        in_dm (bool)
        user_id (int)
    Return:
        is_owner(bool)

    '''
    # initialise is_owner to false to indicate the user is not the owner
    is_owner = False
    # check owner in channel
    if in_channel:
        channel_owners = channel_data[channel_id]['channel_owners']
        for owner_id in channel_owners:
            if user_id in owner_id.values():
                is_owner = True
    # check owner in dm
    if in_dm:
        dm_owners = dm_data[dm_id]['dm_owners']
        for owner_id in dm_owners:
            if user_id in owner_id.values():
                is_owner = True
    return is_owner

def find_message(message_id, message_data, dm_message_data):
    '''
    find the location detail of the given message id
    Arguments:
        message_id (int)
        message_data (dict)
        dm_message_data (dict)
    Return values:
        return re_dic (dict) containing the location detail of given message_id if the message if found
        return False if the message is not found
    '''
    is_found = False
    for channel in message_data:
        # initialize counter i to 0
        i = 0
        # avoid int 'number_of_message' and 'message_index'    
        while type(message_data[channel]) != type(0) and i < len(message_data[channel]):
            if message_data[channel][i]['message_id'] == message_id:
                # the value of channel_id is str
                re_dic = {
                    'in_channel' : True,
                    'in_dm' : False,
                    'channel_id' : channel,
                    'dm_id' : '-1',
                    'index' : i,   
                }
                return re_dic
            i += 1

    for dm in dm_message_data:
        i = 0
        while type(dm_message_data[dm]) != type(0) and i < len(dm_message_data[dm]):
            if dm_message_data[dm][i]['message_id'] == message_id:
                re_dic = {
                    # the value of dm_id is str
                    'in_channel' : False,
                    'in_dm' : True,
                    'channel_id' : '-1',
                    'dm_id' : dm,
                    'index' : i,   
                }
                return re_dic
            i += 1
    return is_found

def modify_message(is_remove, is_edit, message_data, dm_message_data, message_id, message, is_global_owner, user_id, channel_data, dm_data):
    '''
    edit or remove the message with the given message id
    Arguments:
        is_remove (bool)
        is_edit (bool)
        message_data (dict)
        dm_message_data (dict)
        message_id (int)
        message (str) (empty str if is_remove is true)
        is_global_owner (bool)
        user_id (int)
        channel_data (dict)
        dm_data (dict)
    '''
    # read in pin_data and react_data
    pin_data = read_info('pin_data.json')
    react_data = read_info("react_data.json")

    if find_message(message_id, message_data, dm_message_data) == False:
        raise InputError('message (based on ID) does not exist')
    message_location = find_message(message_id, message_data, dm_message_data)

    # message found in channels
    if message_location['in_channel']:
        # find the user who sent the input message
        sent_user_id = message_data[message_location['channel_id']][message_location['index']]['u_id']
        # check if the input user is the owner of current channel
        is_channel_owner = check_owner(message_location['channel_id'], "-1", channel_data, dm_data, True, False, user_id)
        if not (is_global_owner or sent_user_id == user_id or is_channel_owner):
            raise AccessError('You do not have permission to modify this message!')
        # remove message
        if (is_global_owner or sent_user_id == user_id or is_channel_owner) and is_remove:
            del_message(message_location['channel_id'], "-1", message_data, dm_message_data, message_location['index'], True, False)
            del pin_data[str(message_id)]
            del react_data[str(message_id)]
        # edit message
        if (is_global_owner or sent_user_id == user_id or is_channel_owner) and is_edit:
            message_data[message_location['channel_id']][message_location['index']]['message'] = message
            # message notification in channel
            message_notification(user_id, message, True, False, int(message_location['channel_id']), -1)

    # message found in dms
    if message_location['in_dm']:
        sent_user_id = dm_message_data[message_location['dm_id']][message_location['index']]['u_id']
        # check if the input user is the owner of current dm
        is_dm_owner = check_owner("-1", message_location['dm_id'], channel_data, dm_data, False, True, user_id)
        if not (is_global_owner or sent_user_id == user_id or is_dm_owner):
            raise AccessError('You do not have permission to modify this message!')
        # remove message
        if (is_global_owner or sent_user_id == user_id or is_dm_owner) and is_remove:
            del_message("-1", message_location['dm_id'], message_data, dm_message_data, message_location['index'], False, True)
            del pin_data[str(message_id)]
            del react_data[str(message_id)]
        # edit message
        if (is_global_owner or sent_user_id == user_id or is_dm_owner) and is_edit:
            dm_message_data[message_location['dm_id']][message_location['index']]['message'] = message
            # message notification in DM
            message_notification(user_id, message, False, True, -1, int(message_location['dm_id']))
    # dump message data back to json file
    write_info("pin_data.json", pin_data)
    write_info("react_data.json", react_data)
    write_info("message_data.json", message_data)
    write_info("dm_message_data.json", dm_message_data)


def message_user_stats_add(user_id):
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
            num = user_stats_data[str(user_id)]["messages_sent"][-1]["num_messages_sent"] + 1
            append_dic = {
                "num_messages_sent" : num,
                "time_stamp" : time_finish
            }
            user_stats_data[str(user_id)]["messages_sent"].append(append_dic)
    write_info('user_stats_data.json', user_stats_data)

def message_dreams_stats_add(user_id):
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
    num = dreams_stats_data["messages_exist"][-1]["num_messages_exist"] + 1
    append_dic = {
        "num_messages_exist" : num,
        "time_stamp" : time_finish
    }
    dreams_stats_data["messages_exist"].append(append_dic)
    write_info('dreams_stats_data.json', dreams_stats_data)

def message_dreams_stats_delete(user_id):
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
    num = dreams_stats_data["messages_exist"][-1]["num_messages_exist"] - 1
    append_dic = {
        "num_messages_exist" : num,
        "time_stamp" : time_finish
    }
    dreams_stats_data["messages_exist"].append(append_dic)
    write_info('dreams_stats_data.json', dreams_stats_data)
def check_react_id(react_id):
    '''
    check whether the input react id is valid
    Argument:
        react_id (int)
    '''
    if react_id != 1:
        raise InputError('Input react_id is invalid!')

def check_react_list(user_id, react_id, message_id, react_data):
    '''
    check whether the input user is already in the  users list of react_id of input message
    Arguments:
        user_id (int)
        react_id (int)
        message_id (int)
        react_data (dict)
    Return Values:
        in_list (bool)
            True if the user is already in that list, False otherwise
    '''
    in_list = False
    if len(react_data[str(message_id)]) == 0:
        in_list = False
    elif user_id in react_data[str(message_id)][str(react_id)]:
        in_list = True
    return in_list

def message_notification(sent_user_id, message, in_channel, in_dm, channel_id, dm_id):
    '''
    Generate notification when there is a tag in the message
    Argument:
        sent_user_id (int)      - user sent message
        message (str)           - message str
        in_channel  (bool)      - notification in channel
        in_dm       (bool)      - notification in dm
        channel_id  (int)       - id of notification channel
        dm_id       (int)       - id of notification dm

    '''
    # read in data
    users_data = read_info("auth_users_data")
    user_id_to_email = read_info("auth_user_id_to_email")
    # create tag_message in notificaiton
    tag_message = message
    if len(message) > 20:
        tag_message = message[0:20]
    # use spaces to turn message_str into different elements
    message_list = message.split()
    for message_part in message_list:
        handle = ''
        if message_part[0] == '@':
            handle = message_part[1:]
            # check if this handle is valid
        for user in users_data.values():
            id_check = user['auth_user_id']
            # check whether the hanndl belongs to the member of input channel
            if user['handle'] == handle and in_channel:
                tagged_id = id_check
                if check_channel_participate(tagged_id, channel_id):
                    add_tag_notification(tagged_id, users_data[user_id_to_email[str(sent_user_id)]]['handle'], -1, channel_id, tag_message)
            # check whether the hanndl belongs to the member of input DM
            if user['handle'] == handle and in_dm:
                tagged_id = id_check
                if check_dm_participate(id_check, dm_id):
                    add_tag_notification(tagged_id, users_data[user_id_to_email[str(sent_user_id)]]['handle'], dm_id, -1, tag_message)

