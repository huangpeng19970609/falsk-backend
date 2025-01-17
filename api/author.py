from flask import Blueprint

api_author = Blueprint('api_author', __name__)

@api_author.route('/', methods=["GET"])
def hello():
    return '123'
