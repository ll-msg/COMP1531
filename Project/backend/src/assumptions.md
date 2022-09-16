1. when a user who is already a member of that channel join in that channel, channel_join_v1 function will not make any changes.

2. The first person to register as a user in Dream is the global onwer and has the permission to join any channel. Once joined the channel, the global owner will be added as the owner of the channel by default.

3. If the user is already a participant of this channel, the channel_invite_v1 function will do nothing.

4. The channel_id in the channel_create function will start from 0.

5. Then auth_user_id in auth_register should be start from 0.

6. The message id starts from 0.

7. Message_send funtion doesn't send message with empty string.

8. Channel_message and Dm_message will skip any deleted or removed message.

9. Assume the input channel_id in message_send_v2 is refer to a valid channel.

10. The deleted message will only delete the string of the message, other information will be retained.

11. Assume input empty string in message_edit_v2 function is the same as removing it with meesage_remove_v1

12. The length of message in message share function do not have limitation and the og_message_id is refer to a valid message id

13. Any valid user could share origin message even the user has not join the channel or dm this origin is sent to (if the user have authority to call this function)

14. shared message will have the format str('message'--'og_message')

15. The only admin cannot set their own permission id to 2

16. DMs are considered private so user remove does not wipe messages in the users dms

17. Notifications are considered non-essential and dont need to be persistent

18. When requesting a password reset, if the email does not belong to a registered user, raise an InputError