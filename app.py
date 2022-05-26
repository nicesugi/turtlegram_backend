from datetime import date, datetime, timedelta
from functools import wraps
import hashlib
import json
from bson import ObjectId
from flask import Flask, abort, jsonify, request, Response
from flask_cors import CORS
import jwt
from pymongo import MongoClient

SECRET_KEY = 'turtle'

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})

client = MongoClient('localhost', 27017)
db = client.turtle

# # # # # # # # # # # # # 회원가입 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# *args: 리스트형태로 인자가 얼마든지 들어가도됨/ **kwargs: 뭐뭐는 뭐.형태로 키워드가 있고 값이 있고 인식을 할 수 있다는 뜻
# 들어가야 user말고도 다른걸 넣어도 function 작동
def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'Authorization' in request.headers:
            abort(401)
        token = request.headers['Authorization']
        try:
            user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except:
            abort(401)
        return f(user, *args, **kwargs)
    return decorated_function
# decorated_function 붙이면 모든 함수에서 유저를 가져오면 그대로 유저값을 이용할 수 있게 됨.


@app.route("/")
@authorize   
def hello_world(user):
    print(user)
    return jsonify({'msg':'success'})   # 랜더탬플렛하면 연결할 수 있으나 jsonify 동시에 사용 안함


# # # # # # # # # # # # # 회원가입 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


@app.route("/signup", methods=["POST"])
def sign_up():
    data = json.loads(request.data) 

    email = data.get('email')   # =data['email'] 출력값 sugi  -> 값이 없으면 key오류떠서. get추천
    password = data.get('password') # 입력값이 없다면 출력값은 none으로 표시됨
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    if not email or not password:
        # print('이메일이나 패스워드 없음')
        return jsonify({'msg':'정보를 입력해주세요'}), 405
    if '@' not in email:
        # print('이메일을 다시')
        return jsonify({'msg':'이메일을 다시 입력해주세요'}), 400
    if db.user.find_one({"email":email}):
        # print('가입된 메일')
        return jsonify({'msg':'가입이 된 이메일입니다.'}), 402 
    
    
    db.user.insert_one({'email':email, 'password':password_hash})
    # print(email, password_hash)
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
@authorize 
def get_user_info(user):
    # def()에 user써서  user = user 의 내용으로  다음 바로 result해서 간단히 만들 수 도 있음 ! result전까지 주석
    # token = request.headers.get('Authorization')   
    # # print(token)
    # if not token:
    #     return jsonify({'msg':'no token'})
    # # print(token)
    # user = jwt.decode(token, SECRET_KEY, algorithms=['HS256']) # check 3
    # # print(user)                                               
    result = db.user.find_one({'_id' : ObjectId(user["id"])})   
    
    print(result)
    
    return jsonify({'msg':'success', 'email':result['email'], 'id':user['id']})  
    # return jsonify({"msg":"success"}) # check 1
    
    # db.user.insert_one({
    #     "email":email,
    #     "password":password
    #     })
    # return jsonify({'msg':'가입 완료'})              # db저장


# # # # # # # # # # # # # 게시글 # # # # # # # # # # # # # # # # # # # # #
## 오브젝트 아이디랑 값이 다름. 프론트엔드에 보여주기 위한 값.  유저의 아이디값은 실제로 조회하기 위한 포링키? 포린키?

@app.route("/article", methods=["POST"])
@authorize
def post_article(user):
    data = json.loads(request.data)
    print(data)

    db_user = db.user.find_one({'_id': ObjectId(user.get('id'))})

    now = datetime.now().strftime('%H:%M:%S')
    doc = {
        'title': data.get('title', None),
        'content': data.get('content', None),
        'user': user['id'],
        'user_email': db_user['email'],
        'time': now,
    }
    print(doc)

    db.article.insert_one(doc)

    return jsonify({'message': 'success'})

 
 # # # # # # # # # # # # # 게시글 # # # # # # # # # # # # # # # # # # # # #
 # 게시글을 작성한 아이디 정보(아이디/내용/시간/제목/유저/이메일)를 다 db에 저장해줌
 # print(articles)  내가 작성했던 글들이 모두 찍힘. 그치만 ObjectId  때문에 오류가 날 수 있고, 방지하기 위해 str 해주기.
 # 덤프를 사용할 수 있지만 for문 사용하여 str으로 바꿔줄 거임.
 # print(article.get("title"))  for문 잘 돌아가는지, 타이틀만 뽑아서 확인해봄
 # return jsonify({'msg':'success', 'article':article}) 성공적으로 ObjectId 값이 String으로 바껴서 들어옴 ->db 확인가능
 
@app.route("/article", methods=["GET"])
def get_article():
    articles = list(db.article.find())  
    # print(articles) 
    for article in articles:
        # print(article.get("title")) 
        article["_id"] = str(article["_id"])
    return jsonify({'msg':'success', 'articles':articles})
    
    
# # # # # # 변수명 url  # # # # # # # # # # # # # # # # # # # # # # # # # # # #  
#  article_id 는 변수 ! 포스트맨에  {{base_url}}/article/213980 이렇게 써보고,
# 출력값 포스트맨 {"article_id": "213980","message": "success"}으로 app.py 터미널(출력)에도 뜨는지 확인!
    
    
@app.route("/article/<article_id>", methods=["GET"])
def get_article_detail(article_id):
    # print(article_id)  
    article = db.article.find_one({"_id": ObjectId(article_id)})
    # print(article)
    article["_id"] = str(article["_id"])
    
    # return jsonify({'message': 'success', 'article_id': article_id}) #-> print(article_id) 확인 후에 주석처리
    return jsonify({'message': 'success', 'article': article})
 
 
  # # # # # # # # # # #  게시글 수정 PATCH  # # # # # # # # # # # # # # # # # # # # # #  
# 동일한 url 리소스이기 때문에 같은 주소를 같고 하는 행위가 다르기때문에 메소드만 다름. 이런게 좋은 api설계임
# 게시글은 누구나 볼수있지만 회원가입안해도 되지만 패치는 회원, 본인이기 때문에 authorize
@app.route("/article/<article_id>", methods=["PATCH"])
@authorize
def patch_article_detail(user, article_id):

    data = json.loads(request.data)
    title = data.get("title")
    content = data.get("content")

    article = db.article.update_one({"_id": ObjectId(article_id), "user": user["id"]}, {
        "$set": {"title": title, "content": content}})

    if article.matched_count:
        return jsonify({"message": "success"})
    else:
        return jsonify({"message": "fail"}), 403
    # article_id는 오브젝트고 user_id는 스트링
    # $set을 통해 바꿔줄 내용 정하기
    # matched_count 1이면 성공 0이면 실패
    

 # # # # # # # # # # #   게시글 삭제 DELETE   # # # # # # # # # # # # # # # # # # # # # # # # # # # #  
@app.route("/article/<article_id>", methods=["DELETE"])
@authorize
def delete_article_detail(user, article_id):

    article = db.article.delete_one(
        {"_id": ObjectId(article_id), "user": user["id"]})

    if article.deleted_count:
        return jsonify({"message": "success"})
    else:
        return jsonify({"message": "fail"}), 403
 
if __name__ == '__main__':
    app.run('127.0.0.1', port=5002, debug=True)
    # if __name__ == '__main__': app.run( host="192.168.56.20", port=5000)