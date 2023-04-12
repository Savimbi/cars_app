from model import CarDB
from fastapi.encoders import jsonable_encoder

car = {"brand":"Fiat", "make":'500', "km":4000, "cm3":2000, "price":3000, "year":1998}
cdb= CarDB(**car)
jsonable_encoder(cdb)