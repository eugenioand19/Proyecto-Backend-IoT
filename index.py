from config import config
from app import init_app
from db import db
configuration = config['production']
app = init_app(configuration)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()