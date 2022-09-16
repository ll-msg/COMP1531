import re
# import src.auth_data
import src.secret
import src.information_io
from src.read_json import read_info, read_info_2
from src.user_stats_data import user_stats_data
from src.dreams_stats_data import dreams_stats_data
from src.information_io import write_info

from src.error import InputError
from src.error import AccessError

from flask import Flask, request
from json import dumps

import jwt
import hashlib

from random import choices
import string

from datetime import timezone, datetime


def auth_login_v2(email, password):
    """
    Logs in a user by verifying login details and returning a jwt and auth_user_id

    Arguments:
        email (string)      - the email that the user used to register
        password (string)   - the users password

    Exceptions:
        InputError  - Email entered is not a valid email
                    - Email entered does not belong to a user
                    - Password is not correct

    Return Value:
        Returns {"token" : token, "auth_user_id" : auth_user_id} (if the email and password match the stored registration details)
    """

    users_data = read_info("auth_users_data")

    # check if email is valid using regex
    # check password length >6 chars
    email_valid(email)
    password_valid(password)
    
    # check if email is being used by another user
    # then see if password matches
    if email not in users_data:
        raise InputError(description='Email does not belong to a user')
    
    # calculate the hash of the password
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    if (users_data[email]['password'] != password_hash):
        raise InputError(description='Incorrect password')
    
    # loop through session ids (session_count + 1) to 0 in reverse order to find an unused one
    session_id = users_data[email]['session_count']# + 1
    while(session_id >= 0):
        if (session_id in users_data[email]['sessions']):
            session_id = session_id - 1
        else:
            break

    # update sessions and session_count
    users_data[email]['session_count'] += 1
    users_data[email]['sessions'].append(session_id)

    # encode and return jwt
    # structure of jwt is {'auth_user_id' : auth_user_id, 'session_id' : session_id, 'garbage' : garbage}
    # garbage ensures the jwt we generate each time is unique even if session_id is the same (for additional security)
    jwt_curr = encode_token(
        {
            'auth_user_id' : users_data[email]['auth_user_id'],
            'session_id' : session_id,
            'garbage' : random_chars(100)
        }
    )

    # write current values of vars to file
    src.information_io.write_info("auth_users_data", users_data)

    return {
        'token' : jwt_curr,
        'auth_user_id' : users_data[email]['auth_user_id'],
    }



