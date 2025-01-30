from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import UserCampaign, UserCampaignSequence  # Import your models

# Setup database connection
DATABASE_URL = "postgresql://postgres:Anjul123@localhost:5432/lightbulb"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Step 1: Hardcoded Dummy Data for UserCampaign (Assuming the campaigns with IDs 9, 8, 1, 2, 10 already exist)
# Example UserCampaign data for reference
user_campaign_ids = [9, 8, 1, 2, 10]  # These are your provided campaign IDs

# Step 2: Hardcoded Dummy Data for UserCampaignSequence with these user_campaign_ids
dummy_sequences = [
    UserCampaignSequence(
        user_campaign_id=user_campaign_ids[0],  # Using campaign ID 9
        scheduled_date=datetime(2025, 2, 1, 10, 0, 0),  # Scheduled for Feb 1, 2025 at 10:00 AM
        status="pending",
        created_by=1,  # User ID 1
    ),
    UserCampaignSequence(
        user_campaign_id=user_campaign_ids[1],  # Using campaign ID 8
        scheduled_date=datetime(2025, 2, 2, 14, 30, 0),  # Scheduled for Feb 2, 2025 at 2:30 PM
        status="sent",
        created_by=2,  # User ID 2
    ),
    UserCampaignSequence(
        user_campaign_id=user_campaign_ids[2],  # Using campaign ID 1
        scheduled_date=datetime(2025, 2, 3, 9, 0, 0),  # Scheduled for Feb 3, 2025 at 9:00 AM
        status="pending",
        created_by=3,  # User ID 3
    ),
    UserCampaignSequence(
        user_campaign_id=user_campaign_ids[3],  # Using campaign ID 2
        scheduled_date=datetime(2025, 2, 4, 16, 0, 0),  # Scheduled for Feb 4, 2025 at 4:00 PM
        status="pending",
        created_by=4,  # User ID 4
    ),
    UserCampaignSequence(
        user_campaign_id=user_campaign_ids[4],  # Using campaign ID 10
        scheduled_date=datetime(2025, 2, 5, 13, 30, 0),  # Scheduled for Feb 5, 2025 at 1:30 PM
        status="pending",
        created_by=5,  # User ID 5
    ),
]

# Step 3: Add the dummy sequences to the database
session.add_all(dummy_sequences)
session.commit()  # Commit to insert the records

print("Dummy data for UserCampaignSequence has been inserted successfully!")
