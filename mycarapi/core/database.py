from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from mycarapi.core.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)

# cria uma sessão no bd e "empresta" a conexão(yield)
async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        print("Conexão com DB inicializada")
        yield session
        print("Conexão encerrada")