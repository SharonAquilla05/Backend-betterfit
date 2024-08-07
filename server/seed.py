
from datetime import date, timedelta

from werkzeug.security import generate_password_hash
from app import app, db
from models import User, WorkoutPlan, NutritionPlan, ProgressTracking

def seed():
    with app.app_context():
        try:
            user1 = User(
                username='john_doe',
                email='john@example.com',
                password=generate_password_hash('john123'),
                age=28,
                nationality='American',
                description='Fitness enthusiast',
                hobbies='Running, Hiking'
            )
            user2 = User(
                username='jane_smith',
                email='jane@example.com',
                password=generate_password_hash('jane123'),
                age=32,
                nationality='Canadian',
                description='Nutrition expert',
                hobbies='Cooking, Yoga'
            )

            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

            workout_plan1 = WorkoutPlan(
                title='Beginner Cardio',
                description='A beginner-friendly cardio workout plan.',
                duration=30,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30)
            )
            workout_plan2 = WorkoutPlan(
                title='Strength Training',
                description='An advanced strength training program.',
                duration=60,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=60)
            )

            user1.workout_plans.append(workout_plan1)
            user2.workout_plans.append(workout_plan2)

            # Add workout plans to the session
            db.session.add(workout_plan1)
            db.session.add(workout_plan2)
            db.session.commit()

            nutrition_plan1 = NutritionPlan(
                user=user1,
                title='Weight Loss Plan',
                description='Low-calorie diet to aid weight loss.',
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30)
            )
            nutrition_plan2 = NutritionPlan(
                user=user2,
                title='Muscle Gain Plan',
                description='High-protein diet for muscle building.',
                start_date=date.today(),
                end_date=date.today() + timedelta(days=45)
            )

            db.session.add(nutrition_plan1)
            db.session.add(nutrition_plan2)
            db.session.commit()

            # Create progress tracking entries
            progress_tracking1 = ProgressTracking(
                user=user1,
                weight=75.5,
                measurements='Chest: 90 cm, Waist: 80 cm',
                date=date.today()
            )
            progress_tracking2 = ProgressTracking(
                user=user2,
                weight=68.0,
                measurements='Chest: 85 cm, Waist: 70 cm',
                date=date.today()
            )

            db.session.add(progress_tracking1)
            db.session.add(progress_tracking2)
            db.session.commit()
            print("Database seeded successfully!")

        except Exception as e:
            db.session.rollback()
            print(f"An error occurred while seeding the database: {e}")

if __name__ == '__main__':
    seed()
