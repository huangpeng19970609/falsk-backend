from extensions import db
from datetime import datetime
from enum import Enum

class NodeType(Enum):
    FOLDER = 'folder'
    FILE = 'file'

class Folder(db.Model):
    __tablename__ = 'folders'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_root = db.Column(db.Boolean, default=False, nullable=False)
    
    # 父子关系
    parent_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)
    children = db.relationship('Folder', backref=db.backref('parent', remote_side=[id]))
    
    # 节点类型
    node_type = db.Column(db.Enum(NodeType), default=NodeType.FOLDER, nullable=False)
    
    def __init__(self, name, parent=None, is_root=False):
        self.name = name
        self.parent = parent
        self.is_root = is_root
    
    def update_name(self, new_name):
        self.name = new_name
        self.updated_at = datetime.utcnow()
    
    def add_child(self, child):
        """添加子文件夹，并检查是否会形成循环"""
        if self._would_create_cycle(child):
            return False
        child.parent = self
        return True
    
    def _would_create_cycle(self, child):
        """检查添加子文件夹是否会形成循环"""
        current = self
        while current is not None:
            if current.id == child.id:
                return True
            current = current.parent
        return False
    
    def __repr__(self):
        return f'<Folder {self.name}>' 