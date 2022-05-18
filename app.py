from datetime import datetime, timedelta
import hashlib
import json
from bson import ObjectId
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import jwt
from pymongo import MongoClient

SECRET_KEY = 'turtle'

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})

client = MongoClient('localhost', 27017)
db = client.turtle


@app.route("/")
def hello_world():
    return jsonify({'msg':'success'})   # 랜더탬플렛하면 연결할 수 있으나 jsonify 동시에 사용 안함


# # # # # # # # # # # # # 회원가입 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


@app.route("/signup", methods=["POST"])
def sign_up():
    data = json.loads(request.data) 

    email = data.get('email')   # =data['email'] 출력값 sugi  -> 값이 없으면 key오류떠서. get추천
    password = data.get('password') # 입력값이 없다면 출력값은 none으로 표시됨
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    if not email or not password:
        print('이메일이나 패스워드 없음')
        return jsonify({'msg':'정보를 입력해주세요'}), 405
    if '@' not in email:
        print('이메일을 다시')
        return jsonify({'msg':'이메일을 다시 입력해주세요'}), 400
    if db.user.find_one({"email":email}):
        print('가입된 메일')
        return jsonify({'msg':'가입이 된 이메일입니다.'}), 402 
    
    
    db.user.insert_one({'email':email, 'password':password_hash})
    print(email, password_hash)
    return jsonify({'msg':'가입 성공'})


# # # # # # # # # # # # # 로그인 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


@app.route("/login", methods=["POST"])
def login():
    # print(request)
    data = json.loads(request.data)
    # print(data)

    email = data.get("email")
    password = data.get("password")
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # print(password_hash)
    result = db.user.find_one({'email': email, 'password': password_hash})
    # print(result)

    if result is None:
        return jsonify({'msg': '아이디나 비밀번호가 옳지 않습니다.'}), 401

    payload = {
        'id': str(result["_id"]),
        'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    # print(token)
    return jsonify({'msg': 'success', 'token': token}), 200


# # # # # # # # # # # # # 메인 페이지 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# 토큰값으로 백엔드로 보내고 디비 조회 후 이메일 꺼내서 돌려보내주고 그걸로 프론트엔드 업데이트 


@app.route("/getuserinfo", methods=["GET"])
def get_user_info():
           
    token = request.headers.get('Authorization')  # check 2헤더와 바디의 차이점 공부하기
    # print(token)
    if not token:
        return jsonify({'msg':'no token'})
    # print(token)
    user = jwt.decode(token, SECRET_KEY, algorithms=['HS256']) # check 3
    # print(user)                                               
    result = db.user.find_one({'_id' : ObjectId(user["id"])})   # check 4 db저장내역 확인
    
    print(result)
    
    return jsonify({'msg':'success', 'email':result['email']})  #check5 -> 포스트맨 보면, token값만 나오다가 email도 같이 확인가능
    # return jsonify({"msg":"success"}) # check 1
    
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