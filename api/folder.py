from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import List, Union, Optional
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.folder import Folder
from models.article import Article
from extensions import db

folder_api = Blueprint('folder', __name__)

@folder_api.route('/', methods=["GET"])
def hello():
    """健康检查接口"""
    return 'folders'

@folder_api.route('/create', methods=["POST"])
@jwt_required()
def create_folder():
    """创建文件夹
    请求参数:
        name: 文件夹名称
        parent_id: 父文件夹ID
    """
    data = request.json
    folder_name = data.get('name')
    parent_id = data.get('parent_id')  # 可选参数，指定父文件夹

    if not parent_id:
         return jsonify({
            'code': 500,
            'data': None,
            'message': '父文件夹不能为空'
        }), 200

    if not folder_name:
        return jsonify({
            'code': 500,
            'data': None,
            'message': '文件夹名称不能为空'
        }), 200

    try:
        new_folder = Folder(name=folder_name)
        
        if parent_id:
            parent_folder = Folder.query.get(parent_id)
            if not parent_folder:
                return jsonify({
                    'code': 500,
                    'data': None,
                    'message': '父文件夹不存在'
                }), 200
            
            if not parent_folder.add_child(new_folder):
                return jsonify({
                    'code': 500,
                    'data': None,
                    'message': '不能创建循环引用的文件夹结构'
                }), 200

        db.session.add(new_folder)
        db.session.commit()

        return jsonify({
            'code': 200,
            'data': {
                'id': new_folder.id,
                'name': new_folder.name,
                'created_at': new_folder.created_at.isoformat()
            },
            'message': '文件夹创建成功'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'data': None,
            'message': f'创建文件夹失败: {str(e)}'
        }), 200

@folder_api.route('/<int:folder_id>', methods=["GET"])
@jwt_required()
def get_folder(folder_id):
    """获取指定文件夹详情及其直接子项（仅一层）"""
    try:
        folder = Folder.query.get(folder_id)
        if not folder:
            return jsonify({
                'code': 500,
                'data': None,
                'message': '文件夹不存在'
            }), 200

        # 修改联合查询，只包含现有字段
        union_query = db.union_all(
            db.select(
                Folder.id,
                Folder.name,
                db.literal('FOLDER').label('type'),
                Folder.created_at,
                db.literal(True).label('has_children'),
                db.literal(None).label('content'),
                db.literal(None).label('updated_at')
            ).where(Folder.parent_id == folder_id),
            db.select(
                Article.id,
                Article.title.label('name'),
                db.literal('FILE').label('type'),
                Article.created_at,
                db.literal(False).label('has_children'),
                Article.content,
                Article.updated_at
            ).where(Article.parent_id == folder_id)
        ).subquery()

        # 查询子查询，只包含现有字段
        direct_children = db.session.query(
            union_query.c.id,
            union_query.c.name,
            union_query.c.type,
            union_query.c.created_at,
            union_query.c.has_children,
            union_query.c.content,
            union_query.c.updated_at
        ).order_by(union_query.c.created_at).all()

        return jsonify({
            'code': 200,
            'data': {
                'id': folder.id,
                'name': folder.name,
                'created_at': folder.created_at.isoformat(),
                'updated_at': folder.updated_at.isoformat(),
                'children': [{
                    'id': item.id,
                    'name': item.name,
                    'type': item.type,
                    'has_children': item.has_children,
                    'created_at': item.created_at.isoformat() if item.created_at else None,
                    'updated_at': item.updated_at.isoformat() if item.updated_at else None,
                    'content': item.content if item.type == 'FILE' else None
                } for item in direct_children]
            },
            'message': '获取成功'
        }), 200

    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'message': f'获取失败: {str(e)}'
        }), 200

