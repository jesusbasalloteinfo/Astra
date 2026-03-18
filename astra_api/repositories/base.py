from typing import TypeVar, Generic, Type, Optional
from pydantic import BaseModel
from core.MongoDBConnector import db_connector
from bson import ObjectId

T = TypeVar('T', bound=BaseModel)

class BaseMongoRepository(Generic[T]):
    def __init__(self, collection_name: str, model_class: Type[T]):
        self.collection_name = collection_name
        self.model_class = model_class

    @property
    def collection(self):
        """Get the corresponding collection dinamically"""
        return db_connector.get_collection(self.collection_name)

    async def insert_one(self, model: T) -> str:
        """Insert an element into the collection"""
        # exclude_none avoids saving none data, like initial id
        data = model.model_dump(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(data)
        return str(result.inserted_id)

    async def find_one(self, query: dict) -> Optional[T]:
        """Find an element inside the collection"""
        doc = await self.collection.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"]) # Mongo id to str id
            return self.model_class(**doc)
        return None