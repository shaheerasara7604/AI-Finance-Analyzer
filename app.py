from flask import Flask
from flask_login import LoginManager
from config import Config
from utils.db_models import db, User

# 🔹 Blueprint imports
from routes.auth import auth
from routes.dashboard import dashboard
from routes.expenses import expenses

app = Flask(__name__)
app.config.from_object(Config)

# 🔹 Initialize database
db.init_app(app)

# 🔹 Login manager setup
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 🔹 Register blueprints
app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(expenses)

# 🔹 Home route
@app.route("/")
def home():
    return "AI Finance Analyzer is running"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)