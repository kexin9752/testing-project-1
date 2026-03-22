from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.department import Department
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing_depts = db.query(Department).count()
        if existing_depts == 0:
            depts = [
                Department(name="Engineering", description="Software Engineering Team"),
                Department(name="Sales", description="Sales and Marketing Team"),
                Department(name="HR", description="Human Resources Team"),
            ]
            db.add_all(depts)
            db.commit()
            print("Created departments")

        existing_users = db.query(User).count()
        if existing_users == 0:
            depts = db.query(Department).all()
            dept_map = {d.name: d.id for d in depts}

            users = [
                User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password=pwd_context.hash("admin123"),
                    full_name="System Administrator",
                    role="admin",
                    department_id=dept_map.get("HR"),
                    is_active=True
                ),
                User(
                    username="john.doe",
                    email="john@example.com",
                    hashed_password=pwd_context.hash("password123"),
                    full_name="John Doe",
                    role="user",
                    department_id=dept_map.get("Engineering"),
                    is_active=True
                ),
                User(
                    username="jane.smith",
                    email="jane@example.com",
                    hashed_password=pwd_context.hash("password123"),
                    full_name="Jane Smith",
                    role="user",
                    department_id=dept_map.get("Sales"),
                    is_active=True
                ),
            ]
            db.add_all(users)
            db.commit()
            print("Created sample users")

        print("Database initialized successfully!")

    finally:
        db.close()

if __name__ == "__main__":
    init_db()
