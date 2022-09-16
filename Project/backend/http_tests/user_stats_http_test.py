import pytest
import requests
import json
from src import config
from src.error import InputError
from src.error import AccessError


@pytest.fixture
def input():
    requests.delete(config.url + 'clear/v1')
    rsp_channel_owner = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vai@gma.com",
        "password" : "123abc!",
        "name_first" : "Obi",
        "name_last" : "K",
    })
    owner = rsp_channel_owner.json()
    owner_token = owner['token']

    rsp_channel_member = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaidddd@gma.com",
        "password" : "123a444bc!",
        "name_first" : "Obi",
        "name_last" : "KWWWW",
    })
    member = rsp_channel_member.json()
    member_token = member['token']

    rsp_not_member = requests.post(config.url + '/auth/register/v2', json = {
        "email" : "vaidddsddd@gma.com",
        "password" : "123awww444bc!",
        "name_first" : "Owwwbi",
        "name_last" : "KWWWW",
    })
    not_member = rsp_not_member.json()
    not_member_token = not_member['token']

    requests.post(config.url + '/channels/create/v2', json = {
        "token" : owner_token,
        "name" : "Republic",
        "is_public" : True,
    })

    requests.post(config.url + '/dm/create/v1', json = {
        "token" : owner_token,
        "u_ids" : [member_token]
    })


    #                   0           1            2                
    return_list = [owner_token, member_token, not_member_token]

    return return_list


def test_user_stats(input):
    resp = requests.get(config.url + '/user/stats/v1', params = {
        "token" : input[0],
    })
    resp_data = resp.json()
    assert resp_data["user_stats"]["channels_joined"][-1]["num_channels_joined"] == 1

def test_users_stats(input):
    resp = requests.get(config.url + '/users/stats/v1', params = {
        "token" : input[1],
    })
    resp_data = resp.json()
    assert resp_data["dreams_stats"]["channels_exist"][-1]["num_channels_exist"] == 1
