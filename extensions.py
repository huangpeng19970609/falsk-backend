from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# 创建一个未关联任何Flask应用的SQLAlchemy实例
db = SQLAlchemy()
jwt = JWTManager()