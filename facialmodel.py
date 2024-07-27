import json
from PIL import Image
import os
from io import BytesIO

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


def get_userData(email):
    """_summary_

    Args:
        email (_type_): email only 

    Returns:
        _type_: dict object of user
    """
    data = load_database()
    for user in data['users']:
        if email == user['email']:
            return user
        break


def save_database(data):
    """Save the facial data database."""
    with open('./data.json', 'w') as f:
        json.dump(data, f, indent=4)


# process base64 image and save to rgb
def procesImage(base64_string, output_path, filename):

    with Image.open(BytesIO(base64_string)) as img:
        # Convert to RGB if it's not already
        if img.mode != 'RGB':
            img = img.convert('RGB')
            print("image was not RGB")
        full_path = os.path.join(output_path, filename)
        print(full_path)
        # Save the image
        img.save(full_path)
