from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Enum, Boolean, Date, JSON, Double
from app.api.excel.classes.dbBases import Base

UF_LIST = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT',
    'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO',
    'RR', 'SC', 'SP', 'SE', 'TO'
]

class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    idade: Mapped[int] = mapped_column(Integer, nullable=False)
    uf: Mapped[str] = mapped_column(Enum(*UF_LIST, name="uf_enum"), nullable=False)
    observacao: Mapped[str | None] = mapped_column(String(200))
    salario: Mapped[float | None] = mapped_column(Double)
    data_nascimento: Mapped[str | None] = mapped_column(Date)
    eh_funcionario: Mapped[bool] = mapped_column(Boolean, default=False)
    interesses: Mapped[dict | None] = mapped_column(JSON)

    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}')>"