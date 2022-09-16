# message_index indicate the id of the message which will be send next time
# number_of_messages indicate the number of all messages in DREAM, 
# number_of_messages will change after using message_remove function, but message_index will not change after removing
'''
dm_message_data = 

{   
    'message_index : 1,
    'number_of_messages' : 1,

    # dm id is 0

    '0' :  
    [ 
        {   'message_id': 0
            'u_id': 1,
            'message': 'Hello world',
            'time_created': 1582426789,
        }
    ],
}
'''
dm_message_data = {}
