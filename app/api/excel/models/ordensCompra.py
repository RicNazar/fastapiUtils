from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, types
from app.api.excel.classes.dbBases import Base
from datetime import date
from sqlalchemy.sql.schema import SchemaConst

SchemaConst.NULL_UNSPECIFIED


class OrdensCompra(Base):
    __tablename__ = 'OrdensCompra'
    PO:Mapped[str] = mapped_column(types.TEXT, primary_key=True,nullable=False,autoincrement=False) 
    Delivery_To: Mapped[str] = mapped_column(types.TEXT)
    Cliente: Mapped[str] = mapped_column(types.TEXT)
    Madeira: Mapped[str] = mapped_column(types.TEXT)
    INCO_Terms: Mapped[str] = mapped_column(types.TEXT)
    Cond_PGTO: Mapped[str] = mapped_column(types.TEXT,)
    Destino: Mapped[str] = mapped_column(types.TEXT)
    Dias_para_Entrega: Mapped[int] = mapped_column(types.Integer)
    Pais: Mapped[str] = mapped_column(types.TEXT)
    Payment_Terms: Mapped[str] = mapped_column(types.TEXT)
    Data_da_Ordem: Mapped[date] = mapped_column(types.Date)
    Pedido_BM: Mapped[int] = mapped_column(types.Integer)