def auth_register_v2(email, password, name_first, name_last):
    """
    Registers and logs in a user by storing registration data and returning a jwt

    Arguments:
        name_first (string) - the users first name
        name_last (string)  - the users last name
        email (string)      - the users email
        password (string)   - the users password
    
    Exceptions:
        InputError  - name_first or name_last is not between 1 and 50 characters inclusively in length
                    - Email entered is not a valid email
                    - Email address is already being used by another user
                    - Password entered is less than 6 characters long

    Return Value:
        Returns {"token" : token, "auth_user_id" : auth_user_id}
    """

    users_data = read_info("auth_users_data")

    handle_list = read_info_2("auth_handle_list", [])
    
    total_users = read_info_2("auth_total_users", 0)

    user_id_to_email = read_info("auth_user_id_to_email")

    

    # check if email is valid using regex
    # check password length >6 chars
    # check first name and last name are  between 1 and 50 chars
    email_valid(email)
    password_valid(password)
    name_valid(name_first)
    name_valid(name_last)

    # check if email is being used by another user
    if email in users_data:
        raise InputError(description='Email address is already being used by another user')

    # find an unused handle
    # add numbers 0 onwards after handle if its already in use
    user_handle = (name_first.lower() + (name_last.replace(" ", "")).lower())[:20]
    handle_id = 0
    while (user_handle in handle_list):
        if (handle_id == 0):
            user_handle = user_handle + str(handle_id)
        else:
            user_handle = user_handle[:-len(str(handle_id - 1))] + str(handle_id)
        
        handle_id = handle_id + 1
    
    # update global variables
    handle_list.append(user_handle)
    user_id_to_email[str(total_users)] = email

    users_data[email] = {
        'auth_user_id': total_users,
        'first_name' : name_first,
        'last_name' : name_last,
        'password' : hashlib.sha256(password.encode()).hexdigest(), # calculate the hash of the password
        'handle' : user_handle,
        'sessions' : [],
        'session_count' : 0,
        'profile_img_url' : '',
    }

    total_users = total_users + 1

    # write current values of vars to file
    src.information_io.write_info("auth_users_data", users_data)
    src.information_io.write_info("auth_total_users", total_users)
    src.information_io.write_info("auth_user_id_to_email", user_id_to_email)
    src.information_io.write_info("auth_handle_list", handle_list)


    # initialize the user statistics dict
    user_stats_data = read_info('user_stats_data.json')
    dreams_stats_data = read_info('dreams_stats_data.json')
    create_time = datetime.utcnow()
    time_stamp = int(create_time.replace(tzinfo=timezone.utc).timestamp())
    if total_users - 1 == 0:
        dreams_stats_data = {

            "channels_exist" : [
                {
                    "num_channels_exist" : 0,
                    "time_stamp" : time_stamp
                }
            ],
            "dms_exist" : [
                {
                    "num_dms_exist" : 0,
                    "time_stamp" : time_stamp
                }
            ],
            "messages_exist" : [
                {
                    "num_messages_exist" : 0,
                    "time_stamp" : time_stamp
                }
            ],
            "utilization_rate" : float(0)

        }


    user_stats_data[str(total_users - 1)] = {
        
            "channels_joined" : [
                {
                    "num_channels_joined" : 0,
                    "time_stamp" : time_stamp
                }
            ],
            "dms_joined" : [
                {
                    "num_dms_joined" : 0,
                    "time_stamp" : time_stamp
                }
            ],
            "messages_sent" : [
                {
                    "num_messages_sent" : 0,
                    "time_stamp" : time_stamp
                }
            ],
            "involvement_rate" : float(0)

        }
    

    write_info('user_stats_data.json', user_stats_data)
    write_info('dreams_stats_data.json', dreams_stats_data)


    # log in the user
    return auth_login_v2(email, password)


def auth_logout_v2(token):
    """
    Logs out a user by removing their jwt from users_data

    Arguments:
        token (string)    - the token
    
    Return Value:
        Returns True if token is valid and then is removed
        Returns False otherwise
    """

    users_data = read_info("auth_users_data")
    
    user_id_to_email = read_info("auth_user_id_to_email")

    # verify the token is valid
    auth_session_verify(token)

    jwt_data = decode_token(token)
    email = user_id_to_email[str(jwt_data['auth_user_id'])]
    
    # remove the session_id from the sessions list
    users_data[email]['sessions'].remove(jwt_data['session_id'])

    # update sessions_count
    users_data[email]['session_count'] = users_data[email]['session_count'] - 1

    # write current values of vars to file
    src.information_io.write_info("auth_users_data", users_data)

    return {'is_success' : True}


def auth_passwordreset_request_v1(email):
    """
    Create, store and return a random secret code that will be emailed to the user

    Arguments:
        email (string)

    Exceptions:
        InputError  - Email address does not belong to a registered user
    
    Return Value:
        Returns reset_code
    """
    # read in auth data from files
    users_data = read_info("auth_users_data")
    password_reset_dict = read_info("auth_password_reset_dict")

    # check if the email is registered
    if email not in users_data:
        # assumption
        raise InputError(description='Email address does not belong to a registered user')

    # create a random reset code that is unique
    unique_reset_code = False
    while (not unique_reset_code):
        unique_reset_code = True
        reset_code = random_chars(10)
        for email in password_reset_dict:
            if (password_reset_dict[email] == reset_code):
                unique_reset_code = False
    

    # update password_reset_dict
    password_reset_dict[email] = reset_code

    # write reset code info to file
    src.information_io.write_info("auth_password_reset_dict", password_reset_dict)

    # return the reset code
    return reset_code


