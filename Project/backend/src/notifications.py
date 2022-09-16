import src.notifications_data
import src.auth

from src.error import InputError
from src.error import AccessError

from src.read_json import read_info

def notification_message_get_v1(token):
    """
    Return the users most recent 20 notifications

    Arguments:
        token (string)

    Return Value:
        Returns { notifications }
    """
    # verify the token is valid
    src.auth.auth_session_verify(token)
    auth_user_id = src.auth.auth_token_to_id(token)

    # if the user has no notifications
    if auth_user_id not in src.notifications_data.notification_dict:
        return {'notifications':[]}
    
    # serve the reverse list
    notif_list = src.notifications_data.notification_dict[auth_user_id].copy()
    notif_list.reverse()
    
    # get the notifications from notification_dict and return
    return {'notifications' : notif_list}


def add_tag_notification(auth_user_id, handle, dm_id, channel_id, tag_message):
    """
    Add an @tag notification to the notification_dict
    Overwrites oldest notif if a user has 20 notifs

    Arguments:
        auth_user_id (int)      - id of the user to be notified
        handle                  - handle of the user who @ tagged
        dm_id (int)             - id of the dm from which the notif originates (-1 if not dm)
        channel_id (int)        - id of the channel from which the notif originates (-1 if not channel)
        tag_message (string)    - message ahead of the @ tag

    """
    # create an empty list if the user has no previous notifications
    if (auth_user_id not in src.notifications_data.notification_dict):
        src.notifications_data.notification_dict[auth_user_id] = []
        
    # get the channel/dm name
    if (dm_id == -1):
        # read channel_data from the json file
        channel_data = read_info('channel_data.json')
        cd_name = channel_data[str(channel_id)]['name']
    elif (channel_id == -1):
        # read dm_data from the json file
        dm_data = read_info('dm_data.json')
        cd_name = dm_data[str(dm_id)]['name']
    else:
        # should never get here
        pass

    # format of the notification
    notification = {
        "channel_id" : channel_id,
        "dm_id" : dm_id,
        "notification_message" : f"{handle} tagged you in {cd_name}: {tag_message}",
    }

    # if the number of notifications is 20, pop the first notification in notification_dict
    if (len(src.notifications_data.notification_dict[auth_user_id]) == 20):
        src.notifications_data.notification_dict[auth_user_id].pop(0)

    # add the notification to notification_dict
    src.notifications_data.notification_dict[auth_user_id].append(notification)


def add_join_notification(auth_user_id, handle, dm_id, channel_id):
    """
    Add a join dm/channel notification to the notification_dict
    Overwrites oldest notif if a user has 20 notifs

    Arguments:
        auth_user_id (int)      - id of the user to be notified
        dm_id (int)             - id of the dm from which the notif originates (-1 if not dm)
        channel_id (int)        - id of the channel from which the notif originates (-1 if not channel)

    """
    # create an empty list if the user has no previous notifications
    if (auth_user_id not in src.notifications_data.notification_dict):
        src.notifications_data.notification_dict[auth_user_id] = []
    
    # read channel_data from the json file
    channel_data = read_info('channel_data.json')
    
    # get the channel/dm name
    if (dm_id == -1):
        # read channel_data from the json file
        channel_data = read_info('channel_data.json')
        cd_name = channel_data[str(channel_id)]['name']
    elif (channel_id == -1):
        # read dm_data from the json file
        dm_data = read_info('dm_data.json')
        cd_name = dm_data[str(dm_id)]['name']
    else:
        # should never get here
        pass
    
    # format of the notification
    notification = {
        "channel_id" : channel_id,
        "dm_id" : dm_id,
        "notification_message" : f"{handle} added you to {cd_name}",
    }

    # if the number of notifications is 20, pop the first notification in notification_dict
    if (len(src.notifications_data.notification_dict[auth_user_id]) == 20):
        src.notifications_data.notification_dict[auth_user_id].pop(0)

    # add the notification to notification_dict
    src.notifications_data.notification_dict[auth_user_id].append(notification)
