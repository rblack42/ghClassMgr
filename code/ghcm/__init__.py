from flask import Flask
from config import DevConfig

def create_app(name):
    app = Flask(__name__)
    app.config.from_object(name)

    @app.route('/')
    def index():
        return "hello"

    return app


