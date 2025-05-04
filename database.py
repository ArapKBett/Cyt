# database.py
from pymongo import MongoClient
from pymongo.errors import ConnectionError, PyMongoError
from loguru import logger
from config import Config
import datetime

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client["cyber_tricks"]
        self.collection = self.db["resources"]
        self._setup_logging()
        self._ensure_indexes()

    def _setup_logging(self):
        logger.add(Config.LOG_FILE, level=Config.LOG_LEVEL, rotation="10 MB")

    def _ensure_indexes(self):
        try:
            self.collection.create_index("type")
            self.collection.create_index("source")
            self.collection.create_index("timestamp")
            logger.info("Database indexes created successfully")
        except PyMongoError as e:
            logger.error(f"Failed to create indexes: {e}")

    def save_resource(self, resource):
        try:
            resource["timestamp"] = datetime.datetime.utcnow()
            self.collection.insert_one(resource)
            logger.info(f"Saved resource: {resource.get('title', 'Unknown')}")
        except PyMongoError as e:
            logger.error(f"Failed to save resource: {e}")

    def get_resources(self, query, limit=10):
        try:
            return list(self.collection.find(query).limit(limit))
        except PyMongoError as e:
            logger.error(f"Failed to fetch resources: {e}")
            return []

    def get_resource_by_type(self, resource_type):
        return self.get_resources({"type": resource_type})

    def close(self):
        try:
            self.client.close()
            logger.info("Database connection closed")
        except PyMongoError as e:
            logger.error(f"Failed to close database connection: {e}")
