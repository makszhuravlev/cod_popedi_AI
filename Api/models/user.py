from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    login = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    requests = relationship("Request", back_populates="user")

class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String(1000), nullable=False)
    status = Column(String(50), default="pending")
    
    user = relationship("User", back_populates="requests")
    files = relationship("GeneratedFile", back_populates="request")

    __table_args__ = (
        Index('ix_user_text', 'user_id', 'text', unique=True),
    )

class GeneratedFile(Base):
    __tablename__ = "generated_files"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"))
    file_url = Column(String(1000), nullable=False)
    file_type = Column(Enum('image', 'music', 'text', 'gift', name="file_type_enum"), nullable=False)
    
    request = relationship("Request", back_populates="files")