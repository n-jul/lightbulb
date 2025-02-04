from sqlalchemy import Column, BigInteger, String, DateTime, func, ForeignKey, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData
from extended_user.models import extended_user
from database import Base
engine = create_engine('postgresql://postgres:Anjul123@localhost:5432/lightbulb')
metadata = MetaData()
# Base = declarative_base(metadata=metadata)
auth_user = Table('auth_user',metadata,autoload_with=engine)
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
    admin_id = Column(BigInteger, ForeignKey('extended_user.id'), nullable=True, default=None)


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
    user_id = Column(BigInteger,ForeignKey('auth_user.id'), nullable=False)
    is_selected = Column(Boolean, default=True, server_default='true')
# Example of creating the table
# Base.metadata.create_all(engine)

class AdminUserCampaign(Base):
    __tablename__="admin_user_campaign"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    text = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(BigInteger, nullable=False)