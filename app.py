from collections import UserString
import hashlib
import json
from flask import Flask, jsonify, request
import flask
from flask_cors import CORS
from bson.objectid import ObjectId

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.turtle


@app.route("/")
def hello_world():
    return jsonify({'msg':'success'})
    # 랜더탬플렛하면 연결할 수 있음.


@app.route("/signup", methods=["POST"])
def sign_up():
    data = json.loads(request.data) #21번 해결> 포스트맨 json 만듬

    email = data.get('email')   #출력값 sugi  > 값이 없으면 key오류떠서. get추천
    password = data["password"] #출력값 0000
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    if '@' not in email:
       return jsonify({'result': 'try_again','msg':'이메일을 다시 입력해주세요'}) 
       # 입력값에 @가 없으면 이메일 재입력 메세지
    
    # if email & 'email' >= 1: / ...str이라 타입오류 / db email과 입력값의 교집합의 개수가 1개 이상이라면?
    # if db.user.find_one(email) / ?? 기현튜터님이 제시했으나 모르겠음..
    if db.user.find_one({"email":email}):
        return jsonify({'msg':'가입이 된 이메일입니다.'})
    # 입력값이 email db에 있다면, 중복확인 메세지.
    
    db.user.insert_one({"email":email, "password":password_hash})
    return jsonify({'msg':'가입완료'})
    # 입력값에 @가 있고, email db에 없다면, db저장

#methods가 포스트라면
        # if flask.request.method == 'GET':
        # return jsonify('/turtlegram_frontend/login.html') 

# @app.route("/turtlegram_frontend/login.html", methods=["GET"])
# def hello():
#     return jsonify({'msg':'success'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug=True)
    
        # user_id = user.get('id')
    # user_id = db.user.find_one(repr(user['_id']))
    # user_id = str(ObjectId(''))
    
    
    
    #아래는 데이터가 어떻게 나오는지 print해본 것. def sign_up(): 부분 밑에 넣어 확인가능
    # print(request)
    # print(request.form) #결과값--form 'id="sugi"' \-form 'password="1234"'html폼을 작성햇을때 가는형태
    # print(request.data) #형태로는 데이터를 꺼내 쓸 수 없음. 겟을 써도 안되고 , 아이디 바로 써도 에러. 더 처리를 해서 밑의 제이슨 씀
    # print(data) #출력값 {'id': 'sugi', 'password': '0000'}
    # print(data.get('id'))   #출력값 sugi
    # print(data["password"]) #출력값 0000