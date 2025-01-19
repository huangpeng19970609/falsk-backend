from flask import Blueprint,request,jsonify
from models.user import User
from extensions import db
from werkzeug.security import generate_password_hash,check_password_hash 
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

user_api = Blueprint('user', __name__)

@user_api.route('/', methods=["GET"])
def hello():
    return 'users'

# 增
@user_api.route('/add', methods=["GET"])
@jwt_required()  # 保护此路由
def h():
    current_user_id = get_jwt_identity()  # 获取当前用户 ID
    print(current_user_id)
    # 假设你有一个方法可以根据用户 ID 查询用户信息
    current_user = User.query.get(current_user_id)
    
    print(current_user)

    if (not current_user):
        return jsonify({'message': '用户不存在'}), 401
    
    # 使用 generate_password_hash 生成密码哈希
    hashed_password = generate_password_hash('huangpengpeng1215656702', method='pbkdf2:sha256')
    new_user = User(username='admin', password=hashed_password,email='1215656702@qq.com')
    db.session.add(new_user)
    db.session.commit()
    return 'success'

# 更多查询方法可查看api (查询是复杂且灵活的)
@user_api.route('/get', methods=["GET"])
def get():
    # 主键
    currentUser = User.query.get(1)
    user1 = currentUser.username + '-' + currentUser.password

    # 类列表对象 =>  SELECT users.id AS users_id, users.username AS users_username, users.password AS users_password
    user2 = User.query.filter_by(username = "usern1ame23")
    for u in user2:
        print(u)
    print('user.py  ', user2)

    return user1

@user_api.route('/edit')
def edit():
    user = User.query.filter_by(username = "usern1ame23").first()
    user.username = 'huangpeng'
    print('user.py  ', user)
    db.session.commit()
    return '修改成功'

@user_api.route('/delete')
def delete():
    user = User.query.get(1)
    db.session.delete(user)
    db.session.commit()
    return '修改成功'


@user_api.route('/login', methods=["POST"])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(
            {
             'code': 401,
             'data': None,
             'message': '用户名和密码不能为空',
             }
        ), 200

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(
            {
             'code': 401,
             'data': None,
             'message': '用户不存在',
             }
        ), 200
        
    if not check_password_hash(user.password, password):
        return jsonify(
            {
             'code': 401,
             'data': None,
             'message': '密码错误',
             }
        ), 200

    return jsonify({
             'code': 200,
             'data': {
                 'token': create_access_token(identity=str(user.id)),
                 'user': {
                     'id': user.id,
                     'username': user.username,
                 }
             },
             'message': '登录成功',
             }
        ), 200


