from flask import jsonify
from flask_jwt_extended.exceptions import JWTExtendedException, NoAuthorizationError
from jwt.exceptions import PyJWTError, ExpiredSignatureError, InvalidTokenError, InvalidSignatureError

def register_error_handlers(app):
    @app.errorhandler(JWTExtendedException)
    @app.errorhandler(PyJWTError)
    @app.errorhandler(NoAuthorizationError)
    @app.errorhandler(InvalidSignatureError)
    def handle_jwt_error(error):
        error_message = 'Token验证失败'
        status_code = 401
        
        if isinstance(error, ExpiredSignatureError):
            error_message = 'Token已过期'
        elif isinstance(error, InvalidTokenError):
            error_message = '无效的Token'
        elif isinstance(error, NoAuthorizationError):
            error_message = '未提供Token'

            
        return jsonify({
            'message': error_message,
            'error': str(error),
            'code': 401
        }), status_code