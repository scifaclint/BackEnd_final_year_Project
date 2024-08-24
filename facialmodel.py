import json
import os

from werkzeug.utils import secure_filename


def load_database():
    """Load the facial data database."""
    if not os.path.exists('data.json'):
        raise FileNotFoundError('Database file not found')

    try:
        with open('./data.json', 'r') as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError:
        # If JSON is invalid, initialize an empty structure
        data = {"users": []}


def get_userData(data, email):
    """_summary_

    Args:
        email (_type_): email only 

    Returns:
        _type_: dict object of user
    """
    for user in data['users']:
        if email == user['email']:
            return user


def save_database(data):
    """Save the facial data database."""
    with open('./data.json', 'w') as f:
        json.dump(data, f, indent=4)
