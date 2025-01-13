from datetime import datetime
from configs.db import wallet_collection
from bson import ObjectId

class WalletModel:
    
    @staticmethod
    async def create_wallet(wallet_data: dict):
        wallet_data['isDeleted'] = False
        result = await wallet_collection.insert_one(wallet_data)
        return result
    
    @staticmethod
    async def get_wallet_addresses_by_userid_nocount(userid: str, limit: int = 10, offset: int = 0):
        total_count = await wallet_collection.count_documents({'userid': userid, 'isDeleted': False})
        wallets = await wallet_collection.find({'userid': userid, 'isDeleted': False}).sort('updated_at', -1).skip(offset).limit(limit).to_list(length=None)
        return wallets, total_count
    
    async def get_wallet_addresses_by_userid(userid: str, limit: int = 10, offset: int = 0):
        total_count = await wallet_collection.count_documents({'userid': userid, 'isDeleted': False})
        wallets = await wallet_collection.find({'userid': userid, 'isDeleted': False}).sort('updated_at', -1).skip(offset).limit(limit).to_list(length=None)
        return wallets, total_count
    
    @staticmethod
    async def get_wallet_by_address(wallet_address: str):
        wallet = await wallet_collection.find_one({'wallet_address': wallet_address, 'isDeleted': False})
        return wallet
    
    @staticmethod
    async def get_wallet_by_address_and_userid(wallet_address: str, userid: str):
        wallet = await wallet_collection.find_one({'wallet_address': wallet_address, 'userid': userid, 'isDeleted': False})
        return wallet
    
    @staticmethod
    async def update_wallet(wallet_id: str, update_data: dict):
        result = await wallet_collection.update_one(
            {'_id': ObjectId(wallet_id)},
            {'$set': update_data}
        )
        return result