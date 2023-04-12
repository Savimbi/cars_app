from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from model.model import CarBase, CarDB


router = APIRouter()

@router.get("/", response_description="List of cars")
async def list_cars():
    return {"data":"All list of cars goes here"}


@router.post("/", response_description="Add new car")
async def create_car(request: Request, car: CarBase = Body(...)):
    car = jsonable_encoder(car)
    new_car = await     request.app.mongodb["cars1"].insert_one(car)
    created_car = await request.app.mongodb["cars1"].find_one(
        {"_id": new_car.inserted_id}
    )
    return JSONResponse(status_code=status.HTTP_201_CREATED, 
        content=created_car)
    
@router.get("/{id}", response_description="Get a single car")
async def show_car(id: str, request: Request):
    if (car := await request.app.mongodb["cars1"].find_one({"_id":id}) ) is not None:
        return CarDB (**car)
    raise HTTPException(status_code = 404, detail=f"Car with id: {id} not found")
    