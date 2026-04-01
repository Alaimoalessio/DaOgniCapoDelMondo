"""
Create a default user for the private area
Run this script to create an admin user
"""
from app import app
from models import db, User

def create_user():
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username='admin').first()
        if existing_user:
            print("User 'admin' already exists!")
            return
        
        # Create new user
        user = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        user.set_password('admin123')  # Change this password!
        
        db.session.add(user)
        db.session.commit()
        
        print("✓ User created successfully!")
        print("  Username: admin")
        print("  Password: admin123")
        print("\n⚠️  IMPORTANT: Change the password after first login!")

if __name__ == '__main__':
    create_user()

