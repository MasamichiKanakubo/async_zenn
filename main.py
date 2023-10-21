# 必要なライブラリをインポート
import os
import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL
from pymongo import MongoClient
from fastapi import FastAPI, BackgroundTasks, Depends
import asyncio
from dotenv import load_dotenv
from typing import List

# .envファイルを読み込む
load_dotenv()

client = MongoClient(os.environ["MONGO_URL"])
db = client["FastAPI"]
collection = db["User"]


@strawberry.type
class User:
    user_id: int
    name: str
    age: int
  
# 入力データの定義をする（追加）  
@strawberry.input
class Register:
    user_id: int
    name: str
    age: int


# クエリの定義をする
@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(id=1, name="Taro", age=19)
    
async def schedule_user_deletion(user_id):
    await asyncio.sleep(30)
    collection.delete_one({"user_id": user_id})

@strawberry.type
class Mutation:
    @strawberry.field
    async def register(self, regist:Register) -> User:
        collection.insert_one(regist.__dict__)
        asyncio.create_task(schedule_user_deletion(regist.user_id))
        return regist

schema = strawberry.Schema(query=Query, mutation=Mutation)


graphql_app = GraphQL(schema)

app = FastAPI()

app.add_route("/graphql", graphql_app)
