from typing import Optional

from mycarapi.core.database import get_session ##usa para injeção de dependência
from mycarapi.core.security import get_password_hash
from mycarapi.schemas.users import ListUserSchema, UpdateUserSchema, UserRequestSchema, UserResponseSchema
from mycarapi.models.users import User

from fastapi import APIRouter, HTTPException           ##classe do fastAPI que auxilia na configuração de rotas
from fastapi import status, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, update







router = APIRouter()            ##cria uma rota do fastAPI


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



@router.get('/list', status_code=status.HTTP_200_OK, response_model=ListUserSchema)
async def list_users(
        db: AsyncSession = Depends(get_session),
        offset: int = Query(0, ge=0, description='Número de registros para pular'),
        limit: int = Query(100, ge=1, le=100, description='Limite de registros'),
        search: Optional[str] = Query(None, description='Filtro de busca')
    ):
    # cria uma query no bd
    query = select(User)
    ## checagem do filtro de busca
    if search:
        search_filter = f'%{search}%'
        query = query.where((User.username.ilike(search_filter)) | User.email.ilike(search_filter))
    ## tratamento da query
    query = query.offset(offset).limit(limit)       # paginação da lista retornada
    ## executa a query
    result = await db.execute(query)        # retorna os registros de fato

    # modela esses resultados em formato de Model
    users = result.scalars().all()

    return{ 'users': users, 'offset': offset, 'limit': limit }


@router.get('/list/{id}', status_code=status.HTTP_200_OK, response_model=UserResponseSchema)
async def list_users_by_id(id: int, db: AsyncSession = Depends(get_session)):
    user_exists = await db.get(User, id)

    # Verificação da existência do usuario
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado"
        )
    
    return user_exists



@router.put('/update-user/{id}', status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema)
async def update_user(id: int, new_user: UpdateUserSchema, db: AsyncSession = Depends(get_session)):
    # Verificação dos dados
    ## Verifica se existe o id fornecido
    exist_user = await db.get(User, id)
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID não existente no banco')
    
    ## Carregar os dados recebidos em um model
    update_data = new_user.model_dump(exclude_unset=True)

    ## Verifica a disponibilidade do username se foi fornecido
    if 'username' in update_data and update_data['username'] != exist_user.username:
        exist_username = await db.scalar(select(exists().where(User.username == update_data['username'])))
        if exist_username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username já está em uso')
    
    ## Verifica a disponibilidade do email se foi fornecido
    if 'email' in update_data and update_data['email'] != exist_user.email:
        exist_email = await db.scalar(select(exists().where(User.email == update_data['email'])))
        if exist_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email já está em uso')

    if 'password' in update_data:
        update_data['password'] = get_password_hash(update_data['password'])

    # Atualiza o usuário com os dados fornecidos
    for field, value in update_data.items():
        setattr(exist_user, field, value)
    
    await db.commit()
    await db.refresh(exist_user)

    return exist_user


@router.delete('/delete-user/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, db: AsyncSession = Depends(get_session)):
    # Verificação dos dados
    ## Verificar existência de usuario com id dado
    exist_user = await db.get(User, id)
    if not exist_user: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Não existe usuário com esse ID"
        )
    
    #Aqui está tudo certo
    await db.delete(exist_user)
    await db.commit()

    return