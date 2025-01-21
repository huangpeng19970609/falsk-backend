from flask import Blueprint, request, jsonify
from models.article import Article
from models.folder import Folder
from extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

article_api = Blueprint('article', __name__)

# 创建文章
@article_api.route('/create', methods=['POST'])
@jwt_required()
def create_article():
    data = request.json
    parent_id = data.get('parent_id')  # 可以为 None
    user_id = get_jwt_identity()
    title = data.get('title', '未命名文档')
    
    try:
        if parent_id:
            # 如果指定了父文件夹，验证其存在性
            parent_folder = Folder.query.get(parent_id)
            if not parent_folder:
                return jsonify({
                    'code': 404,
                    'message': '指定的父文件夹不存在',
                    'data': None
                }), 200
        else:
            # 如果没有指定父文件夹，使用根文件夹
            parent_folder = Folder.query.filter_by(is_root=True).first()
            if not parent_folder:
                # 如果根文件夹不存在，创建一个
                parent_folder = Folder(name="默认文件夹", is_root=True)
                db.session.add(parent_folder)
                db.session.commit()
            parent_id = parent_folder.id
        
        new_article = Article(
            title=title,
            content='',
            parent_id=parent_id,
            user_id=user_id
        )
        db.session.add(new_article)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '文章创建成功',
            'data': {
                'id': new_article.id,
                'title': new_article.title,
                'parent_id': new_article.parent_id,
                'created_at': new_article.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建文章失败: {str(e)}',
            'data': None
        }), 200

# 获取文章列表
@article_api.route('/list', methods=["GET"])
def get_articles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    articles = Article.query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'data': [{
            'id': article.id,
            'title': article.title,
            'content': article.content,
            'user_id': article.user_id,
            'created_at': article.created_at.isoformat()
        } for article in articles.items],
        'total': articles.total,
        'pages': articles.pages,
        'current_page': articles.page,
        'code': 200
    })

# 获取单个文章
@article_api.route('/<int:article_id>', methods=["GET"])
def get_article(article_id):
    article = Article.query.get_or_404(article_id)
    
    return jsonify({
        'data': {
            'id': article.id,
            'title': article.title,
            'content': article.content,
            'user_id': article.user_id,
            'created_at': article.created_at.isoformat(),
        },
        'code': 200
    })

# 更新文章
@article_api.route('/<int:article_id>', methods=["PUT"])
@jwt_required()
def update_article(article_id):
    current_user_id = get_jwt_identity()
    article = Article.query.get_or_404(article_id)

    print('current_user_id type:', type(current_user_id))
    print('article.user_id type:', type(article.user_id))
    
    # 将两个值转换为相同类型进行比较
    if str(article.user_id) != str(current_user_id):
        return jsonify({'message': '没有权限修改此文章'}), 403
    
    data = request.get_json()
    article.title = data.get('title', article.title)
    article.content = data.get('content', article.content)
    
    db.session.commit()
    
    return jsonify({'message': '文章更新成功', 'code': 200})

# 删除文章
@article_api.route('/<int:article_id>', methods=["DELETE"])
@jwt_required()
def delete_article(article_id):
    current_user_id = get_jwt_identity()
    article = Article.query.get_or_404(article_id)
    
    # 检查是否是文章作者

    if str(article.user_id) != str(current_user_id):
        return jsonify({'message': '没有权限删除此文章'}), 403
    
    db.session.delete(article)
    db.session.commit()
    
    return jsonify({'message': '文章删除成功', 'code': 200})