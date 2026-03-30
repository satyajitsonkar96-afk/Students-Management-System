from flask import Flask          # Import the main Flask class to create a WSGI application
from config import Config        # Import the configuration class from a local config module
from routes.main_routes import main_bp   # Import the main blueprint for routing common pages
from routes.admin_routes import admin_bp # Import the admin blueprint for admin-specific routes
from datetime import timedelta   # Import timedelta to set session lifetime duration

app = Flask(__name__)            # Create the Flask application instance

# ✅ load config (should contain SECRET_KEY)
app.config.from_object(Config)   # Load configuration settings from the Config class (e.g., SECRET_KEY)

# ⏳ session timeout
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)  # Set session to expire after 5 minutes of inactivity

# register blueprints
app.register_blueprint(main_bp)  # Attach the main blueprint to the app for handling general routes
app.register_blueprint(admin_bp) # Attach the admin blueprint for handling admin routes

if __name__ == "__main__":       # Run the app only if this script is executed directly (not imported)
    app.run(debug=True)          # Start the development server with debug mode enabled (auto-reload, detailed errors)