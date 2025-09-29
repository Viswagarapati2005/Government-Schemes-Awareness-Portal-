from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['DB_CONFIG'] = {
        'host': 'localhost',
        'user': 'root',
        'password': 'VK181920',
        'database': 'schemes_db'
    }
    return app