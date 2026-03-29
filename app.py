from flask import Flask
from config import Config
from routes.main_routes import main_bp
from routes.admin_routes import admin_bp
from datetime import timedelta

app = Flask(__name__)

# ✅ load config (should contain SECRET_KEY)
app.config.from_object(Config)

# ⏳ session timeout
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)
