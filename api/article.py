from flask import Blueprint, request, jsonify
from models.article import Article
from extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

article_api = Blueprint('article', __name__)

# 创建文章
@article_api.route('', methods=["POST"])
@jwt_required()
def create_article():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    article = Article(
        title=data['title'],
        content=data['content'],
        user_id=current_user_id
    )
    
    db.session.add(article)
    db.session.commit()
    
    return jsonify({'message': '文章创建成功', 'id': article.id, 'code': 200} ), 201

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
    
    # 检查是否是文章作者
    if article.user_id != current_user_id:
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
    if article.user_id != current_user_id:
        return jsonify({'message': '没有权限删除此文章'}), 403
    
    db.session.delete(article)
    db.session.commit()
    
    return jsonify({'message': '文章删除成功', 'code': 200})