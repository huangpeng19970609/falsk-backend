from flask import Flask
from db.config import DB_CONFIG  # 假设您在config.py中定义了数据库配置
from api.article import article_api
from api.user import user_api
from api.upload import upload_api

from extensions import db, jwt  # 导入已创建的db实例
from flask_cors import CORS
from flask_migrate import Migrate

import secrets
from flask_jwt_extended import JWTManager

from error_handlers import register_error_handlers

def create_app():
    app = Flask(__name__)
    
    # 1. 首先设置基本配置
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['JWT_SECRET_KEY'] = secrets.token_hex(16)
    
    # 2. 注册错误处理器（要在 JWT 初始化之前）
    register_error_handlers(app)
    
    # 3. 初始化 JWT
    jwt.init_app(app)
    
    # 4. 设置 CORS
    CORS(app, resources={r"/api/*": {
        "origins": "http://localhost:3000",
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"]
    }})

    # 5. 数据库配置和初始化
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{DB_CONFIG['USERNAME']}:{DB_CONFIG['PASSWORD']}@"
        f"{DB_CONFIG['HOSTNAME']}:{DB_CONFIG['PORT']}/{DB_CONFIG['DATABASE']}?charset=utf8"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate = Migrate(app, db)

    # 6. 创建数据库表
    with app.app_context():
        db.create_all()

    # 7. 最后才注册蓝图
    app.register_blueprint(article_api, url_prefix="/article")  # 注意这里添加了 /api 前缀
    app.register_blueprint(user_api, url_prefix="/user")
    app.register_blueprint(upload_api, url_prefix="/upload")

    # 定义根路由
    @app.route('/')
    def hello():
        return 'Hello World'
    
    return app


# 使用工厂函数创建应用实例并运行
if __name__ == '__main__':
    app = create_app()
    app.run('127.0.0.1', 8000, debug=True)