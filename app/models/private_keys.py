from datetime import datetime
from configs.db import private_keys_collection
from bson import ObjectId
from app.schemas.wallet import WalletNetwork

class PrivateKeysModel:
    
    def __init__(self, userid, private_key, network: WalletNetwork):
        self.userid = userid
        self.private_key = private_key
        self.network = network
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def save(self):
        if not self.private_key:
            self.network = WalletNetwork.SUPRA
        
        private_keys_collection.insert_one({
            'userid': self.userid,
            'private_key': self.private_key,
            'network': self.network.value,  # Save the enum value
            'created_at': self.created_at,
            'updated_at': self.updated_at
        })

    def save_private_key(userid, private_key, network=WalletNetwork.SUPRA):
        private_key_model = PrivateKeysModel(userid, private_key, network)
        return private_key_model.save()

    def get_by_userid(userid):
        data = private_keys_collection.find_one({'userid': userid})
        if data:
            data['network'] = Network(data['network'])  # Convert back to enum
        return data