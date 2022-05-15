from collections import UserString
import hashlib
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from bson.objectid import ObjectId

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbturtle


@app.route("/")
def hello_world():
    return jsonify({'message':'success'})
    # 랜더탬플렛하면 연결할 수 있음.


@app.route("/signup", methods=["POST"])
def sign_up():
    # print(request)
    # print(request.form) #결과값--form 'id="sugi"' \-form 'password="1234"'html폼을 작성햇을때 가는형태
    # print(request.data) #형태로는 데이터를 꺼내 쓸 수 없음. 겟을 써도 안되고 , 아이디 바로 써도 에러. 더 처리를 해서 밑의 제이슨 씀
    data = json.loads(request.data) #21번 해결> 포스트맨 json 만듬
    # print(data) #출력값 {'id': 'sugi', 'password': '0000'}
    # print(data.get('id'))   #출력값 sugi
    # print(data["password"]) #출력값 0000
    # user_id = user.get('id')
    # user_id = db.user.find_one(repr(user['_id']))
    # user_id = str(ObjectId(''))
    email = data["email"]   #출력값 sugi 
    password = data["password"] #출력값 0000
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    db.user.insert_one({"email":email, "password":password_hash})
    return jsonify({'message':'success2'})
    


if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug=True)