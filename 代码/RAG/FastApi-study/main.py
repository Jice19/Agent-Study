# from fastapi import FastAPI , Query , Path
# from pydantic import BaseModel , Field
#
# # 创建FastAPI应用实例
# app = FastAPI()
#
# # class Item(BaseModel):
# #     name: str
# #     price: float
# #     is_offer: bool = None
#
# # 请求体校验
# # class Item(BaseModel):
# #     name: str
# #     description: str = Field(None, title="The description of the item", max_length=300)
# #     price: float = Field(..., gt=0, description="The price must be greater than zero")
# #     tax: float = None
#
# # 定义根路径的GET请求处理函数
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
# @app.get("/items/{item_id}")
# async def read_item(item_id: int):
#     return {"item_id": item_id}
#
# # @app.get("/items/")
# # async def read_items(skip: int = 0, limit: int = 10):
# #     return {"skip": skip, "limit": limit}
#
# # @app.post("/items/")
# # async def create_item(item: Item):
# #     return item
#
# # @app.get("/items/")
# # async def read_items(
# #     q: str = Query(
# #         None,
# #         min_length=3,
# #         max_length=50,
# #         regex="^fixedquery$"
# #     )
# # ):
# #     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
# #     if q:
# #         results.update({"q": q})
# #     return results
#
# @app.get("/items/{item_id}")
# async def read_items(
#     item_id: int = Path(..., title="The ID of the item to get", gt=0, le=1000),
#     q: str = None
# ):
#     results = {"item_id": item_id}
#     if q:
#         results.update({"q": q})
#     return results
#
#
# class Item(BaseModel):
#     name: str
#     description: str | None = None  # 等价于Optional[str]
#     price: float
#     tax: float | None = None
#
# @app.post("/items/", response_model=Item)
# async def create_item(item: Item):
#     return item

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader

# 1. 必须先创建 FastAPI 应用实例！
app = FastAPI()

API_KEY = "1234567890"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.get("/protected/", dependencies=[Depends(get_api_key)])
async def protected_route():
    return {"message": "This is a protected route"}