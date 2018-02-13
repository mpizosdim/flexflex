import os
from flask import Flask
from flask_restful import Api
from flask_jwt import JWT
from security import authenticate, identity
from utils import UserRegister, Recommendation

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data/database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "s5346576urtyhdgfdxsW34E5RGFSCD"
api = Api(app)

jwt = JWT(app, authenticate, identity) # /auth

api.add_resource(UserRegister, '/register')
api.add_resource(Recommendation, '/<string:username>/dailyrec')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)