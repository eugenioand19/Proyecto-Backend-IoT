
from flask import Flask
from db import db
from flask_marshmallow import Marshmallow
from routes.central_routes import register_blueprints
from flask import Flask
from db import db
from flask_marshmallow import Marshmallow
from routes.central_routes import register_blueprints


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:456123@localhost/bdIoT"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
ma = Marshmallow(app)

# Synchronize changes between models and tables
""" with app.app_context():
    db.create_all()
 """
register_blueprints(app)

if __name__ == "__main__":
    app.run(debug=True)