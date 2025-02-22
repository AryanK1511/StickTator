from typing import Dict

from app.database.mongo import MongoDBHandler


class UserService:
    @staticmethod
    def create_user(name: str, email: str, image: str) -> Dict:
        return MongoDBHandler().create_user(name, email, image)
