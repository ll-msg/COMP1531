import json

def read_info(filepath):
    """
    Usage   auth_user_data = read_info("src/auth_data.txt")
    Input   filepath
    Output  data (can be int, list, dict, etc)
    """
    try:
        with open(filepath, 'r') as data_file:
            json_data = data_file.read()
            data = json.loads(json_data)
    except Exception:
        data = {}
    return data

def read_info_2(filepath, default_val):
    """
    Usage   auth_user_data = read_info("src/auth_data.txt")
    Input   filepath
    Output  data (can be int, list, dict, etc)
    """
    try:
        with open(filepath, 'r') as data_file:
            json_data = data_file.read()
            return json.loads(json_data)
    except Exception:
        return default_val
