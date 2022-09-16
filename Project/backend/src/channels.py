
from src.error import InputError
from src.error import AccessError
from src.auth import auth_session_verify, auth_token_to_id 
from src.information_io import write_info
from src.read_json import read_info
from src.user_stats_data import user_stats_data
from datetime import timezone, datetime, timedelta
from src.dreams_stats_data import dreams_stats_data

def channels_list_v2(token):
    '''
    Provide a list of all channels and their associated details that the authorised user is part of

    Arguments:
        <auth_user_id> (integer)    - The id of a authorised user who is member of the channel

    Exceptions:
        AccessError                 - Token passed in is not a valid id.

    Return Value:
        Returns channel lists which contain the channels and associated details

    '''
    # check whether the input token refer to a valid user id
    auth_session_verify(token)
    # convert token to user id
    auth_user_id = auth_token_to_id(token)
    # read channel data
    channel_data = read_info('channel_data.json')
    # Declare an empty list where we will store
    # all channels the user is apart of
    channels_list = []
    # Check whether the channel_data is empty, if so, renturn a dic with 'channels' as key and empty list as value
    if len(channel_data) == 0:
        return_dic = {}
        return_dic['channels'] = channels_list
        return return_dic
    # Loop through each channel and check if user
    # is a member/owner of the channel    
    for index in channel_data:
        channel = channel_data[index]
        # If there is a match we will add the channel info
        # to channels_list and skip to the next channel
        for member in channel['channel_members']:
            if (member['u_id'] == auth_user_id):
                detail_dic = {}
                detail_dic['channel_id'] = int(index)
                detail_dic['name'] = channel['name']
                channels_list.append(detail_dic)
                break
    return_dic = {}
    return_dic['channels'] = channels_list
    return return_dic


def channels_listall_v2(token):

    '''
    Provide a list of all channels existing in the database and their associated details

    Arguments:
        <auth_user_id> (integer)    - The id of a authorised user who is member of the channel

    Exceptions:
        N/A

    Return Value:
        Returns channel lists which contain all the channels and associated details

    '''
    # check whether the input token refer to a valid user id
    auth_session_verify(token)
    channel_data = read_info('channel_data.json')
    
    channels_list = []
    
    for index in range (0, len(channel_data)):
        channel = channel_data[str(index)]
        channels_list.append({'channel_id' : index, 'name' : channel['name']})
    
    return {'channels' : channels_list}

# create a new channel - either private or public
def channels_create_v2(token, name, is_public):
    '''
    Create a new channel which is either public or private

    Arguments:
        <auth_user_id> (integer)    - The id of a authorised user who is member of the channel
        <name> (string)     - The name of the channel
        <is_public> (boolean)   - The status of the channel, either True or False

    Exceptions:
        InputError  - Occurs when the channel name is longer than 20 characters
        AccessError - Occurs when the token passed in is not a valid id.
    Return Value:
        Returns the channel_id of the new channel

    '''
    # check whether the input token refer to a valid user id
    auth_session_verify(token)
    # convert token to user id
    auth_user_id = auth_token_to_id(token)
    # read in channel_data
    channel_data = read_info('channel_data.json')
    # read in standup_data
    standup_data = read_info('standup_data.json')
    # Input error case - name is longer than 20 characters
    if (len(name)) > 20:
        raise InputError("The channel name should not be more than 20 characters long.")
    # update the channel_id
    channel_id = len(channel_data)
    # main part - create a either private or public channel
    channel_data[str(channel_id)] = {
        'name': name,
        'public': is_public,
        'channel_owners' : [
                {'u_id': auth_user_id}
            ],
        'channel_members' : [
            {'u_id': auth_user_id}],
        'publicity': is_public
    }
    # initialize the standup data
    standup_data[str(channel_id)] = {
        'is_active' : False,
        'length' : 0,
        'time_finish' : 0, # use time stamp!
        'creator' : 0,
        'message' : [],
    }
    # Overwrite standup_data to standup_data.json
    write_info("standup_data.json", standup_data)
    # Overwrite channel_data to channel_data.json
    write_info('channel_data.json', channel_data)

    channel_user_stats_add(auth_user_id)
    channel_dreams_stats_add(auth_user_id)

   # return the channel_id
    return {
        'channel_id': channel_id
    }

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

def channel_dreams_stats_add(user_id):
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
    num = dreams_stats_data["channels_exist"][-1]["num_channels_exist"] + 1
    append_dic = {
        "num_channels_exist" : num,
        "time_stamp" : time_finish
    }
    dreams_stats_data["channels_exist"].append(append_dic)
    write_info('dreams_stats_data.json', dreams_stats_data)


