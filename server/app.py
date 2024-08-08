from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_restful import Api, Resource
from dotenv import load_dotenv
import os
from models import db, User, WorkoutPlan, NutritionPlan, ProgressTracking

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

db.init_app(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
CORS(app, supports_credentials=True)
api = Api(app) 

class Register(Resource):
    def post(self):
        username = request.json.get("username")
        email = request.json.get("email")
        password = request.json.get("password")
        age = request.json.get("age")
        nationality = request.json.get("nationality")
        description = request.json.get("description")
        hobbies = request.json.get("hobbies")

        if not username or not email or not password or not age:
            return {"error": "Missing fields"}, 400

        if User.query.filter_by(email=email).first():
            return {"error": "Email already exists"}, 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password, age=age, nationality=nationality, description=description, hobbies=hobbies)
        db.session.add(new_user)
        db.session.commit()
        return new_user.to_dict(), 201
    
class Login(Resource):
    def post(self):
        email = request.json.get("email")
        password = request.json.get("password")

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            return {"message": "Logged in successfully"}, 200
        return {"error": "Invalid credentials"}, 401

class Logout(Resource):
    def post(self):
        session.pop('user_id', None)
        return {"message": "Logged out successfully"}, 200

class UserResource(Resource):
    def get(self, user_id=None):
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
            return {"error": "User not found"}, 404

        users = User.query.all()
        return {"users": [user.to_dict() for user in users]}, 200
    
class WorkoutPlanResource(Resource):
    def post(self):
        data = request.get_json()
        new_plan = WorkoutPlan(
            title=data['title'],
            description=data.get('description'),
            duration=data['duration'],
            start_date=data['start_date'],
            end_date=data['end_date']
        )
        db.session.add(new_plan)
        db.session.commit()
        return new_plan.to_dict(), 201

    def get(self, plan_id=None):
        if plan_id:
            plan = WorkoutPlan.query.get(plan_id)
            if plan:
                return plan.to_dict(), 200
            return {"error": "Plan not found"}, 404
        
        plans = WorkoutPlan.query.all()
        return [plan.to_dict() for plan in plans], 200

    def patch(self, plan_id):
        plan = WorkoutPlan.query.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}, 404
        
        data = request.get_json()
        if 'title' in data:
            plan.title = data['title']
        if 'description' in data:
            plan.description = data['description']
        if 'duration' in data:
            plan.duration = data['duration']
        if 'start_date' in data:
            plan.start_date = data['start_date']
        if 'end_date' in data:
            plan.end_date = data['end_date']

        db.session.commit()
        return {"message": "Plan updated"}, 200

    def delete(self, plan_id):
        plan = WorkoutPlan.query.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}, 404

        db.session.delete(plan)
        db.session.commit()
        return {"message": "Plan deleted"}, 200


if __name__ == '__main__':
    app.run(debug=True)
