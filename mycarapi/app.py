from fastapi import FastAPI, status
from mycarapi.routers import users, brands

app = FastAPI()
app.include_router(
    router=users.router,
    prefix='/api/v1/users',        ##caminho da rota
    tags=['users']
)

app.include_router(
    router=brands.router,
    prefix='/api/v1/brands',        
    tags=['brands']
)

@app.get('/health_check', status_code=status.HTTP_200_OK)
def HealtCheck():
    return {'status': 'application running'}
