import json

def write_info(filepath, data):
    """
    Usage   write_info("src/auth_data.txt", auth_user_data)
    Input   filepath
            data (can be int, list, dict, etc)
    """
    with open(filepath, 'w') as data_file:
        json_data = json.dumps(data)
        data_file.write(json_data)

def read_info(filepath):
    """
    Usage   auth_user_data = read_info("src/auth_data.txt")
    Input   filepath
    Output  data (can be int, list, dict, etc)
    """
    with open(filepath, 'r') as data_file:
        json_data = data_file.read()
        data = json.loads(json_data)
        return data
    
