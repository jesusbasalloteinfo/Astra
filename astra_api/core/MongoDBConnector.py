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

"""
Database connector for MongoDB using AsyncMongoClient.
"""
import logging
import os
from pymongo import AsyncMongoClient
from typing import Optional
from core.logging_utils import get_logger
from dotenv import load_dotenv 

load_dotenv() 
logging.getLogger("pymongo").setLevel(logging.INFO)

class MongoDBConnector:
    """
    Handles connections to a MongoDB instance.

    Provides methods to establish, close, and retrieve database and collection
    references asynchronously.
    """
    def __init__(self):
        """Initialize the MongoDB connector."""
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "27017"))
        self.user = os.getenv("DB_USER", None)
        self.pswd = os.getenv("DB_PASSWORD", None)
        self.db_name = os.getenv("DB_NAME", "default")
        self.client: Optional[AsyncMongoClient] = None
        self.logger = get_logger("MongoDBConnector")

    async def connect(self):
        """
        Establish connection to MongoDB.

        Raises:
            Exception: If the connection fails.
        """
        if self.client is None:
            try:
                if self.user and self.pswd:
                    uri = f"mongodb://{self.user}:{self.pswd}@{self.host}:{self.port}"
                else:
                    uri = f"mongodb://{self.host}:{self.port}"

                self.logger.debug(f"Connecting to MongoDB at {self.host}:{self.port}...")
                self.client = AsyncMongoClient(uri, tz_aware=True)

                self.logger.info("Succesfully established connection with MongoDB.")
            except Exception as e:
                self.logger.error(f"Error connecting to MongoDB", details=e)
                raise

    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client is not None:
            self.logger.debug("Closing MongoDB connection...")
            await self.client.close()
            self.client = None

    def get_db(self):
        """
        Get a MongoDB database instance.

        Returns:
            Database: The MongoDB database instance.

        Raises:
            RuntimeError: If the client is not connected.
        """
        if self.client is None:
            raise RuntimeError("DB connection not found")
        return self.client[self.db_name]

    def get_collection(self, collection_name: str):
        """
        Get a MongoDB collection.

        Args:
            collection_name (str): Name of the collection to retrieve.

        Returns:
            Collection: The MongoDB collection instance.
        """
        return self.get_db()[collection_name]

# Module Singleton
db_connector:MongoDBConnector = MongoDBConnector()
