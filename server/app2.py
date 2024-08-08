from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
import os
from cryptography.fernet import Fernet

# Initialize the app and configure the database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)
CORS(app)


# Generate or load encryption key
encryption_key = os.getenv('ENCRYPTION_KEY')
if not encryption_key:
    encryption_key = Fernet.generate_key().decode()
    with open('.env', 'a') as f:
        f.write(f'\nENCRYPTION_KEY={encryption_key}\n')
cipher = Fernet(encryption_key.encode())

def encrypt(data):
    return cipher.encrypt(data.encode()).decode()

def decrypt(data):
    return cipher.decrypt(data.encode()).decode()

# Define your models here
class NutritionPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": decrypt(self.title),
            "description": decrypt(self.description) if self.description else None,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }

class ProgressTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    measurements = db.Column(db.String, nullable=True)
    date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "weight": self.weight,
            "measurements": decrypt(self.measurements) if self.measurements else None,
            "date": self.date,
        }

# Nutrition Plan Resources
class NutritionPlanResource(Resource):
    def post(self):
        data = request.get_json()
        new_plan = NutritionPlan(
            user_id=data['user_id'],
            title=encrypt(data['title']),
            description=encrypt(data['description']) if data.get('description') else None,
            start_date=data['start_date'],
            end_date=data['end_date']
        )
        db.session.add(new_plan)
        db.session.commit()
        return new_plan.to_dict(), 201

    def get(self, plan_id=None):
        if plan_id:
            plan = NutritionPlan.query.get(plan_id)
            if plan:
                return plan.to_dict(), 200
            return {"error": "Plan not found"}, 404
        
        plans = NutritionPlan.query.all()
        return [plan.to_dict() for plan in plans], 200

    def patch(self, plan_id):
        plan = NutritionPlan.query.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}, 404
        
        data = request.get_json()
        if 'title' in data:
            plan.title = encrypt(data['title'])
        if 'description' in data:
            plan.description = encrypt(data['description'])
        if 'start_date' in data:
            plan.start_date = data['start_date']
        if 'end_date' in data:
            plan.end_date = data['end_date']

        db.session.commit()
        return {"message": "Plan updated"}, 200

    def delete(self, plan_id):
        plan = NutritionPlan.query.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}, 404

        db.session.delete(plan)
        db.session.commit()
        return {"message": "Plan deleted"}, 200

# Progress Tracking Resources
class ProgressTrackingResource(Resource):
    def post(self):
        data = request.get_json()
        new_progress = ProgressTracking(
            user_id=data['user_id'],
            weight=data['weight'],
            measurements=encrypt(data['measurements']) if data.get('measurements') else None,
            date=data['date']
        )
        db.session.add(new_progress)
        db.session.commit()
        return new_progress.to_dict(), 201

    def get(self, progress_id=None):
        if progress_id:
            progress = ProgressTracking.query.get(progress_id)
            if progress:
                return progress.to_dict(), 200
            return {"error": "Progress not found"}, 404
        
        progresses = ProgressTracking.query.all()
        return [progress.to_dict() for progress in progresses], 200

    def patch(self, progress_id):
        progress = ProgressTracking.query.get(progress_id)
        if not progress:
            return {"error": "Progress not found"}, 404
        
        data = request.get_json()
        if 'weight' in data:
            progress.weight = data['weight']
        if 'measurements' in data:
            progress.measurements = encrypt(data['measurements'])
        if 'date' in data:
            progress.date = data['date']

        db.session.commit()
        return {"message": "Progress updated"}, 200

    def delete(self, progress_id):
        progress = ProgressTracking.query.get(progress_id)
        if not progress:
            return {"error": "Progress not found"}, 404

        db.session.delete(progress)
        db.session.commit()
        return {"message": "Progress deleted"}, 200

# Add routes
api.add_resource(NutritionPlanResource, '/nutrition_plans', '/nutrition_plans/<int:plan_id>')
api.add_resource(ProgressTrackingResource, '/progress_tracking', '/progress_tracking/<int:progress_id>')

# Basic endpoint to check if the server is running
@app.route('/')
def hello_world():
    return 'Hello, World!'

# Run the application
if __name__ == '__main__':
    app.run(port=5555, debug=True)
