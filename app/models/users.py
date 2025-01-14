from datetime import datetime
import enum
from bson import ObjectId # type: ignore
from configs.db import user_collection

class UserModel:

    def __init__(
            self, 
            first_name: str, 
            last_name: str, 
            email_address: str, 
            biography: str, 
            personal_website: str, 
            twitter_handle: str,
            reddit_handle: str,
            github_username: str,
            phone_login_enabled: bool,
            phone_unique_id: str,
            signup_method: str,
            social_id: str,
            social_platform: str
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address
        self.biography = biography
        self.personal_website = personal_website
        self.twitter_handle = twitter_handle
        self.reddit_handle = reddit_handle
        self.github_username = github_username
        self.phone_login_enabled = phone_login_enabled
        self.phone_unique_id = phone_unique_id
        self.signup_method = signup_method
        self.social_id = social_id
        self.social_platform = social_platform
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @staticmethod
    async def create_user(user_data: dict):
        user_data['created_at'] = datetime.utcnow()
        user_data['updated_at'] = datetime.utcnow()
        result = await user_collection.insert_one(user_data)
        return result

    @staticmethod
    async def update_user(userid: str, update_data: dict):
        update_data['updated_at'] = datetime.utcnow()
        result = await user_collection.update_one({'userid': userid}, {'$set': update_data})
        return result

    @staticmethod
    async def find_user_by_id(userid: str):
        user = await user_collection.find_one({'_id': ObjectId(userid)})
        return user
    
    @staticmethod
    async def get_user_by_userid(userid: str):
        user = await user_collection.find_one({'userid': userid})
        return user
    
    @staticmethod
    async def get_user_by_social_id(social_id: str):
        user = await user_collection.find_one({'social_id': social_id})
        return user