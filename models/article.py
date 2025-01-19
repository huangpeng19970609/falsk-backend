from datetime import datetime
from extensions import db

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键关联到用户
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('articles', lazy=True))

    # 修改 parent_id 为可空
    parent_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)
    parent = db.relationship('Folder', back_populates='articles')
