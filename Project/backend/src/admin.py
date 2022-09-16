import src.auth
# import src.auth_data
# import src.admin_data

from src.read_json import read_info, read_info_2
import src.information_io

from src.error import InputError
from src.error import AccessError

def admin_verify(token):
    """
    Check whether a given token belongs to an admin (a DREAMS owner)

    Arguments:
        token (string)  - token to be checked

    Return Value:
        Returns True if token belongs to a DREAMS owner
        Returns False otherwise
    """
    # verify the token is valid
    src.auth.auth_session_verify(token)

    admin_set = read_info_2("admin_admin_list", [0])
    
    return (src.auth.auth_token_to_id(token) in admin_set)


def user_remove_v1(token, auth_user_id):
    """
    Remove user with auth_user_id from DREAMS if token belongs to admin
    Also replace all their messages, name with "Removed user"

    Arguments:
        token (string)      - token of the user doing the removing
        auth_user_id (int)  - auth_user_id of the user who has to be removed
    
    Exceptions:
        InputError  - u_id does not refer to a valid user
                    - The user is currently the only owner
        
        AccessError - The authorised user is not an owner
    
    Return:
        Empty dict
    """
    
    total_users = read_info("auth_total_users")
    
    users_data = read_info("auth_users_data")
    
    user_id_to_email = read_info("auth_user_id_to_email")
    
    admin_set = read_info_2("admin_admin_list", [0])

    number_of_admins = read_info_2("admin_number_of_admins", 1)

    # verify if the token belongs to admin
    isAdmin = admin_verify(token)
    if (isAdmin):

        # if the auth_user_id is >= the total_users its not valid
        if (auth_user_id >= total_users):
            raise InputError(description='u_id does not refer to a valid user')
        
        # if the user being removed is the only admin (DREAMS owner)
        if ((auth_user_id in admin_set) and (number_of_admins == 1)):
            raise InputError(description='The user is currently the only owner')
        
        # read message_data from json file
        message_data = read_info('message_data.json')

        for channel in message_data:
            # initialize counter i to 0
            i = 0
            # avoid int 'number_of_message' and 'message_index'    
            while type(message_data[channel]) != type(0) and i < len(message_data[channel]):
                if  (auth_user_id == message_data[channel][i]['u_id']):
                    message_data[channel][i]['message'] = 'Removed user'
                i = i + 1
        
        # read message_data from json file
        dm_message_data = read_info('dm_message_data.json')

        for dm in dm_message_data:
            i = 0
            while type(dm_message_data[dm]) != type(0) and i < len(dm_message_data[dm]):
                if (auth_user_id == dm_message_data[dm][i]['u_id']):
                    dm_message_data[dm][i]['message'] = 'Removed user'
                i = i + 1
        
        
        # replace the deleted users first and last name with 'Removed' 'user', blanks all other attributes
        user_email = user_id_to_email[str(auth_user_id)]
        users_data[user_email]['first_name'] = 'Removed'
        users_data[user_email]['last_name'] = 'user'
        users_data[user_email]['sessions'] = []
        users_data[user_email]['session_count'] = 0
        users_data[user_email]['password'] = src.auth.random_chars(100)

        # write current values of vars to file
        src.information_io.write_info("auth_users_data", users_data)
        src.information_io.write_info("message_data.json", message_data)
        src.information_io.write_info("dm_message_data.json", dm_message_data)
    
        return {}
    
    else:
        raise AccessError(description='The authorised user is not an owner')


def user_permission_change_v1(token, auth_user_id, permission_id):
    """
    Change permission_id of user with auth_user_id if token belongs to admin
    Admins (DRDEAMS owners) have permission id 1 and regular users have 2

    Arguments:
        token (string)      - token of the user changing the permission
        auth_user_id (int)  - auth_user_id of the user whose permissions have to be changed
        permission_id (int) - the new permission id to be set
    
    Exceptions:
        InputError  - u_id does not refer to a valid user
                    - permission_id does not refer to a value permission
        
        AccessError - The authorised user is not an owner

    Return:
        Empty dict
    """

    total_users = read_info("auth_total_users")

    admin_set = read_info_2("admin_admin_list", [0])

    number_of_admins = read_info_2("admin_number_of_admins", 1)

    # verify if the token belongs to admin
    isAdmin = admin_verify(token)
    if (isAdmin):
        # if the auth_user_id is >= the total_users its not valid
        if (auth_user_id >= total_users):
            raise InputError(description='u_id does not refer to a valid user')
        
        # if the permission value is not valid
        if (permission_id not in [1,2]):
            raise InputError(description='permission_id does not refer to a value permission')
        
        # if the user is not already an admin, make them one
        if (auth_user_id not in admin_set) and (permission_id == 1):
            admin_set.append(auth_user_id)
            number_of_admins += 1

        # if the user is an admin, remove them
        if (auth_user_id in admin_set) and (permission_id == 2):
            if (number_of_admins == 1):
                # assumption that the only admin cannot change permission_id to 2 for themselves
                raise InputError(description='There is only one admin')
            
            admin_set.remove(auth_user_id)
            number_of_admins -= 1

        # write information to files
        src.information_io.write_info("admin_admin_list", admin_set)
        src.information_io.write_info("admin_number_of_admins", number_of_admins)
    else:
        raise AccessError(description='The authorised user is not an owner')
    
    return {}
    
