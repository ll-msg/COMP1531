import re
from src.error import InputError
from src.error import AccessError
from src.auth import auth_session_verify, auth_token_to_id, random_chars
import src.information_io
from src.read_json import read_info, read_info_2

import urllib.request
from PIL import Image

from os import remove

# import src.auth_data as auth_data

def user_profile_v2(token, u_id):
    '''
    user_profile_v2 is a function which will, for a valid user, return information about their user ID, email, first name, last name and handle.

    Arguments:
        token (string)    - A tamper-proof string belonging to a valid id encryped with JWT
        u_id (integer)    - The user id of a person who is calling upon this function
        ...

    Exceptions:
        InputError  - Occurs when user with u_id is not a valid user
        AccessError - Occurs when the token being passed in is not a valid id

    Return Value:
        Returns a dictionary with details about the user.

    '''    
    #checks if token is valid 
    auth_session_verify(token)
    #checks if user id is valid 
    check_user_valid(u_id)

    users_data = read_info("auth_users_data")
    
    user_id_to_email = read_info("auth_user_id_to_email")
    
    email = user_id_to_email[str(u_id)]   
    #using the email, get details from the dictionary users_data
    name_first = users_data[email]['first_name']
    name_last = users_data[email]['last_name']
    handle_str = users_data[email]['handle']
    profile_img_url = users_data[email]['profile_img_url']
    
    #return a dictionary with all the details gathered
    return {
        'user': {
            'u_id': u_id,
            'email': email,
            'name_first': name_first,
            'name_last': name_last,
            'handle_str': handle_str,
            'profile_img_url' : profile_img_url,
        },
    }

def user_profile_setname_v2(token, name_first, name_last):
    '''
    user_profile__setname_v2 is a function which will, for a valid user, update the user's first and last names.

    Arguments:
        token (string)    - A tamper-proof string belonging to a valid id encryped with JWT
        name_first (string)    - The name that the user is trying to change their first name to 
        name_last (string)    - The name that the user is trying to change their last name to 
        
        ...

    Exceptions:
        InputError  - Occurs when name_first is not between 1 and 50 characters inclusively in length
        InputError  - Occurs when name_last is not between 1 and 50 characters inclusively in length
        AccessError - Occurs when the token being passed in is not a valid id

    Return Value:
        Returns an empty dictionary.

    '''  
    #checks if token is valid 
    auth_session_verify(token)

    users_data = read_info("auth_users_data")
    
    #checks if the given names are valid 
    check_name_valid(name_first)
    check_name_valid(name_last)
    
    #obtain uid
    user_id = auth_token_to_id(token)
    
    #loops through data to find the user and change their name 
    for email in users_data:
        if users_data[email]['auth_user_id'] == user_id:
            users_data[email]['first_name'] = name_first
            users_data[email]['last_name'] = name_last
    
    # write current values of vars to file
    src.information_io.write_info("auth_users_data", users_data)
    
    return {
    }

def user_profile_setemail_v2(token, email):
    '''
    user_profile_setemail_v2 is a function which will, for a valid user, update the user's email address.

    Arguments:
        token (string)    - A tamper-proof string belonging to a valid id encryped with JWT
        email (string)    - The email that the user is trying to update their email to 
        ...

    Exceptions:
        InputError  - Occurs when the provided email is not a valid email
        InputError  - Occurs when the provided email is already in use by another user 
        AccessError - Occurs when the token being passed in is not a valid id

    Return Value:
        Returns an empty dictionary.

    '''  
    #checks if token is valid 
    auth_session_verify(token)

    users_data = read_info("auth_users_data")
    
    user_id_to_email = read_info("auth_user_id_to_email")
    
    #checks if the given email is valid 
    valid_email(email)
    
    #checks if the given email is being used by another user
    if email in users_data:
        raise InputError("This email address is already being used!")
    user_id = auth_token_to_id(token)
    old_email = user_id_to_email[str(user_id)]
    #updates email to new email input
    users_data[email] = users_data[old_email]
    del users_data[old_email]
    user_id_to_email[str(user_id)] = email
    
    # write current values of vars to file
    src.information_io.write_info("auth_users_data", users_data)
    src.information_io.write_info("auth_user_id_to_email", user_id_to_email)

    return {
    }

