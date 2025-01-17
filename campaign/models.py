from sqlalchemy import Column, BigInteger, String, DateTime, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserCampaign(Base):
    __tablename__ = 'user_campaign'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    text = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(BigInteger, nullable=False)

class UserCampaignSequence(Base):
    __tablename__ = 'user_campaign_sequence'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_campaign_id = Column(BigInteger, ForeignKey('user_campaign.id'), nullable=False)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(BigInteger, nullable=False)

# Example of creating the table
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:Anjul123@localhost:5432/lightbulb')
Base.metadata.create_all(engine)
