from flask import Blueprint

index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def home():
    return "Welcome to TranScore Backend!"