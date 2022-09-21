from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for,Blueprint
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import certifi




# db 연결
ca = certifi.where()
client = MongoClient('mongodb://15.164.214.98', 27017, username="test", password="test")
db = client.yoryjory

bp_list = Blueprint("lists", __name__, url_prefix="/list", template_folder='templates')


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'


@bp_list.route('/')
def listpage():
    return render_template('index.html')


# 이 부분을 어떻게 할지 못 정함 / def home 이 init.py에 있기 때문에
# @app.route('/')
# def home():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.users.find_one({"username": payload["id"]})
#         return render_template('index.html', user_info=user_info)
#     except jwt.ExpiredSignatureError:
#         return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
#     except jwt.exceptions.DecodeError:
#         return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
#



# post 쪽에서 이걸 받아와야함 승훈님이 보내주신 것에는 id/username/date/프로필사진이 없으니까 이걸 받아와야할 함수?가 필요
# user_info = db.users.find_one({"username": payload["id"]})
# comment_receive = request.form["comment_give"]
# date_receive = request.form["date_give"]
# doc = {
#     "username": user_info["username"],
#     "profile_name": user_info["profile_name"],
#     "profile_pic_real": user_info["profile_pic_real"],
#     "comment": comment_receive,
#     "date": date_receive
# }
# db.posts.insert_one(doc)




@bp_list.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posts = list(db.posts.find({}).sort("date", -1).limit(20))
        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['id']}))
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.","posts":posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



@bp_list.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 좋아요 수 변경

        user_info = db.users.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
        return jsonify({"result": "success", 'msg': 'updated'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



