from flask import Flask, jsonify, request
from facialmodel import load_database, save_database, get_userData
from facialmodel import procesImage
from werkzeug.utils import secure_filename
from model import model
import json
import logging
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Set the upload path
path = "./uploads"

tempfile = "./tempfiles"


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
    print(request_data)
    userData = load_database()

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
    else:
        return jsonify({"status": False, "message": "Error occured"}), 400


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


# done with this enrollment


@app.route("/api/signup", methods=['POST'])
def detect_analyse():
    request_data = request.get_json(force=True)
    base_64_image = request_data['image_base64']
    email = request_data['email']
    data = load_database()
    data_faces = model.load_face_data()
    model_results = model.enroll_face(base_64_image)

    if model_results['status'] and model_results['num_faces'] == 1:
        # face_token = model_results['data']['faces'][0]['face_token']
        # for user in data_faces['users']:
        #     if email == user['email']:
        #         user['facial_data'] = face_token
        #         break
        data_faces['users'].append({
            "email": email,
            "facial_data": base_64_image
        })
        model.save_face_data(data_faces)
        return jsonify({"status": True, "message": "facial data added successfully"}), 201
    else:
        return jsonify({"status": False, "message": "Errors Occured"}), 400


@app.route('/api/compareAuth', methods=["POST"])
def compareAuth():
    request_data = request.get_json(force=True)
    base_64_image = request_data['image_base64']
    email = request_data['email']
    data = model.load_face_data()

    for user in data['users']:
        if email == user['email']:
            face_token1 = user['facial_data']
            break
    compare_results = model.compare_faces(face_token1, base_64_image)

    if compare_results['status'] and compare_results['confidence'] >= 70.0:
        return jsonify({"status": True, "message": "Faces matched"}), 201
    else:
        return jsonify({"status": False, "message": "Error "}), 400


@app.errorhandler(Exception)
def handle_error(e):
    app.logger.error(f"An unhandled error occurred: {str(e)}")
    return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = './uploads'
    app.run(host='0.0.0.0', port=5000, debug=True)
