from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.config import settings
from bson import ObjectId
from pymongo import MongoClient


class MongoDBHandler:
    def __init__(self):
        mongo_uri = settings.MONGO_URI
        self.client = MongoClient(mongo_uri)
        self.db = self.client.device_management
        self.users = self.db.users

        self.users.create_index("email", unique=True)

    def create_user(self, name: str, email: str, image: str) -> Dict:
        if not name or not email:
            raise ValueError("Name and email are required")

        if self.users.find_one({"email": email}):
            raise ValueError(f"User with email {email} already exists")

        user = {
            "name": name,
            "email": email,
            "image": image,
            "machines": [],
            "history": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        result = self.users.insert_one(user)
        return self.users.find_one({"_id": result.inserted_id})

    def find_user_by_email(self, email: str) -> Optional[Dict]:
        return self.users.find_one({"email": email})

    def add_machine(self, email: str, machine_name: str) -> Dict:
        user = self.find_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        for machine in user["machines"]:
            if machine["name"] == machine_name:
                if machine["status"] == "disconnected":
                    query = {"email": email, "machines.name": machine_name}
                    update = {"$set": {"machines.$.status": "connected"}}
                    self.users.update_one(query, update)
                updated_user = self.find_user_by_email(email)
                for machine in updated_user["machines"]:
                    machine["_id"] = str(machine["_id"])
                return updated_user

        machine = {
            "_id": ObjectId(),
            "name": machine_name,
            "status": "connected",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        result = self.users.update_one(
            {"email": email}, {"$push": {"machines": machine}}
        )

        if result.modified_count == 0:
            raise ValueError(f"Failed to add machine for user {email}")

        updated_user = self.find_user_by_email(email)
        for machine in updated_user["machines"]:
            machine["_id"] = str(machine["_id"])

        return updated_user

    def update_machine_status(self, email: str, machine_name: str, status: str) -> Dict:
        if status not in ["connected", "disconnected"]:
            raise ValueError("Status must be either 'connected' or 'disconnected'")

        user = self.find_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        machine_exists = any(
            machine["name"] == machine_name for machine in user["machines"]
        )
        if not machine_exists:
            raise ValueError(f"Machine {machine_name} not found for user {email}")

        query = {"email": email, "machines.name": machine_name}
        update = {"$set": {"machines.$.status": status}}

        self.users.update_one(query, update)

        updated_user = self.find_user_by_email(email)
        for machine in updated_user["machines"]:
            machine["_id"] = str(machine["_id"])

        return updated_user

    def add_report(
        self, email: str, machine_name: str, s3_url: str, description: str
    ) -> Dict:
        user = self.find_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        # Ensure machine_name is treated as a string
        machine_exists = any(
            machine["name"] == machine_name for machine in user["machines"]
        )
        if not machine_exists:
            raise ValueError(f"Machine {machine_name} not found for user {email}")

        report = {
            "_id": ObjectId(),
            "markdown_report_s3_url": s3_url,
            "machine_name": machine_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": description,
        }

        result = self.users.update_one({"email": email}, {"$push": {"history": report}})

        if result.modified_count == 0:
            raise ValueError(f"Failed to add report for user {email}")

        return self.find_user_by_email(email)

    def get_machine_reports(self, email: str, machine_id: str) -> List[Dict]:
        user = self.find_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        machine_obj_id = ObjectId(machine_id)
        reports = [
            report
            for report in user["history"]
            if report["machine_id"] == machine_obj_id
        ]

        return sorted(reports, key=lambda x: x["created_at"], reverse=True)

    def get_all_reports(self, email: str) -> List[Dict]:
        user = self.find_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        reports = [report for report in user["history"]]

        return sorted(reports, key=lambda x: x["created_at"], reverse=True)

    def get_machine_by_id(self, email: str, machine_id: str) -> Optional[Dict]:
        user = self.find_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        machine_obj_id = ObjectId(machine_id)
        for machine in user["machines"]:
            if machine["_id"] == machine_obj_id:
                return machine
        return None

    def delete_machine(self, email: str, machine_id: str) -> Dict:
        machine_obj_id = ObjectId(machine_id)
        result = self.users.update_one(
            {"email": email}, {"$pull": {"machines": {"_id": machine_obj_id}}}
        )

        if result.modified_count == 0:
            raise ValueError(f"Machine {machine_id} not found for user {email}")

        return self.find_user_by_email(email)

    def get_machines(self, email: str) -> List[Dict]:
        user = self.find_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        machines = user.get("machines", [])
        for machine in machines:
            machine["_id"] = str(machine["_id"])
        return machines
