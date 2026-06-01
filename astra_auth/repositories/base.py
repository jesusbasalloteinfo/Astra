"""
ASTRA - Automated Smart Telescope Remote Assistant
Copyright (C) 2026 Jesus Basallote

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import List, TypeVar, Generic, Type, Optional
from pydantic import BaseModel
from core.MongoDBConnector import db_connector
from bson import ObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING

T = TypeVar('T', bound=BaseModel)

class BaseMongoRepository(Generic[T]):
    """Generic base repository for MongoDB operations using Pydantic models."""

    def __init__(self, collection_name: str, model_class: Type[T]):
        """Initialize the repository.

        Args:
            collection_name (str): The name of the MongoDB collection.
            model_class (Type[T]): The Pydantic model class associated with this repository.
        """
        self.collection_name = collection_name
        self.model_class = model_class

    @property
    def collection(self):
        """Get the corresponding MongoDB collection dynamically.

        Returns:
            Collection: The MongoDB collection instance.
        """
        return db_connector.get_collection(self.collection_name)

    async def setup_indexes(self):
        """Set the collection indexes. Should be overridden by subclasses."""
        pass

    async def insert_one(self, model: T) -> str:
        """Insert a single document into the collection.

        Args:
            model (T): The Pydantic model instance to insert.

        Returns:
            str: The string representation of the inserted document's ID.
        """
        # exclude_none avoids saving none data, like initial id
        data = model.model_dump(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(data)
        return str(result.inserted_id)

    async def update_one(self, query: dict, update_data: dict) -> bool:
        """Update a single document matching the query.

        Args:
            query (dict): The MongoDB query to match the document.
            update_data (dict): The update operations (e.g., {"$set": ...}).

        Returns:
            bool: True if a document was matched and updated, False otherwise.
        """
        # update_data must include the Mongo operators like $set, $push, etc.
        result = await self.collection.update_one(query, update_data)
        return result.matched_count > 0
    
    async def find_one(self, query: dict) -> Optional[T]:
        """Find a single document matching the query.

        Args:
            query (dict): The MongoDB query to match the document.

        Returns:
            Optional[T]: The Pydantic model instance if found, otherwise None.
        """
        doc = await self.collection.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"]) # Mongo id to str id
            return self.model_class(**doc)
        return None
    
    async def find_many(self, query: dict) -> List[T]:
        """Find multiple documents matching the query.

        Args:
            query (dict): The MongoDB query to match the documents.

        Returns:
            List[T]: A list of Pydantic model instances.
        """
        cursor = self.collection.find(query)
        docs = await cursor.to_list(length=None)
        
        results = []
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            results.append(self.model_class(**doc))
        return results

    async def delete_one(self, query: dict) -> bool:
        """Delete a single document matching the query.

        Args:
            query (dict): The MongoDB query to match the document.

        Returns:
            bool: True if a document was deleted, False otherwise.
        """
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0