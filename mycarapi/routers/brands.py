from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy import exists, select

from mycarapi.core.database import get_session
from mycarapi.models.cars import Brand
from mycarapi.schemas.brands import BrandListSchema, BrandRequestSchema, BrandResponseSchema

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post('/create-brand', status_code=status.HTTP_201_CREATED, response_model=BrandResponseSchema, summary="Create Brands")
async def create_brand(brand_request: BrandRequestSchema, db: AsyncSession = Depends(get_session)):
    ## Validar a existência da marca
    exist_brand = await db.scalar(select(exists().where(Brand.name == brand_request.name)))
    if exist_brand:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Marca de mesmo nome existente")
    
    new_brand = Brand(
        name = brand_request.name,
        description = brand_request.description,
        is_active = brand_request.is_active
    )

    db.add(new_brand)
    await db.commit()
    await db.refresh(new_brand)

    return new_brand

@router.get('/list', status_code=status.HTTP_200_OK, response_model=BrandListSchema, summary="List all brands")
async def list_brands(
        db: AsyncSession = Depends(get_session), 
        offset: int = Query(0, ge=0, description="Número de registros para pular"), 
        limit: int = Query(100, ge=1, le=100, description="Máximo de registros para aparecer"),
        filter: Optional[str] = Query(None, description="Filtro de busca")
    ):
    ## Criar uma query no bd
    query = select(Brand)

    ## checagem da busca
    if filter:
        search = f'%{filter}'
        query = query.where(Brand.name.ilike(search))
    
    ## tratar a query
    query = query.offset(offset).limit(limit)

    ## Executar a query
    result = await db.execute(query)
    # Modelar no formato de saida adequado
    brands = result.scalars().all()

    return {'brands': brands, 'offset': offset, 'limit': limit}
