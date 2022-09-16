from json import dumps
from flask import Flask, request, send_from_directory
from flask_mail import Mail, Message
from flask_cors import CORS
from src.error import InputError
from src import config
from src.error import AccessError
import src.auth_data as auth_data
import src.dm
import src.auth
import src.other
import src.admin
import src.notifications

from src.message import message_send_v2, message_remove_v1, message_edit_v2, message_senddm_v1, message_share_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1, message_sendlater_v1, message_sendlaterdm_v1
from src.channels import channels_list_v2, channels_listall_v2, channels_create_v2
from src.channel import channel_details_v2, channel_invite_v2, channel_join_v2, channel_messages_v2, channel_addowner_v1, channel_removeowner_v1, channel_leave_v1
from src.user_stats import user_stats_v1, users_stats_v1
from src.user import user_profile_v2, user_profile_setemail_v2, user_profile_sethandle_v1, user_profile_setname_v2
from src.standup import standup_start_v1, standup_active_v1, standup_send_v1

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

mail= Mail(APP)
APP.config['MAIL_SERVER']='smtp.gmail.com'
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USERNAME'] = 'thu13bdorito@gmail.com'
APP.config['MAIL_PASSWORD'] = 'totallyrandompassword'
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True
mail = Mail(APP)


APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)


# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route("/auth/login/v2", methods=['POST'])
def login():
    data = request.get_json()
    return dumps(src.auth.auth_login_v2(data['email'], data['password']))


@APP.route("/auth/register/v2", methods=['POST'])
def register():
    data = request.get_json()
    return dumps(src.auth.auth_register_v2(data['email'], data['password'], data['name_first'], data['name_last']))


@APP.route("/auth/logout/v1", methods=['POST'])
def logout():
    data = request.get_json()
    return dumps(src.auth.auth_logout_v2(data['token']))

@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    src.other.clear_v1()
    return dict()

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create():
    data = request.get_json()
    return dumps(channels_create_v2(data['token'], data['name'], data['is_public']))

@APP.route("/channels/list/v2", methods=['GET'])
def channels_list():
    token = request.args.get('token')
    return dumps(channels_list_v2(token))

@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall():
    token = request.args.get('token')
    return dumps(channels_listall_v2(token))

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_message_route():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    return dumps(channel_messages_v2(token, channel_id, start))

@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_route():
    data = request.get_json()
    return dumps(channel_join_v2(data['token'], data['channel_id']))

@APP.route("/channel/details/v2", methods=['GET'])
def channel_detail_route():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    return dumps(channel_details_v2(token,channel_id))

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_route():
    data = request.get_json()
    return dumps(channel_invite_v2(data['token'], data['channel_id'], data['u_id']))

@APP.route("/message/send/v2", methods=['POST'])
def message_send_route():
    data = request.get_json()
    return dumps(message_send_v2(data['token'], data['channel_id'], data['message']))

@APP.route("/message/edit/v2", methods=['PUT'])
def message_edit_route():
    data = request.get_json()
    return dumps(message_edit_v2(data['token'], data['message_id'], data['message']))

@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove_route():
    data = request.get_json()
    return dumps(message_remove_v1(data['token'], data['message_id']))

@APP.route("/message/share/v1", methods=['POST'])
def message_share_route():
    data = request.get_json()
    return dumps(message_share_v1(data['token'], data['og_message_id'], data['message'], data['channel_id'], data['dm_id']))

@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm_route():
    data = request.get_json()
    return dumps(message_senddm_v1(data['token'], data['dm_id'], data['message']))
@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    data = request.get_json()
    return dumps(src.dm.dm_create_v1(data['token'], data['u_ids']))

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    data = request.args.get('token')
    return dumps(src.dm.dm_list_v1(data))

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    src.dm.dm_remove_v1(data['token'], data['dm_id'])
    return {}

@APP.route("/dm/invite/v1", methods=['POST'])
def dm_invite():
    data = request.get_json()
    return dumps(src.dm.dm_invite_v1(data['token'], data['dm_id'], data['u_id']))

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    data = request.get_json()
    return dumps(src.dm.dm_leave_v1(data['token'], data['dm_id']) )

@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))
    return dumps(src.dm.dm_messages_v1(token, dm_id, start))

@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    return dumps(src.dm.dm_details_v1(token, dm_id))

@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    data = request.get_json()
    return dumps(channel_addowner_v1(data['token'], data['channel_id'], data['u_id']))

