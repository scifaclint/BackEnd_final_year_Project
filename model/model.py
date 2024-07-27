import base64
import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("api_key")
api_secret = os.getenv("api_secret")
url_detect = os.getenv("url_detect")
url_compare = os.getenv("url_compare")


def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
        base64_encoded_data = base64.b64encode(image_data)
        base64_string = base64_encoded_data.decode('utf-8')
    return base64_string


def enroll_face(image_64):
    try:
        response = requests.post(url_detect, {
            "api_key": api_key,
            "api_secret": api_secret,
            "image_base64": image_64

        })
        data = response.json()

        # returns the length of faces detected
        return {"status": True, "faces": len(data['faces'])}
    except Exception as err:
        return ({"status": False, "message": "Error occurred", "error": err})



def compare_faces(image_64_new, old_userImage):
    """_summary_

    Args:
        image_64_new (_type_): already in base64
        old_userImage (_type_): path of image would be changed

    Returns:
        _type_: number of faces detected from api call
    """
    image_64_old_image = encode_image_to_base64(old_userImage)
    try:
        response = requests.post(url_compare, {
            "api_key": api_key,
            "api_secret": api_secret,
            "image_base64_1": image_64_new,
            "image_base64_2": image_64_old_image

        })
        data = response.json()
        return ({"status": True, "confidence": data['confidence']})
    except Exception as err:
        return ({"status": False, "message": err})
