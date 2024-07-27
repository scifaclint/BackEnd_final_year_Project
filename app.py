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
        userface = request_data['userFace']
        email = request_data['userEmail']
        user_data = get_userData(email)
        path_to_existing_face = user_data['facial_data']

        comparison_results = model.compare_faces(
            userface, path_to_existing_face)
        if comparison_results["status"] and (comparison_results['confidence'] > 90):

            return jsonify({"status": True, "message": "Faces matche"}), 200
        else:
            return jsonify({"status": False, "message": "Face did not matched"})

    else:
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
    request_data = request.get_json(force=True)
    userface = request_data['userFace']
    userEmail = request_data['userEmail']
    filename = secure_filename(request_data['filename'])

    try:
        enrol_status = enrollUser(userface)
        print(enrol_status)
        if enrol_status['status'] and (enrol_status['faces'] == 1):
            all_data = load_database()
            procesImage(userface, path, filename)
            for user in all_data['users']:
                if userEmail == user['email']:
                    user["facial_data"] = f"{path}/{filename}"
                    break
            save_database(all_data)

            return jsonify({"status": True, "message": "good to go!"})
        else:
            return jsonify({"status": False, "message": "No facial data in images"})
    except Exception as err:
        return jsonify({"status": False, "message": "Error Occured duing operations", "error": err})


@app.errorhandler(Exception)
def handle_error(e):
    app.logger.error(f"An unhandled error occurred: {str(e)}")
    return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = '../uploads'
    app.run(host='0.0.0.0', port=5000, debug=True)
