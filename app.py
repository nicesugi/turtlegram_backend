from collections import UserString
import datetime
import hashlib
import json
from sre_constants import SUCCESS
from flask import Flask, jsonify, request
from flask_cors import CORS
from bson.objectid import ObjectId
import jwt

SECRET_KEY = 'turtle'

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.turtle


@app.route("/")
def hello_world():
    return jsonify({'msg':'success'})   # 랜더탬플렛하면 연결할 수 있으나 jsonify 동시에 사용 안함


@app.route("/signup", methods=["POST"])
def sign_up():
    data = json.loads(request.data) 

    email = data.get('email')   # 출력값 sugi  > 값이 없으면 key오류떠서. get추천
    password = data.get('password') # 출력값 0000
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    print(password_hash)
    
    result = db.users.find_one({
        'email' : email,
        'password' : password
    })
    print(result)
    
    if result is None:
        return jsonify({"msg":"아이디나 비밀번호가 옳지 않습니다"}), 401
    
    payload = {
        'id': str(result["_id"]),
        'exp': datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    print(token)
    
    return jsonify({"msg":"success", "token":token})


@app.route("/getuserinfo", methods=["GET"])
def get_user_info():
    # print(request.headers)         # check 2 헤더 찍히는거 확인  후 삭제 / 역할 체크
    # token = request.headers.get("Authorization")
    # if not token:
    #     return jsonify({"msg":"no token"})
    # print(token)
    user = jwt.decode(token, SECRET_KEY, algorithms=['HS256']) # check 3
    print(user)                                               # check 3 아이디랑 만료날짜 확인
    result = db.users.find_one({
        '_id' : ObjectId(user["id"])   # check 4 db저장내역 확인
    })
    
    print(result)
    
    return jsonify({"msg":"success", "email":result["email"]})  #check5  
    # return jsonify({"msg":"success"}) # check 1 후 삭제
    
    
    
    # db.user.insert_one({
    #     "email":email,
    #     "password":password
    #     })
    # return jsonify({'msg':'가입 완료'})              # db저장

 
if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)



# @app.route("/login", methods=["POST"])
# def log_in():
#     print(request)
#     data = json.loads(request.data) 
#     # print(request.form) #결과값--form 'id="sugi"' \-form 'password="1234"'html폼을 작성햇을때 가는형태
#     # print(request.data) #형태로는 데이터를 꺼내 쓸 수 없음. 겟을 써도 안되고 , 아이디 바로 써도 에러. 더 처리를 해서 밑의 제이슨 씀
#     print(data) #출력값 {'id': 'sugi', 'password': '0000'}
#     # print(data.get('id'))   #출력값 sugi
#     # print(data["password"]) #출력값 0000
#     # print(data.get('email'))   # 출력값 sugi  > 값이 없으면 key오류떠서. get추천
#     # print(data["password"]) # 출력값 0000email = data.get('email')   # 출력값 sugi  > 값이 없으면 key오류떠서. get추천
#     email = data.get('email')
#     password = data.get('password') # 출력값 0000
#     password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
#     # password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
#     print(password_hash)
    
#     result = db.user.find_ond({
#         "email":email, 
#         "password":password_hash
#     })
#     print(result)
    
#     return jsonify({'msg':'success'})






    
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
    
    
        # if email & 'email' >= 1: / ...str이라 타입오류 / db email과 입력값의 교집합의 개수가 1개 이상이라면?
    # if db.user.find_one(email) / ?? 기현튜터님이 제시했으나 모르겠음..
    
    
    
    #methods가 포스트라면
# @app.route("/login")
# def hello_login():
#     return jsonify({'msg':'로그인화묜'})
        # return jsonify('/turtlegram_frontend/login.html') 

# @app.route("/turtlegram_frontend/login.html", methods=["GET"])
# def hello():
#     return jsonify({'msg':'success'})

    
#     if '@' not in email:
#         return jsonify({'msg':'이메일형식이 아닙니다'}) 
# # 입력값에 @가 없으면 이메일 재입력 메세지
#     if db.user.find_one({"email":email}):
#         return jsonify({'msg':'이미 존재하는 이메일입니다'})    # 입력값이 email db에 있다면, 중복확인 메세지.

#     if space() in email:
#         return jsonify({'정보를 입력해주세요'})