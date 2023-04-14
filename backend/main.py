from decouple import config
from fastapi import FastAPI, File, HTTPException, Request, Body, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn
from routers.cars import router as cars_router
from routers.users import router as users_router
from fastapi.middleware.cors import CORSMiddleware



DB_URL = config('DB_URL', cast=str)
DB_NAME = config('DB_NAME', cast=str)

origins = ["*"]

app = FastAPI()
app.include_router(cars_router,prefix="/cars", tags=["cars"])
app.include_router(users_router, prefix="/users", tags=["users"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],
)
  
        
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(DB_URL)
    app.mongodb = app.mongodb_client[DB_NAME]
    
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    
    
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True
    )