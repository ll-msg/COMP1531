

"""
File names where auth data is stored
"auth_users_data"
"auth_total_users"
"auth_user_id_to_email"
"auth_handle_list"
"auth_password_reset_dict"
"""



"""
stores user data upon registration
auth_user_id are assigned from 0 onwards

structure of users_data
users_data = {'admin@admin.com' : {
        'auth_user_id': 0,
        'first_name' : 'admin_fn',
        'last_name' : 'admin_ln',
        'password' : hashlib.sha256('admin1234'.encode()).hexdigest(),
        'handle' : 'admin_fnadmin_ln',
        'sessions' : [],        # list containing all active session ids (ints)
        'session_count' : 0,    # number of active sessions (int)
        'profile_img_url' : profile_img_url,
    },
    ...
}
"""


"""
stores total nuber of users registered
"""


"""
dict that maps auth_user_id to emails (saves time, O(1) instead of O(N)) (N is the number of users registered)

user_id_to_email = {
    auth_user_id : email,
    ...
}
"""


"""
set of all handles (saves time, O(1) instead of O(S)) (S is the number of active sessions)

handle_set = {
    handle1,
    handle2,
    ...
}
"""

"""
stores the secret codes for all password reset operations.
Each email can have only 1 secret code at most and this is deleted once the password is reset.
password_reset_dict = {"email":"secret_code"}
"""
