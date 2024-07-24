from flask import Flask, jsonify, request
from facialmodel import load_database, save_database, enroll_face, compare_faces, convert_base64_npArray, delete_files_in_directory
from facialmodel import procesImage
from werkzeug.utils import secure_filename
import os
import sys
import base64
import json
import logging
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Set the upload path
path = "./uploads"
tempFolder = "./tempfiles"
imageName = "temImage"


def getId(list):
    if len(list) == 0:
        return 1
    else:
        return len(list) + 1


@app.route('/')
def hello():
    return "Hello "


@app.route('/api/data', methods=['POST'])
def get_data():
    try:
        request_data = request.get_json(force=True)
        app.logger.info(f"Received data: {request_data}")
        email = request_data.get("email")
        if not email:
            return jsonify({"error": "Email not provided"}), 400
        with open("./data.json", "r") as file:
            all_users = json.load(file)
        for user in all_users["users"]:
            if user.get("email") == email:
                data_h = jsonify(user)
                return data_h

        return jsonify({"error": "User not found"}), 404

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

# both transfer and login


@app.route('/api/transfer', methods=["POST"])
def transfer():
    request_data = request.get_json(force=True)
    userData = load_database()

    if request_data['type'] == "login":

       # Load existing data

        # Get sender data
        getSenderData = next(
            (user for user in userData['users'] if user["email"] == sender), None)

        if not getSenderData:
            return jsonify({"error": "Sender not found"}), 404

        senderExistFace = getSenderData['facial_data']
        senderNewFace = convert_base64_npArray(
            request_data['userFace'], "tempfile.jpg")

        # compare facial data
        comparison_result = compare_faces(
            stored_facial_data=senderExistFace, new_facial_data=senderNewFace)

        if comparison_result.status:
            return jsonify({"message": "matched"}), 200
        else:
            return jsonify({"message": "error"}), 400

    try:
        app.logger.info(f"Received data: {request_data}")
        sender = request_data.get("sender")
        receiver = request_data.get("receiver")
        amount = request_data.get('addToReceiver')
        transactions = request_data.get('transactions')
        substractSendr = request_data.get("subsctractSender")

        if request_data:
            # update receiver
            for userD in userData['users']:
                if receiver == userD['email']:
                    userD['balance'] = userD['balance'] + amount
                    userD['transactions'].append({
                        "id": getId(userD['transactions']),
                        "type": "received",
                        "amount": amount,
                        "date": transactions['date']
                    })
                    break

            for userD in userData['users']:
                # Update sender data
                if sender == userD['email']:
                    userD['balance'] = userD['balance'] - \
                        substractSendr
                    userD['transactions'].append({
                        "id": getId(userD['transactions']),
                        "type": "paid",
                        "amount": amount,
                        "date": transactions['date']
                    })
                    break

        # now save data
        save_database(userData)

        return jsonify({"message": "Transaction Complete"}), 200

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/addUser', methods=["POST"])
def addUser():
    try:
        request_data = request.get_json(force=True)
        app.logger.info(f"Received data: {request_data}")
        if not request_data:
            return jsonify({"message": "Error adding user"}), 400

        userd = load_database()
        userd.get("users").append(request_data)
        save_database(userd)
        return jsonify({"message": "User added "}), 201

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/faceEnroll', methods=["POST"])
def enrollUser():
    try:
        data = request.get_json(force=True)
        app.logger.info(f"Received data: {data}")

        email = data.get('userEmail')
        facialData = data.get('userFace')
        filename = secure_filename(data.get('filename'))

        if not all([email, facialData, filename]):
            return jsonify({"error": "Incomplete data provided"}), 400

        file_path = f"{path}/{filename}"
        decode_facial = base64.b64decode(facialData)
        enroll_face_results = enroll_face(
            input_type="picture", file=convert_base64_npArray(decode_facial, f"{imageName}.jpg"))

        # Save picture
        if enroll_face_results.status:
            # with open(os.path.join(path, filename), 'wb') as f:
            #     f.write(decode_facial)
            procesImage(decode_facial, path, filename)
            database = load_database()
            for usermail in database['users']:
                if email == database["email"]:
                    usermail['facial_data'] = file_path
                    break
            save_database(database)
            delete_files_in_directory(tempFolder)

            return jsonify({"message": "Facial data added"}), 200
        else:
            return jsonify({"error": ""}), 400

    except Exception as err:
        app.logger.error(f"An error occurred: {str(err)}")
        return jsonify({"error": str(err)}), 500


@app.route('/api/verifyUser', methods=["POST"])
def verifyFace_model():
    try:
        request_data = request.get_json(force=True)
        app.logger.info(f"Received data: {request_data}")

        userEmail = request_data.get('email')
        facial_data_new = request_data.get('userFace')

        database = load_database()

        for userData in database['users']:
            if userEmail == userData['email']:
                location_user_Face = userData['facial_data']
                break
        compare_results = compare_faces(
            stored_facial_data=location_user_Face, new_facial_data=convert_base64_npArray(facial_data_new, "tempimage.jpg"))
        if compare_results.status:
            return jsonify({"message": "faces matched"}), 201
        # Save new picture
        else:
            return jsonify({"message": "faces not matched"}), 401

        # Authenticate face
    except Exception as err:
        return jsonify({"message": "error occured"}), 401


@app.errorhandler(Exception)
def handle_error(e):
    app.logger.error(f"An unhandled error occurred: {str(e)}")
    return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = '../uploads'
    app.run(host='0.0.0.0', port=5000, debug=True)
