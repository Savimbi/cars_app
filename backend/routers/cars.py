import shutil
from typing import List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Request, UploadFile, status,File
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from auth.authentication import AuthHandler
from models.model import CarBase, CarDB, CarUpdate


router = APIRouter()
auth_handler = AuthHandler()

@router.get("/", response_description="List of cars")
async def list_cars(
    request: Request,
    min_price: int = 0,
    max_price: int = 100000,
    brand: Optional[str]=None,
    page:int=1
    ) -> List[CarDB]:
    RESULTS_PER_PAGE =25
    skip = (page-1)*RESULTS_PER_PAGE
    query = {"price":{"$lt":max_price, "$gt":min_price} }
    if brand:
        query["brand"] = brand
        
    full_query = request.app.mongodb['cars1'].find(query).sort("_id",-1).skip(skip).limit(RESULTS_PER_PAGE)
    results = [ CarDB(**raw_car) async for raw_car in full_query ]
    
    return results


@router.post("/", response_description="Add new car")
async def create_car(request: Request, car: CarBase = Body(...),
                     userId=Depends(auth_handler.auth_wrapper)):
    car = jsonable_encoder(car)
    car["owner"] = userId    
    new_car = await     request.app.mongodb["cars1"].insert_one(car)
    created_car = await request.app.mongodb["cars1"].find_one(
        {"_id": new_car.inserted_id}
    )
    return JSONResponse(status_code=status.HTTP_201_CREATED, 
        content=created_car)
    
@router.post("/upload")
async def upload(file: UploadFile = File(...) ):
    print("Get here?")
    try:
        with open("destination.jpg", 'wb') as f:
            shutil.copyfileobj(file.file, f)
        return {"filename": file.filename}
    except Exception:
        return HTTPException(status_code=404, detail=f'There was error to upload file')
    finally:
        file.file.close()
    
    
@router.get("/{id}", response_description="Get a single car")
async def show_car(id: str, request: Request):
    if (car := await request.app.mongodb["cars1"].find_one({"_id":id}) ) is not None:
        return CarDB (**car)
    raise HTTPException(status_code = 404, detail=f"Car with id: {id} not found")

@router.patch("/{id}", response_description="Update car")
async def update_task(id: str, request: Request, car: CarUpdate = Body(...), userId=Depends(auth_handler.auth_wrapper)):
    user = await request.app.mongodb["users"].find_one({"_id": userId})
    findCar = await request.app.mongodb["cars"].find_one({"_id": id})
    
    if (findCar["owner"] != userId) and user["role"] != "ADMIN":
        raise HTTPException(
            status_code=401, detail="Only the owner or an Advanced user can update the car informations"
        )
    await request.app.mongodb['cars1'].update_one( {"_id": id}, {"$set": car.dict(exclude_unset=True)})
    if (car := await request.app.mongodb['cars1'].find_one({"_id": id})) is not None:
            return CarDB(**car)
    raise HTTPException(status_code=404, detail=f"Car with{id} not found")
    
@router.delete("/{id}", response_description="Delete car")
async def delete_task(id: str, request: Request):
    delete_result = await request.app.mongodb['cars1'].delete_one({"_id": id})
    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
    raise HTTPException(status_code=404, detail=f"Car with {id} not found")
    