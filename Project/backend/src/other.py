# import src.auth_data
import src.message
import src.dm
import src.channel
import src.admin_data
from src.information_io import write_info, read_info
import threading 
from src.error import InputError
from src.error import AccessError

import os


def clear_v1():

    # clear registered users data
    write_info("auth_users_data", {})
    write_info("auth_total_users", 0)
    write_info("auth_user_id_to_email", {})
    write_info("auth_handle_list", [])

    write_info("admin_admin_list", [0])
    write_info("admin_number_of_admins", 1)
    
    src.notifications_data.notification_dict = {}

    write_info("auth_password_reset_dict", {})

    # clear out the profile pictures
    pfp_folder = 'src/imgurl'
    for filename in os.listdir(pfp_folder):
        if (filename != 'random.jpg'):
            file_path = os.path.join(pfp_folder, filename)
            os.remove(file_path)

    channel_data = {}
    write_info("channel_data.json", channel_data)
    message_data = {}
    write_info("message_data.json", message_data)
    dm_data = {}
    write_info("dm_data.json", dm_data)
    dm_message_data = {}
    write_info("dm_message_data.json", dm_message_data)
    pin_data = {}
    write_info("pin_data.json", pin_data)
    react_data = {}
    write_info("react_data.json", react_data)
    standup_data = {}
    write_info("standup_data.json", standup_data)
    user_stats_data = {}
    write_info("user_stats_data.json", user_stats_data)
    dreams_stats_data = {}
    write_info("dreams_stats_data.json", dreams_stats_data)

    
    
def search_v2(token, query_str):
    """
    Returns a collection of all messsages (in channels and dms the user is present in) which contain the query string 

    Arguments:
        token (string)       - the users token
        query_str (string)   - the query string

    Exceptions:
        InputError  - query_str is above 1000 characters

    Return Value:
        Returns { messages }
    """

    # if the query string has more than 1000 chars
    if (len(query_str) > 1000):
        raise InputError(description='Query string over 1000 chars long')
    
    # verify the token is valid
    src.auth.auth_session_verify(token)
    auth_user_id = src.auth.auth_token_to_id(token)

    # get message_data from the json file
    message_data = read_info('message_data.json')
    
    dm_message_data = read_info('dm_message_data.json')
    
    messages = []
    
    # search through channels
    for channel in message_data:
        if (type(message_data[channel]) == type(0)):
            continue
        # check that the user is a member of that channel
        if (not src.channel.check_participate(auth_user_id, channel)):
            continue
        
        # initialize counter i to 0
        i = 0
        # avoid int 'number_of_message' and 'message_index'    
        while type(message_data[channel]) != type(0) and i < len(message_data[channel]):
            if query_str in message_data[channel][i]['message']:
                # message matches the search parameters
                # append message to the list
                messages.append(
                    {
                       'message_id' : message_data[channel][i]['message_id'],
                       'u_id' : message_data[channel][i]['u_id'],
                       'message' : message_data[channel][i]['message'],
                       'time_created' : message_data[channel][i]['time_created'],
                    }
                )
            
            i = i + 1
    
    # search through dms
    for dm in dm_message_data:
        if (type(dm_message_data[dm]) == type(0)):
            continue
        # check that the user is a member of that dm
        if (not src.message.check_dm_participate(auth_user_id, dm)):
            continue
        
        i = 0
        while type(dm_message_data[dm]) != type(0) and i < len(dm_message_data[dm]):
            if query_str in dm_message_data[dm][i]['message']:
                # message matches the search parameters
                # append message to the list
                messages.append(
                    {
                       'message_id' : dm_message_data[dm][i]['message_id'],
                       'u_id' : dm_message_data[dm][i]['u_id'],
                       'message' : dm_message_data[dm][i]['message'],
                       'time_created' : dm_message_data[dm][i]['time_created'],
                    }
                )
            i = i + 1

    return {'messages': messages}


def users_all_v1(token):
    """
    Returns a list of all registered users along with regstration details

    Arguments:
        token (string) - the users token

    Return Value:
        Returns {'users':[
            {
                "u_id" : u_id,
                "email" : email,
                "name_first" : name_first,
                "name_last" : name_last,
                "handle_str" : handle_str,
            },
            ...
        ]
    }
    """

    src.auth.auth_session_verify(token)

    users_data = read_info("auth_users_data")

    user_list = []

    for key, value in users_data.items():
        user_list.append(
            {
                "u_id" : value["auth_user_id"],
                "email" : key,
                "name_first" : value["first_name"],
                "name_last" : value["last_name"],
                "handle_str" : value["handle"],
                'profile_img_url' : value['profile_img_url'],
            }
        )

    return {
        'users': user_list
    }

