from fastapi import FastAPI

from APP.routers import users, payments


app = FastAPI(
    title="Test_task_Dimatech",
    version="1.0",
    description="For payments"
)

app.include_router(users.router)
app.include_router(payments.router)



@app.get("/")
async def root():
    """
    Корневой маршрут
    """
    return {"message": "API payments"}
