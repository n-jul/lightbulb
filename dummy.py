from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from extended_user.models import Practice  # Ensure this import matches your project structure
from database import Base

# Database connection URL (Update as per your configuration)
DATABASE_URL = "postgresql://postgres:Anjul123@localhost:5432/lightbulb"

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Dummy data for the practice table with 10 realistic names
dummy_practices = [
    {"name": "Advanced Orthopedic Care"},
    {"name": "Greenwood Family Dentistry"},
    {"name": "Mountain View Chiropractic"},
    {"name": "Silver Oak Healthcare"},
    {"name": "Pine Valley Wellness Center"},
    {"name": "Riverbend Pediatrics"},
    {"name": "Westside Rehabilitation Clinic"},
    {"name": "Summit Health Institute"},
    {"name": "Bright Futures Medical Group"},
    {"name": "Downtown Surgical Center"}
]

try:
    # Insert dummy data
    for data in dummy_practices:
        practice = Practice(name=data["name"])
        session.add(practice)

    # Commit changes
    session.commit()
    print("Dummy data inserted successfully!")

except Exception as e:
    session.rollback()
    print(f"Error inserting dummy data: {e}")

finally:
    session.close()
