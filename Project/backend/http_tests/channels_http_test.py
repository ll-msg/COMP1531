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

def test_channels_create(set_up_one_user):
    r = requests.post(config.url + '/channels/create/v2', json = {
        "token" : set_up_one_user,
        "name" : "Republic",
        "is_public" : True,
    })
    test_dic = r.json()
    channel_id = test_dic['channel_id']
    assert test_dic == {"channel_id" : channel_id}

def test_channels_create_input_error(set_up_one_user):
    assert requests.post(config.url + '/channels/create/v2', json = {
        "token" : set_up_one_user,
        "name" : "Republic" * 100,
        "is_public" : True,
    }).status_code == 400

def test_channels_list_success(set_up_one_user):
    # create a channel
    r = requests.post(config.url + '/channels/create/v2', json = {
        "token" : set_up_one_user,
        "name" : "Republic",
        "is_public" : True,
    })
    channel_id = r.json()
    channel_id = channel_id['channel_id']
    resp = requests.get(config.url + "/channels/list/v2", params={'token': set_up_one_user})
    resp_data = resp.json()
    assert resp_data == {'channels':[{'channel_id' : channel_id, 'name' : 'Republic'}]}
    requests.delete(config.url + 'clear/v1')