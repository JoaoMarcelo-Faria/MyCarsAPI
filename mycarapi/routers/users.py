from mycarapi.core.database import get_session ##usa para injeção de dependência
from mycarapi.core.security import get_password_hash
from mycarapi.schemas.users import ListUserSchema, UpdateUserSchema, UserRequestSchema, UserResponseSchema
from mycarapi.db import USERS as usersDB
from mycarapi.models.users import User

from pydantic import EmailStr
from fastapi import APIRouter, HTTPException           ##classe do fastAPI que auxilia na configuração de rotas
from fastapi import status, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists







router = APIRouter()            ##cria uma rota do fastAPI

@router.get('/list', status_code=status.HTTP_200_OK, response_model=ListUserSchema)
async def list_users():
    return { 'users': usersDB }



@router.get('/list/{id}', status_code=status.HTTP_200_OK, response_model=UserResponseSchema)
async def list_users_by_id(id: int):
    ##verificação da existência do usuário de id requisitado
    if(id>len(usersDB) or id<1):
        raise HTTPException(status_code=404, detail='Usuário não encontrado')
    
    ##retorna o usuário
    return usersDB[id-1]



@router.post('/create-user', status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema, summary="Create new user")
async def create_user(
    user: UserRequestSchema, 
    db: AsyncSession = Depends(get_session)         # faz a injeção da dependência de "get_session", ou seja, faz essa corrotina executar antes de create_user
):
    # receber e validar os dados
    ## validação do nome de usuário
    username_exists = await db.scalar(            #faz uma consulta no bd
        select(exists().where(User.username == user.username))          # consultando na tabela User, coluna username, se existe o nome user.username
    )       
    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Username já está em uso'
        )
    
    ## validação do email
    email_exists = await db.scalar(
        select(exists().where(User.email == user.email))
    )
    if email_exists: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email já está em uso'
        )
    
    ## criptografar a senha
    encripted_password = get_password_hash(user.password)

    new_user = User(
        username = user.username,
        password = encripted_password,
        email = user.email
    )

    # adicionar no banco
    db.add(new_user)
    await db.commit()                       # salva o objeto no bd(IO -> await)
    await db.refresh(new_user)

    return new_user



@router.put('/update-user/{id}', status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema)
async def update_user(id: int, newUser: UpdateUserSchema):
    #atualizar o usuario
    usersDB[id-1] = UserResponseSchema(**newUser.model_dump(), id=id)

    return usersDB[id-1]

@router.delete('/delete-user/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int):
    del usersDB[id-1]
    return None