@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    data = request.get_json()
    return dumps(channel_removeowner_v1(data['token'], data['channel_id'], data['u_id']))

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    data = request.get_json()
    return dumps(channel_leave_v1(data['token'], data['channel_id']))

@APP.route("/user/profile/v2", methods=['GET'])
def user_profile():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    return dumps(user_profile_v2(token, u_id))

@APP.route("/user/profile/setname/v2", methods=['PUT'])
def user_profile_setname():
    data = request.get_json()
    return dumps(user_profile_setname_v2(data['token'], data['name_first'], data['name_last']))

@APP.route("/user/profile/setemail/v2", methods=['PUT'])
def user_profile_setemail():
    data = request.get_json()
    return dumps(user_profile_setemail_v2(data['token'], data['email']))

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_profile_sethandle():
    data = request.get_json()
    return dumps(user_profile_sethandle_v1(data['token'], data['handle_str']))

@APP.route("/users/all/v1", methods=['GET'])
def users_all():
    token = request.args.get('token')
    return dumps(src.other.users_all_v1(token))

@APP.route("/search/v2", methods=['GET'])
def search_v2():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    return dumps(src.other.search_v2(token, query_str))

@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_remove():
    data = request.get_json()
    return dumps(src.admin.user_remove_v1(data['token'], data['u_id']))

@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_cpm():
    data = request.get_json()
    return dumps(src.admin.user_permission_change_v1(data['token'], data['u_id'], data['permission_id']))

@APP.route("/notifications/get/v1", methods=['GET'])
def notification_get():
    token = request.args.get('token')
    return dumps(src.notifications.notification_message_get_v1(token))

@APP.route("/user/stats/v1", methods=['GET'])
def user_stats():
    token = request.args.get('token')
    return user_stats_v1(token)

@APP.route("/users/stats/v1", methods=['GET'])
def users_stats():
    token = request.args.get('token')
    return users_stats_v1(token)
@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def passwordreset_request():
    data = request.get_json()
    reset_code = src.auth.auth_passwordreset_request_v1(data['email'])
    msg = Message('Password reset request', sender = 'thu13bdorito@gmail.com', recipients = [data['email']])
    msg.body = "Your secret code to reset your password is - " + reset_code
    mail.send(msg)
    return {}

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def passwordreset_reset():
    data = request.get_json()
    src.auth.auth_passwordreset_reset_v1(data['reset_code'], data['new_password'])
    return {}

@APP.route('/message/sendlater/v1', methods=['POST'])
def channel_message_later():
    data = request.get_json()
    return dumps(message_sendlater_v1(data['token'], data['channel_id'], data['message'], data['time_sent']))

@APP.route('/message/sendlaterdm/v1', methods=['POST'])
def dm_message_later():
    data = request.get_json()
    return dumps(message_sendlaterdm_v1(data['token'], data['dm_id'], data['message'], data['time_sent']))

@APP.route('/message/react/v1', methods=['POST'])
def react_message():
    data = request.get_json()
    return dumps(message_react_v1(data['token'], data['message_id'], data['react_id']))

@APP.route('/message/unreact/v1', methods=['POST'])
def unreact_message():
    data = request.get_json()
    return dumps(message_unreact_v1(data['token'], data['message_id'], data['react_id']))

@APP.route('/message/pin/v1', methods=['POST'])
def pin_message():
    data = request.get_json()
    return dumps(message_pin_v1(data['token'], data['message_id']))

@APP.route('/message/unpin/v1', methods=['POST'])
def unpin_message():
    data = request.get_json()
    return dumps(message_unpin_v1(data['token'], data['message_id']))

@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    data = request.get_json()
    return dumps (standup_start_v1(data['token'], data['channel_id'], data['length']))

@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(standup_active_v1(token, channel_id))

@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    data = request.get_json()
    return dumps(standup_send_v1(data['token'], data['channel_id'], data['message']))

@APP.route("/imgurl/<path:path>")
def static_send_from_dir(path):
    return send_from_directory('imgurl', path)

@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def pf_upload():
    data = request.get_json()
    token = data['token']
    img_url = data['img_url']
    x_start = data['x_start']
    y_start = data['y_start']
    x_end = data['x_end']
    y_end = data['y_end']
    server_base_url = request.url_root
    return src.user.user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end, server_base_url)

if __name__ == "__main__":
    APP.run(port=config.port) # Do not edit this port

