import face_recognition
import numpy as np
import json
from PIL import Image
import os
import uuid
import base64
from io import BytesIO

import cv2
from werkzeug.utils import secure_filename

tempFolder = "./tempfiles"


def load_database():
    """Load the facial data database."""
    if not os.path.exists('data.json'):
        raise FileNotFoundError('Database file not found')

    try:
        with open('./data.json', 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # If JSON is invalid, initialize an empty structure
        data = {"users": []}

    return data


def save_database(data):
    """Save the facial data database."""
    with open('./data.json', 'w') as f:
        json.dump(data, f, indent=4)


def enroll_face(input_type, file):

    """
    Enroll a user's face based on the input type and file.

    Args:
        email (str): Email of the user to enroll.
        input_type (str): Type of the input - 'picture' or 'video'.
        file (str): Path to the image or video file.

    Returns:
        dict: Enrollment result with facial data and messages.
    """

    if input_type == "picture":
        image = face_recognition.load_image_file(file)
        user_face_locations = face_recognition.face_locations(image)
        user_face_encodings = face_recognition.face_encodings(
            image, user_face_locations)

        # Check if any face was found
        if len(user_face_encodings) == 1:
            facial_data = user_face_encodings[0].tolist()
            return {'status:': True}
        elif len(user_face_encodings) > 1:
            return {'status': False, "message": "Multiple faces detected"}
        else:
            return {'status': False, "message": "No face detected"}

    elif input_type == 'video':
        video_capture = cv2.VideoCapture(file)
        face_detected = False
        facial_data = None

        while video_capture.isOpened():
            ret, frame = video_capture.read()
            if not ret:
                break

            rgb_frame = frame[:, :, ::-1]   # Convert BGR to RGB
            user_face_locations = face_recognition.face_locations(rgb_frame)
            user_face_encodings = face_recognition.face_encodings(
                rgb_frame, user_face_locations)

            if len(user_face_encodings) == 1:
                face_detected = True
                facial_data = user_face_encodings[0].tolist()
                break
            elif len(user_face_encodings) > 1:
                video_capture.release()
                return {'message': 'More than one face detected'}

        video_capture.release()

        if face_detected:
            database = load_database()

            return {'message': 'User not found'}
        else:
            return {'message': 'No face detected'}


def compare_faces(stored_facial_data, new_facial_data):
    """
    Compare stored facial data with new facial data.

    Args:
        stored_facial_data (list): Facial data of the stored user.
        new_facial_data (list): Facial data of the new user for authentication.

    Returns:
        dict: Authentication result message.
    """

    stored_encoding = np.array(stored_facial_data)
    new_user_encoding = np.array(new_facial_data)

    # Check dimensions and format
    if stored_encoding.ndim != 1 or new_user_encoding.ndim != 1:
        return {'message': 'Facial data is not in the correct format'}

    # Debugging print statements
    print(f"Stored Encoding Shape: {stored_encoding.shape}")
    print(f"New User Encoding Shape: {new_user_encoding.shape}")

    matches = face_recognition.compare_faces(
        [stored_encoding], new_user_encoding)

    if True in matches:
        return {"status": True, 'message': 'Face matched'}
    else:
        return {"status": False, 'message': 'Face did not match'}


def convert_base64_npArray(base, email):
    delete_files_in_directory(tempFolder)

    # decode base_64 data from server
    filename = secure_filename(email)

    tempPath = "./tempfiles/"

    # with open(os.path.join(tempPath, filename), "wb") as f:
    #     f.write(decode_facial)
    procesImage(base, tempPath, filename)
    print("image Saved")
    print(f"{tempPath}{filename}")
    data = f"{tempPath}{filename}"
    print(type(data))
    return (f"{tempPath}{filename}")


# clean tempfiles


def delete_files_in_directory(directory_path):
    try:
        # Iterate through each file in the directory
        for filename in os.listdir(directory_path):
            # Create the full file path
            file_path = os.path.join(directory_path, filename)
            # Check if it's a file and delete it
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


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
