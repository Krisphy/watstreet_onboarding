from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

# Initial Setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

# Parsing User Arguments
user_args = reqparse.RequestParser()
user_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
user_args.add_argument('email', type=str, required=True, help="Email cannot be blank")

# Data Structure for Database
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"User(name = {self.name}, email = {self.email})"

# Dict for Serialization
userFields = {
    'id':fields.Integer,
    'name':fields.String,
    'email':fields.String,
}

# /api/users/ Resource
class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all()
        return users
    
    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(name=args["name"], email=args["email"])
        db.session.add(user)
        db.session.commit()
        users = UserModel.query.all()
        return users, 201
    
    @marshal_with(userFields)
    def put(self):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(name = args["name"]).first()
        if not user:
            abort (404, "user name not found")
        user.email = args["email"]
        db.session.commit()
        users = UserModel.query.all()
        return users, 200
    
# /api/user/<id>/ Resource
class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, "user not found")
        return user
    
    @marshal_with(userFields)
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, "user id not found")
        user.name = args["name"]
        user.email = args["email"]
        db.session.commit()
        return user

    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, "user id not found")
        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users

# Adds Resources to API
api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/user/<int:id>')

# Entry
if __name__ == '__main__':
    app.run(debug=True)