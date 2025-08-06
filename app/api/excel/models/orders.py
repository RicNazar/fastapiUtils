from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, types
from app.api.excel.classes.dbBases import Base
from datetime import date

class Orders(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    product: Mapped[str] = mapped_column(types.String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    order_date: Mapped[date] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(types.String(50), nullable=False)

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, product='{self.product}')>"