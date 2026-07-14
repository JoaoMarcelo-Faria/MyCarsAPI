## -------- Modelagem antiga do SQLAlchemy --------------
# Essa abordagem funciona mas não utiliza das vantagens do TypeHints e não é a mais moderna
# from sqlalchemy import Column, Integer, String, DateTime, func

# from mycarapi.models.base import Base


# class User(Base):
#     __tablename__ = 'users'

#     id=Column(Integer, primary_key=True)
#     username = Column(String, unique=True, nullable=False)
#     password = Column(String, nullable=False)
#     email = Column(String, nullable=False, unique=False)
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
#     created_at = Column(DateTime, server_default=func.now())

## ----------- Modelagem nova do SQLAlchemy -------------

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func
from mycarapi.models.base import Base
from datetime import datetime

# evita o erro de circular import
if TYPE_CHECKING:
    from mycarapi.models.cars import Car

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=func.now()      #quando for atualizado, deve-se pegar a data e hora atual
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()           #quando um registro for criado, deve-se pegar a data e hora atual
    )

    cars: Mapped[List['Car']] = relationship (
        'Car',
        back_populates = 'owner'
    )