from flask import Flask
from app.config import Config

def create_app(config=None):
    app = Flask(__name__, template_folder="templates")
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(Config)

    import os
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)
    os.makedirs(app.config.get("OUTPUT_FOLDER", "output_imgs"), exist_ok=True)

    from app.routes import bp
    app.register_blueprint(bp)

    return app
