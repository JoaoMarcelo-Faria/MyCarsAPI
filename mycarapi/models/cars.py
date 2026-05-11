from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, Text, String, Numeric, ForeignKey, Integer

from mycarapi.models.base import Base
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from decimal import Decimal
from enum import Enum

# evita o erro de circular import
if TYPE_CHECKING:
    from mycarapi.models.users import User

# normalização de dados para model de cars
# enum de transmissão
class TransmissionType(str, Enum):
    MANUAL = 'manual'
    AUTOMATIC = 'automatic'
    SEMI_AUTOMATIC = 'semi_automatic'
    CVT = 'cvt'

# enum de combustível
class FuelType(str, Enum):
    GAS = 'gasoline'
    ETHANOL = 'ethanol'
    FLEX = 'flex'
    DIESEL = 'diesel'
    ELECTRIC = 'electric'
    HYBRID = 'hybrid'

# Brands não é uma entidade no sistema mas seu model está ligada intimamente a cars
# Nome do model no singular(boas praticas) e Pascal case
class Brand(Base):
    __tablename__ = 'brands'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        server_onupdate=func.now()
    )

    # relação a nivel de codigo entre marcas e carros
    # relação ManyToOne -> muitos carros podem pertencer a uma marca
    cars: Mapped[List['Car']] = relationship(
        'Car',
        back_populates='brand'
    )

class Car(Base):
    __tablename__ = 'cars'

    id: Mapped[int] = mapped_column(primary_key=True)

    model: Mapped[str] = mapped_column(String(50), nullable=False)
    factory_year: Mapped[int] = mapped_column(Integer, nullable=False)
    model_year: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str] = mapped_column(String(30), nullable=False)
    plate: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    is_available: Mapped[bool] = mapped_column(default=True)
    
    #campos com enum
    fuel_type: Mapped[FuelType] = mapped_column(String(20), nullable=False)
    transmission: Mapped[TransmissionType] = mapped_column(String(20), nullable=False)

    #campos que declaram relações com outros models
    owner_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
    )
    brand_id: Mapped[int] = mapped_column(
        ForeignKey('brands.id')
    )

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        server_onupdate=func.now()
    )

    # propriedade e não campo do banco
    # permite o acesso de carros que pertencem a uma certa brand
    # relacionamento ManyToOne
    brand: Mapped['Brand'] = relationship(
        'Brand',
        back_populates='cars'
    )

    # permite o acesso de carros que pertencem a um certo dono
    owner: Mapped['User'] = relationship(
        'User',
        back_populates='cars'
    )