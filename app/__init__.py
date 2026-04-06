from flask import Flask


def create_app():
    # Import generators first to trigger field registration
    # (must happen before blueprint import to avoid circular imports)
    import app.generators as _gen  # noqa: F401

    flask_app = Flask(__name__)
    flask_app.secret_key = 'gerador-dados-massa-2024-secret-key'

    from app.api.routes import api_bp
    flask_app.register_blueprint(api_bp)

    return flask_app