def user_profile_sethandle_v1(token, handle_str):
    '''
    user_profile_sethandle_v1 is a function which will, for a valid user, update their handle.

    Arguments:
        token (string)    - A tamper-proof string belonging to a valid id encryped with JWT
        handle (string)    - The handle that the user is trying to change their handle to 
        ...

    Exceptions:
        InputError  - Occurs when handle_str is not between 3 and 20 characters inclusive
        InputError  - Occurs when handle is already being used by another user 
        AccessError - Occurs when the token being passed in is not a valid id

    Return Value:
        Returns an empty dictionary.

    '''  
    #checks if token is valid 
    auth_session_verify(token)

    users_data = read_info("auth_users_data")
    handle_list = read_info_2("auth_handle_list", [])
    
    #checks if handle is valid 
    if len(handle_str) > 20 or len(handle_str) < 3:
        raise InputError("Input handle is invalid!")
    
    #checks if handle is in use
    in_use = 0
    user_id = auth_token_to_id(token)
    for email in users_data:
        if users_data[email]['handle'] == handle_str:
            in_use = 1
        if users_data[email]['auth_user_id'] == user_id:
            curr_email = email
    if in_use == 1:
        raise InputError("Handle is already being used!")
        
    #changes user's previous handle to current handle
    old_handle = users_data[curr_email]['handle']
    users_data[curr_email]['handle'] = handle_str
    handle_list.remove(old_handle)
    handle_list.append(handle_str)

    # write current values of vars to file
    src.information_io.write_info("auth_users_data", users_data)
    src.information_io.write_info("auth_handle_list", handle_list)
    
    return {
}


def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end, server_base_url):
    """
    Given an image url and cropping details, set that users profile picture

    Arguments:
        token (string)
        img_url (string)
        x_start, y_start, x_end, y_end (ints)
        server_base_url (string) - the base url of the flask server

    Exceptions:
        InputError  - img_url returns an HTTP status other than 200
                    - any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
                    - Image uploaded is not a JPG
    
    Return Value:
        {}
    """
    img_url_type = img_url.split(".")[-1]
    if (img_url_type != "jpg"):
        raise InputError("Image uploaded is not a JPG")
    
    auth_session_verify(token)
    auth_user_id = auth_token_to_id(token)

    user_id_to_email = read_info("auth_user_id_to_email")
    users_data = read_info("auth_users_data")

    # retrieve the image to a temp.jpg
    temp_local_path = "temp.jpg"
    image_local_path = "imgurl/" + random_chars(20) + ".jpg"
    try:
        urllib.request.urlretrieve(img_url, temp_local_path)
    except Exception as e:
        raise InputError("img_url returns an HTTP status other than 200") from e

    # crop the image given start and end x and y coordinates of cropping rectangle
    imageObject = Image.open(temp_local_path)

    # check dimensions of image and if start and end x and y are valid
    im_width, im_height = imageObject.size

    if (not ((0 <= x_start < x_end <= im_width) and (0 <= y_start < y_end <= im_height))):
        raise InputError("x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL")

    cropped = imageObject.crop( (x_start, y_start, x_end, y_end) )
    cropped.save("src/" + image_local_path)

    # delete the old image
    old_link  = users_data[user_id_to_email[str(auth_user_id)]]['profile_img_url']
    if "imgurl/" in old_link:
        old_name = old_link.split("imgurl/")[-1]
        # dont remove the default random.jpg profile picture
        if (old_name != "random.jpg"):
            remove('src/imgurl/' + old_name)

    # update the profile_img_url in users_data
    users_data[user_id_to_email[str(auth_user_id)]]['profile_img_url'] = server_base_url + image_local_path

    src.information_io.write_info("auth_users_data", users_data)
    
    return {}


def valid_email(email):
    '''
    checks whether the given email is valid
    Arguments:
        email (string)
    Return Value:
        raise InputError if the input email is invalid
    '''    
    #creates a regular expression in order to validate emails
    regex = r'^[a-zA-Z0-9]+[._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}$'
    if not re.search(regex, email):
        raise InputError("Email is not valid!")
    else:
        pass

def check_user_valid(user_id):
    '''
    check whether the input auth_user_id is invalid
    Arguments:
        auth_user_id (int)
    Return Value:
        raise InputError if the input user_id is invalid
    '''
    user_is_valid = False    
    if isinstance(user_id, int) != True:
        raise InputError("Input user id is invalid!")

    users_data = read_info("auth_users_data")
    for email in users_data:
        if users_data[email]['auth_user_id'] == user_id:
            user_is_valid = True
    
    if not user_is_valid:
        raise InputError("Input user id is invalid!")

def check_name_valid(name):
    '''
    check whether the input name is between the range of 1 and 50 characters inclusive 
    Arguments:
        name (int)
    Return Value:
        raise InputError if the input user_id is invalid
    '''    
    if len(name) > 50 or len(name) < 1:
        raise InputError("Input name is invalid!")

