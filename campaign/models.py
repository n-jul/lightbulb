from sqlalchemy import Column, BigInteger, String, DateTime, func, ForeignKey, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
Base = declarative_base()

engine = create_engine('postgresql://postgres:Anjul123@localhost:5432/lightbulb')
Base.metadata.create_all(engine)

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

class UserMessage(Base):
    __tablename__="user_message"
    id = Column(BigInteger,primary_key=True,autoincrement=True)
    campaign_id = Column(BigInteger, ForeignKey('user_campaign.id'),nullable=False)
    user_id = Column(BigInteger,ForeignKey('public.auth_user.id'), nullable=False)
    is_select = Column(Boolean, default=True, server_default='true')
# Example of creating the table
