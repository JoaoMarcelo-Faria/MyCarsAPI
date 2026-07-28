from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy import exists, func, select

from mycarapi.core.database import get_session
from mycarapi.models.cars import Brand, Car
from mycarapi.schemas.brands import BrandListSchema, BrandRequestSchema, BrandResponseSchema, BrandUpdateSchema

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
        filter: Optional[str] = Query(None, description="Filtro de busca"),
        active_param: Optional[bool] = Query(None, description="Filtro de marca ativa"),
    ):
    ## Criar uma query no bd
    query = select(Brand)

    ## checagem da busca
    if filter:
        search = f'%{filter}%'
        query = query.where(Brand.name.ilike(search))
    
    if active_param is not None:
        query = query.where(Brand.is_active == active_param)
    
    ## tratar a query
    query = query.offset(offset).limit(limit)

    ## Executar a query
    result = await db.execute(query)
    # Modelar no formato de saida adequado
    brands = result.scalars().all()
    print(brands)
    return {'brands': brands, 'offset': offset, 'limit': limit}

@router.get("/list/{id}", status_code=status.HTTP_200_OK, response_model=BrandResponseSchema, summary="Get a branch by ID")
async def list_brand_by_id(id: int, db: AsyncSession = Depends(get_session)):
    ## Verificação 
    exist_brand = await db.get(Brand, id)
    if not exist_brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca não encontrada")
    
    return exist_brand


@router.delete("/delete-brand/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a branch by ID")
async def delete_branch(id: int, db: AsyncSession = Depends(get_session)):
    ## Verificação de existência
    exist_brand = await db.get(Brand, id)
    if not exist_brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca não encontrada")
    
    cars_count = await db.scalar(
        select(func.count()).select_from(Car).where(Car.brand_id == id)
    )
    if cars_count > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Essa marca possui carros associados")
    
    await db.delete(exist_brand)
    await db.commit()

    return


@router.put("/update-brand/{id}", status_code=status.HTTP_200_OK, response_model=BrandUpdateSchema, summary="Update a branch by ID")
async def update_branch(id: int,  new_brand: BrandRequestSchema, db: AsyncSession = Depends(get_session)):
    exist_brand = await db.get(Brand, id)
    if not exist_brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca não encontrada")

    updated_data = new_brand.model_dump(exclude_unset=True)

    if 'name' in updated_data and updated_data['name'] != exist_brand.name:
        exist_name = await db.scalar(select(exists().where(Brand.name == updated_data["name"])))
        if exist_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nome já está em uso")

    for field, value in updated_data.items():
        setattr(exist_brand, field, value)

    await db.commit()
    await db.refresh(exist_brand)

    return exist_brand