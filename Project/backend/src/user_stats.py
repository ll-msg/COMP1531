from src.channel_data import channel_data
from src.dm_data import dm_data
from src.message_data import message_data
from src.dm_message_data import dm_message_data
from src.user_stats_data import user_stats_data
from src.dreams_stats_data import dreams_stats_data
from src.auth import auth_session_verify, auth_token_to_id 
from src.error import InputError
from src.error import AccessError
from src.information_io import write_info
from src.read_json import read_info, read_info_2

def user_stats_v1(token):
    '''
    user_stats_v1 is a function which will, for a valid user, return statistics about this user's use of UNSW DREAMS

    Arguments:
        token (string)    - A tamper-proof string belonging to a valid id encryped with JWT
        ...

    Exceptions:

        N/A

    Return Value:
        Returns a dictionary with user statistics

    '''   
    # checks if token is valid 
    auth_session_verify(token) 
    # convert token to user_id
    user_id = auth_token_to_id(token)
    # read in data file
    user_stats_data = read_info('user_stats_data.json')
    message_data = read_info('message_data.json')
    dm_data = read_info('dm_data.json')
    channel_data = read_info('channel_data.json')

    # calculate the user sum of utilization
    user_sum = user_stats_data[str(user_id)]["channels_joined"][-1]["num_channels_joined"] + user_stats_data[str(user_id)]["dms_joined"][-1]["num_dms_joined"] + user_stats_data[str(user_id)]["messages_sent"][-1]["num_messages_sent"]
    
    # calculate dreams
    if message_data == {}:
        number_of_messages = 0
    if message_data != {}:
        number_of_messages = message_data['number_of_messages']
    total_sum = len(channel_data) + len(dm_data) + number_of_messages
    
    # update involvement_rate
    if total_sum == 0:
        user_stats_data[str(user_id)]["involvement_rate"] = 0
    if total_sum != 0:
        user_stats_data[str(user_id)]["involvement_rate"] = float(user_sum) / float(total_sum)
    write_info('user_stats_data.json', user_stats_data)
    
    return_dict = {"user_stats": user_stats_data[str(user_id)]}

    return return_dict




def users_stats_v1(token):
    '''
    users_stats_v1 is a function which will, for a valid user, return statistics about the use of UNSW DREAMS

    Arguments:
        token (string)    - A tamper-proof string belonging to a valid id encryped with JWT
        ...

    Exceptions:

        N/A

    Return Value:
        Returns a dictionary with UNSW DREAMS statistics

    '''    
    # checks if token is valid 
    auth_session_verify(token) 
    # read in data file
    dreams_stats_data = read_info('dreams_stats_data.json')
    user_stats_data = read_info('user_stats_data.json')

    num_user = 0
    for user in user_stats_data:
        if user_stats_data[user]["channels_joined"][-1]["num_channels_joined"] >= 1 or user_stats_data[user]["dms_joined"][-1]["num_dms_joined"] >= 1:
            num_user = num_user + 1
    
    total_users = read_info_2("auth_total_users", 0)
    dreams_stats_data["utilization_rate"] = float(num_user) / float(total_users)

    write_info('dreams_stats_data.json', dreams_stats_data)
    return_dict = {"dreams_stats": dreams_stats_data}


    return return_dict