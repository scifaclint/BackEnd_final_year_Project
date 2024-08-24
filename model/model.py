import base64
import requests
from dotenv import load_dotenv
import os
import json
load_dotenv()

api_key = os.getenv("api_key")
api_secret = os.getenv("api_secret")
url_detect = os.getenv("url_detect")
url_compare = os.getenv("url_compare")


def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
    base64_encoded_data = base64.b64encode(image_data)
    return base64_encoded_data


def enroll_face(image_64):
    try:
        response = requests.post(url_detect, {
            "api_key": api_key,
            "api_secret": api_secret,
            "image_base64": image_64

        })
        data = response.json()
        return {"status": True, "data": data, "num_faces": len(data['faces'])}
    except Exception as err:
        return ({"status": False, "message": "Error occurred", "error": err})


def compare_faces(face_token, old_userImage):
    """_summary_

    Args:
        image_64_new (_type_): already in base64
        old_userImage (_type_): path of image would be changed

    Returns:
        _type_: number of faces detected from api call
    """

    try:
        response = requests.post(url_compare, {
            "api_key": api_key,
            "api_secret": api_secret,
            "image_base64_1": face_token,
            "image_base64_2": old_userImage

        })
        print(response.json())
        data = response.json()
        return ({"status": True, "confidence": data['confidence']})
    except Exception as err:
        return ({"status": False, "message": err})


def load_face_data():
    with open("./faces.json", "r") as f:
        data = json.load(f)
        return data


def save_face_data(data):
    with open("./faces.json", "w") as f:
        json.dump(data, f, indent=4)

# face_token = 'dd501442961502eadc323efb8117efd8'
# token2 = "0ed0794bd38925e33b3e85f2286b2b69"
# with open('./uploads/scitest@gmail.com.jpg', 'rb') as f:
#     image_base = f.read()
#     f.close()

# base_64 = base64.b64encode(image_base).decode('utf-8')

# print(compare_faces(face_token, base_64))

# # print(enroll_face(bas


