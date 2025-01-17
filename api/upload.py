from flask import Blueprint, request, current_app
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import hashlib
import time

upload_api = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def get_upload_path():
    """根据环境返回不同的上传路径"""
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        return '/var/www/blog/uploads'
    else:
        # 本地开发环境
        return os.path.join(current_app.root_path  , 'static', 'uploads')

def get_url_prefix():
    """根据环境返回不同的URL前缀"""
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        return '/uploads'
    else:
        return 'http://127.0.0.1:8000/static/uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """生成唯一的文件名，避免文件名冲突"""
    # 检查文件名是否包含扩展名
    parts = original_filename.rsplit('.', 1)
    if len(parts) > 1:
        file_extension = parts[1].lower()
    else:
        # 如果没有扩展名，默认为jpg
        file_extension = 'jpg'
    
    timestamp = str(time.time())
    unique_string = f"{timestamp}-{original_filename}"
    hash_name = hashlib.md5(unique_string.encode()).hexdigest()
    return f"{hash_name}.{file_extension}"

@upload_api.route('/image', methods=['POST'])
def upload_image():
    
    print(request.files)

    if 'file' not in request.files:
        return {'code': 400, 'message': '没有文件'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'code': 400, 'message': '没有选择文件'}, 400
    
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        filename = generate_unique_filename(secure_filename(file.filename))
        # 按年月日组织文件
        date_path = datetime.now().strftime('%Y%m')
        # 获取当前环境的上传路径
        base_upload_path = get_upload_path()
        upload_path = os.path.join(base_upload_path, date_path)
        
        # 确保文件夹存在
        os.makedirs(upload_path, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        
        # 获取当前环境的URL前缀
        url_prefix = get_url_prefix()
        return {
            'code': 200,
            'data': {
                'url': f'{url_prefix}/{date_path}/{filename}',
                'filename': filename
            },
            'message': '上传成功'
        }
    
    return {'code': 400, 'message': '不支持的文件类型'}, 400 