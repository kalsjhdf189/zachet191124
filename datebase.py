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
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    location = Column(String, nullable=False)

    # Добавляем связь с перемещениями (название back_populates должно быть таким же, как в модели Movement)
    movements = relationship("Movement", back_populates="product")


class Movement(Base):
    __tablename__ = "movements"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    from_location = Column(String, nullable=False)
    to_location = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)

    # Связь с товаром (название back_populates должно быть таким же, как в модели Product)
    product = relationship("Product", back_populates="movements")



class Connect:
    @staticmethod
    def create_connection():
        engine = create_engine("postgresql://postgres:1234@localhost:5432/viktor")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session