@folder_api.route('/<int:folder_id>', methods=["PUT"])
@jwt_required()
def update_folder(folder_id):
    """更新文件夹名称
    参数:
        folder_id: 文件夹ID
    请求参数:
        name: 新的文件夹名称
    """
    data = request.json
    new_name = data.get('name')

    if not new_name:
        return jsonify({
            'code': 400,
            'data': None,
            'message': '文件夹名称不能为空'
        }), 200

    folder = Folder.query.get(folder_id)
    if not folder:
        return jsonify({
            'code': 404,
            'data': None,
            'message': '文件夹不存在'
        }), 200

    try:
        folder.update_name(new_name)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': {
                'id': folder.id,
                'name': folder.name,
                'updated_at': folder.updated_at.isoformat()
            },
            'message': '更新成功'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'data': None,
            'message': f'更新失败: {str(e)}'
        }), 200

@folder_api.route('/<int:folder_id>', methods=["DELETE"])
@jwt_required()
def delete_folder(folder_id):
    """删除指定文件夹
    参数:
        folder_id: 要删除的文件夹ID
    """
    folder = Folder.query.get(folder_id)
    
    if not folder:
        return jsonify({
            'code': 404,
            'data': None,
            'message': '文件夹不存在'
        }), 200

    try:
        db.session.delete(folder)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': None,
            'message': '删除成功'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'data': None,
            'message': f'删除失败: {str(e)}'
        }), 200

@folder_api.route('/init', methods=["POST"])
def init_root_folder():
    """初始化根文件夹，如果根文件夹不存在则创建"""
    try:
        # 使用is_root字段来标识根文件夹，而不是依赖name
        root_folder = Folder.query.filter_by(is_root=True).first()
        
        if root_folder:
            return jsonify({
                'code': 200,
                'data': {
                    'id': root_folder.id,
                    'name': root_folder.name,
                    'created_at': root_folder.created_at.isoformat()
                },
                'message': '根文件夹已存在'
            }), 200
            
        # 创建新的根文件夹，设置is_root为True
        root_folder = Folder(name="默认文件夹", is_root=True)
        db.session.add(root_folder)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': {
                'id': root_folder.id,
                'name': root_folder.name,
                'created_at': root_folder.created_at.isoformat()
            },
            'message': '根文件夹创建成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'data': None,
            'message': f'初始化根文件夹失败: {str(e)}'
        }), 200

@folder_api.route('/list', methods=["GET"])
@jwt_required()
def get_folder_list():
    """获取顶层文件夹列表（仅包含根目录和一级文件夹）"""
    try:
        root_folder = Folder.query.filter_by(is_root=True).first()
        
        if root_folder:
            # 修改联合查询，只包含现有字段
            union_query = db.union_all(
                db.select(
                    Folder.id,
                    Folder.name,
                    db.literal('FOLDER').label('type'),
                    Folder.created_at,
                    db.literal(True).label('has_children'),
                    db.literal(None).label('content'),
                    db.literal(None).label('updated_at')
                ).where(Folder.parent_id == root_folder.id),
                db.select(
                    Article.id,
                    Article.title.label('name'),
                    db.literal('FILE').label('type'),
                    Article.created_at,
                    db.literal(False).label('has_children'),
                    Article.content,
                    Article.updated_at
                ).where(Article.parent_id == root_folder.id)
            ).subquery()

            # 查询子查询，只包含现有字段
            direct_children = db.session.query(
                union_query.c.id,
                union_query.c.name,
                union_query.c.type,
                union_query.c.created_at,
                union_query.c.has_children,
                union_query.c.content,
                union_query.c.updated_at
            ).order_by(union_query.c.created_at).all()

            root_data = {
                'id': root_folder.id,
                'name': root_folder.name,
                'created_at': root_folder.created_at.isoformat(),
                'updated_at': root_folder.updated_at.isoformat(),
                'is_root': True,
                'children': [{
                    'id': item.id,
                    'name': item.name,
                    'type': item.type,
                    'has_children': item.has_children,
                    'created_at': item.created_at.isoformat() if item.created_at else None,
                    'updated_at': item.updated_at.isoformat() if item.updated_at else None,
                    'content': item.content if item.type == 'FILE' else None
                } for item in direct_children]
            }
        else:
            root_data = None

        return jsonify({
            'code': 200,
            'data': root_data,
            'message': '获取成功'
        }), 200

    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'message': f'获取文件夹列表失败: {str(e)}'
        }), 200