def auth_passwordreset_reset_v1(reset_code, new_password):
    """
    Given a reset code change that users password

    Arguments:
        email (string)

    Exceptions:
        InputError  - reset_code is not a valid reset code
        InputError  - Password entered is less than 6 characters long
    """
    # read in auth data from files
    users_data = read_info("auth_users_data")
    password_reset_dict = read_info("auth_password_reset_dict")

    valid_reset_code = False
    
    # go through every single email and check if its code matches
    for email in password_reset_dict:
        if (password_reset_dict[email] == reset_code):
            valid_reset_code = True
    
    # if the reset code is invalid, raise exception
    if (not valid_reset_code):
        raise AccessError(description='Reset code is not a valid reset code')
    
    # see if the new password is valid
    password_valid(new_password)
    
    # change that users password and remove reset code from password_reset_dict
    new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    users_data[email]['password'] = new_password_hash
    del password_reset_dict[email]

    # write updated info to files
    src.information_io.write_info("auth_users_data", users_data)
    src.information_io.write_info("auth_password_reset_dict", password_reset_dict)



def auth_session_verify(token):
    """
    Check whether a token is valid by checking if its session_id is in user_data[email]['sessions']

    Arguments:
        token (string)

    Exceptions:
        AccessError  - Occurs when token signature is invalid
                     - Occurs when session_id is invalid
    
    Return Value:
        Returns True if token is valid and session is active
    """

    user_id_to_email = read_info("auth_user_id_to_email")
    
    users_data = read_info("auth_users_data")
    
    jwt_data = decode_token(token)
    
    email = user_id_to_email[str(jwt_data['auth_user_id'])]
    
    if (jwt_data['session_id'] not in users_data[email]['sessions']):
        raise AccessError(description='Token is invalid')
    
    return True


def auth_token_to_id(token):
    """
    Return the auth_user_id given a token.

    Arguments:
        token (string)

    Return Value:
        Returns auth_user_id of user with token
    """
    
    jwt_data = decode_token(token)
    return jwt_data['auth_user_id']


def email_valid(email):
    """
    Check whether a password is valid (satisfies certain conditions)

    Arguments:
        password (string)

    Exceptions:
        InputError  - Occurs when password is not valid

    Return Value:
        Returns True if name is valid
    """
    re_string = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'
    if (re.search(re_string, email) == None):
        raise InputError(description='Email entered is not a valid email')
    return True


def name_valid(name):
    """
    Check whether a name is valid (satisfies certain conditions)

    Arguments:
        name (string)

    Exceptions:
        InputError  - Occurs when name is not valid

    Return Value:
        Returns True if name is valid
    """
    if (len(name) < 1 or len(name) > 50):
        raise InputError(description='Name is not between 1 and 50 characters inclusively in length')
    return True


def password_valid(password):
    """
    Check whether a password is valid (satisfies certain conditions)

    Arguments:
        password (string)

    Exceptions:
        InputError  - Occurs when password is not valid

    Return Value:
        Returns True if password is valid
    """
    if (len(password) < 6):
        raise InputError(description='Password entered is less than 6 characters long')
    return True


def random_chars(strlen):
    """
    Retun a string of random chars of length strlen consisting of lowercase letters, uppercase letters and digits

    Arguments:
        strlen (int)

    Return Value:
        Returns string of len strlen
    """
    return ''.join(choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k = strlen))


def decode_token(token):
    """
    Decodes a jwt and if its valid returns the payload

    Arguments:
        token (string)

    Exceptions:
        AccessError  - Occurs when token is not valid (wrong signature)

    Return Value:
        Returns jwt_data (the payload)
    """
    try:
        jwt_data = jwt.decode(token.encode('utf-8'), src.secret.SECRET, algorithms = ['HS256'])
        return jwt_data
    except Exception as e:
        raise AccessError(description='Token is invalid') from e


def encode_token(data_dict):
    """
    Encodes and returns a jwt

    Arguments:
        data_dict (dict) - the payload data in dict format

    Return Value:
        Returns token
    """
    return jwt.encode(data_dict, src.secret.SECRET, algorithm = 'HS256')
