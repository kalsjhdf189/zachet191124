from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    location = Column(String)
    
    movements = relationship("Movement", back_populates="product")

class Movement(Base):
    __tablename__ = "movements"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    from_location = Column(String)
    to_location = Column(String)
    quantity = Column(Integer)
    
    product = relationship("Product", back_populates="movements")

class Connect:
    @staticmethod
    def create_connection():
        engine = create_engine("postgresql://postgres:1234@localhost:5432/viktor")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session