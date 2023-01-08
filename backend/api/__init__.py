import json
import sqlite3
from flask_cors import CORS, cross_origin
from flask import Flask, session, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import yaml
from .routes import rest_api
from .models import db, Users
import logging

# conn = sqlite3.connect(r"C:\Users\srika\Desktop\Desktop\ES\skill_database_app\backend\api\apidata.db", check_same_thread=False)
# curs = conn.cursor()

app = Flask(__name__)
app.config.from_object('api.config.BaseConfig')
config = yaml.load(open('database.yaml'), Loader=yaml.Loader)
client = MongoClient(config['uri'], tls=True, tlsAllowInvalidCertificates=True)
database = client['skill_management']
logging.basicConfig(filename='application.log', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


db.init_app(app)
rest_api.init_app(app)
CORS(app)

# Setup database
@app.before_first_request
def initialize_database():
    db.create_all()

"""
   Custom responses
"""

@app.after_request
def after_request(response):
    """
       Sends back a custom error with {"success", "msg"} format
    """

    if int(response.status_code) >= 400:
        response_data = json.loads(response.get_data())
        if "errors" in response_data:
            response_data = {"success": False,
                             "msg": list(response_data["errors"].items())[0][1]}
            response.set_data(json.dumps(response_data))
        response.headers.add('Content-Type', 'application/json')
    return response

@app.route('/users', methods=['POST', 'GET'])
@cross_origin()
def data():
    # POST a data to database
    if request.method == 'POST':
        body = request.json
        Name = body['Name']
        Skill = body['Skill']
        Domain = body['Domain'] 
        Years = body['Years'] 
        Level = body['Level'] 
        # db.users.insert_one({
        database['users'].insert_one({
            "Name": Name,
            "Skill": Skill,
            "Domain":Domain,
            "Years":Years,
            "Level":Level
        })
        return jsonify({
            'status': 'Data is posted to MongoDB!',
            'Name': Name,
            'Skill': Skill,
            'Domain':Domain,
            'Years':Years,
            'Level':Level
        })
    
    # GET all data from database
    if request.method == 'GET':
        allData = database['users'].find()
        dataJson = []
        for data in allData:
            id = data['_id']
            Name = data['Name']
            Skill = data['Skill']
            Domain = data['Domain']
            Years = data['Years']
            Level = data['Level']
            dataDict = {
                'id': str(id),
                'Name': Name,
                'Skill': Skill,
                'Domain': Domain,
                'Years': Years,
                'Level': Level
            }
            dataJson.append(dataDict)
        # print(dataJson)
        return jsonify(dataJson)

@app.route('/users/<string:id>', methods=['GET', 'DELETE', 'PUT'])
@cross_origin()
def onedata(id):

    # GET a specific data by id
    if request.method == 'GET':
        data = database['users'].find_one({'_id': ObjectId(id)})
        id = data['_id']
        Name = data['Name']
        Skill = data['Skill']
        Domain = data['Domain']
        Years = data['Years']
        Level = data['Level']
        dataDict = {
            'id': str(id),
            'Name': Name,
            'Skill': Skill,
            'Domain':Domain,
            'Years':Years,
            'Level':Level
        }
        # print(dataDict)
        return jsonify(dataDict)
        
    # DELETE a data
    if request.method == 'DELETE':
        database['users'].delete_many({'_id': ObjectId(id)})
        print('\n # Deletion successful # \n')
        return jsonify({'status': 'Data id: ' + id + ' is deleted!'})

    # UPDATE a data by id
    if request.method == 'PUT':
        body = request.json
        Name = body['Name']
        Skill = body['Skill']
        Domain = body['Domain']
        Years = body['Years']
        Level = body['Level']

        database['users'].update_one(
            {'_id': ObjectId(id)},
            {
                "$set": {
                    "Name":Name,
                    "Skill":Skill,
                    "Domain": Domain,
                    "Years": Years,
                    "Level": Level
                }
            }
        )

        print('\n # Update successful # \n')
        return jsonify({'status': 'Data id: ' + id + ' is updated!'})

Name = ""
@app.route('/all_users', methods=['GET', 'POST'])
@cross_origin()
def fetch_all():
    global Name
    allData = database['users'].find()
    # all = [i for i in x]
    dataJson = []
    for data in allData:
        Name = data['Name']
        Skill = data['Skill']
        Domain = data['Domain']
        Years = data['Years']
        Level = data['Level']
        dataDict = {
            'Name': Name,
            'Skill': Skill,
            'Domain': Domain,
            'Years': Years,
            'Level': Level
        }
        dataJson.append(dataDict)
    return jsonify(dataJson)

# @app.route('/current_user', methods =['GET', 'POST'])
# def curr_user():
#     curs.execute('SELECT username FROM users WHERE username =?', (Name, ))
#     user = curs.fetchone()
#     name = ""
#     if user:            
#         session['loggedin'] = True
#         session['name'] = user
#         name = session['name']

#     else:
#         mesage = 'Please enter correct email / password !'
#     return jsonify(name)