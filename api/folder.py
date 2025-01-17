from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import List, Union, Optional
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.folder import Folder
from extensions import db

folder_api = Blueprint('folder', __name__)

@folder_api.route('/', methods=["GET"])
def hello():
    return 'folders'

@folder_api.route('/create', methods=["POST"])
@jwt_required()
def create_folder():
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
    folder = Folder.query.get(folder_id)
    
    if not folder:
        return jsonify({
            'code': 500,
            'data': None,
            'message': '文件夹不存在'
        }), 200

    return jsonify({
        'code': 200,
        'data': {
            'id': folder.id,
            'name': folder.name,
            'created_at': folder.created_at.isoformat(),
            'updated_at': folder.updated_at.isoformat(),
            'children': [{
                'id': child.id,
                'name': child.name,
                'type': child.node_type.value
            } for child in folder.children]
        },
        'message': '获取成功'
    }), 200

@folder_api.route('/<int:folder_id>', methods=["PUT"])
@jwt_required()
def update_folder(folder_id):
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
    """初始化根文件夹"""
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
    try:
        # 使用is_root字段查询根文件夹
        root_folder = Folder.query.filter_by(is_root=True).first()
        
        # 获取其他所有非根文件夹
        other_folders = Folder.query.filter_by(is_root=False).order_by(Folder.created_at.asc()).all()
        
        folders = [root_folder] + other_folders if root_folder else other_folders
        
        return jsonify({
            'code': 200,
            'data': [{
                'id': folder.id,
                'name': folder.name,
                'created_at': folder.created_at.isoformat(),
                'updated_at': folder.updated_at.isoformat(),
                'is_root': folder.is_root,  # 添加is_root字段到响应中
                'children': [{
                    'id': child.id,
                    'name': child.name,
                    'type': child.node_type.value
                } for child in folder.children]
            } for folder in folders if folder],
            'message': '获取成功'
        }), 200

    except Exception as e:
        return jsonify({
            'code': 500,
            'data': None,
            'message': f'获取文件夹列表失败: {str(e)}'
        }), 200
