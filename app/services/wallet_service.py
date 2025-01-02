from datetime import datetime
from app.core.generate_seed_wallet_address import decrypt_seed_phrase, generate_seed_wallet_address
from app.core.jwt_handler import generate_jwt_token
from app.models.wallet import WalletModel
from eth_account import Account # type: ignore
import logging

logger = logging.getLogger(__name__)

async def get_wallet_addresses_by_userid(userid: str, limit: int = 10, offset: int = 0):
    try:
        wallets, total_count = await WalletModel.get_wallet_addresses_by_userid(userid, limit, offset)
        return wallets, total_count
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def create_wallet(user_id: str, wallet: str):
    try:
        wallet_dict = wallet.dict()
        
        # create a wallet address and seed phrase
        wallet_address, seed_phrase = generate_seed_wallet_address()
        wallet_data = {
            "wallet_name": wallet_dict["wallet_name"],
            "wallet_address": wallet_address,
            "seed_phrase": seed_phrase,
            "userid": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await WalletModel.create_wallet(wallet_data)
        return wallet_data
    except Exception as e:
        logger.error(f"An error occurred while creating the wallet: {e}")
        return None

async def update_wallet(user_id: str, wallet_address: str, new_wallet_name: str):
    try:
        wallet = await WalletModel.get_wallet_by_address_and_userid(wallet_address, user_id)
        if not wallet:
            logger.error(f"Wallet not found for user_id: {user_id} and wallet_address: {wallet_address}")
            return None
        
        wallet["wallet_name"] = new_wallet_name
        wallet["updated_at"] = datetime.utcnow()
        await WalletModel.update_wallet(wallet["_id"], wallet)
        return wallet
    except Exception as e:
        logger.error(f"An error occurred while updating the wallet name: {e}")
        return None
    
async def delete_user_wallet(user_id: str, wallet_address: str):
    print("$############################")
    try:
        wallet = await WalletModel.get_wallet_by_address_and_userid(wallet_address, user_id)
        if not wallet:
            logger.error(f"Wallet not found for user_id: {user_id} and wallet_address: {wallet_address}")
            return None
        
        await WalletModel.update_wallet(wallet["_id"], {"isDeleted": True})
        return wallet
    except Exception as e:
        logger.error(f"An error occurred while deleting the wallet: {e}")
        return None