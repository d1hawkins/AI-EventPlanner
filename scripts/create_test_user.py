"""Create a test user for login verification"""
import sys
sys.path.append('.')

from passlib.context import CryptContext
from app.db.session import SessionLocal
from app.db.models import User
from app.db.models_saas import Organization, OrganizationUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("Test user already exists")
            print(f"Email: test@example.com")
            print(f"Password: TestPassword123!")
            return
        
        # Create an organization first
        org = Organization(
            name="Test Organization",
            slug="test-org",
            plan_id="free"
        )
        db.add(org)
        db.flush()
        
        # Create test user
        hashed_password = pwd_context.hash("TestPassword123!")
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(user)
        db.flush()
        
        # Link user to organization
        org_user = OrganizationUser(
            organization_id=org.id,
            user_id=user.id,
            role="admin",
            is_primary=True
        )
        db.add(org_user)
        db.commit()
        
        print("✅ Test user created successfully!")
        print(f"Email: test@example.com")
        print(f"Username: testuser")
        print(f"Password: TestPassword123!")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating test user: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
