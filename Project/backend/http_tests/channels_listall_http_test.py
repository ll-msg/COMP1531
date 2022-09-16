import pytest
import requests
import json
from src import config
from src.error import InputError
from src.error import AccessError

@pytest.fixture
def set_up_one_user():
    requests.delete(config.url + 'clear/v1')
    r = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaildmail@gmail.com",
        "password" : "123abc!",
        "name_first" : "Obiwan",
        "name_last" : "Kenobi",
    })
    return_dic = r.json()
    return return_dic['token']

def test_channels_listall_success(set_up_one_user):
    #create two channels
    r_one = requests.post(config.url + '/channels/create/v2', json = {
        "token" : set_up_one_user,
        "name" : "Mondstadt",
        "is_public" : True,
    })
    channel_id_one = r_one.json()
    channel_id_one = channel_id_one['channel_id']
    r_two = requests.post(config.url + '/channels/create/v2', json = {
        "token" : set_up_one_user,
        "name" : "Liyue",
        "is_public" : False,
    })
    channel_id_two = r_two.json()
    channel_id_two = channel_id_two['channel_id']
    
    #creates a new user who is not part of either channel
    r_three = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "fragranceinthaw@gmail.com",
        "password" : "123abc!",
        "name_first" : "Tao",
        "name_last" : "Hu",
    })
    user_dic = r_three.json()
    token = user_dic['token']
    
    #assert that all channels are listed when function is called
    resp = requests.get(config.url + "/channels/listall/v2", params={'token': token})
    resp_data = resp.json()
    assert resp_data == {'channels':[{'channel_id' : channel_id_one, 'name' : 'Mondstadt'}, {'channel_id' : channel_id_two, 'name' : 'Liyue'}]}
