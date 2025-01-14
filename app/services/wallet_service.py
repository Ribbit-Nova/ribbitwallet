from datetime import datetime
from app.core.generate_seed_wallet_address import generate_seed_wallet_address, get_wallet_address_from_seed_phrase, get_wallet_address_from_private_key
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
        logging.error('An error occurred', extra={'log_data': e})
        return None

async def create_wallet(userid: str, wallet: str):
    try:
        wallet_dict = wallet.dict()
        
        # create a wallet address and seed phrase
        wallet_address, seed_phrase, private_key = generate_seed_wallet_address()
        wallet_data = generate_new_wallet(wallet_dict['wallet_name'])
        wallet_data['userid'] = userid
        await WalletModel.create_wallet(wallet_data)
        return wallet_data
    except Exception as e:
        logging.error('An error occurred while creating the wallet', extra={'log_data': e})
        return None

async def import_wallet(userid: str, import_data: str):
    import_data = import_data.dict()
    wallet_name = import_data.get('wallet_name', 'Imported Wallet')
    private_key = None
    if 'seed_phrase' in import_data and import_data['seed_phrase']:
        wallet_address, private_key = get_wallet_address_from_seed_phrase(import_data['seed_phrase'])
    elif 'private_key' in import_data and import_data['private_key']:
        wallet_address, private_key = get_wallet_address_from_private_key(import_data['private_key'])
    else:
        raise HTTPException(status_code=400, detail='Either seed phrase or private key must be provided')

    existing_wallet = await WalletModel.get_wallet_by_address_and_userid(wallet_address, userid)
    if existing_wallet:
        logger.info('Wallet address already exists for the user')
        existing_wallet['updated_at'] = datetime.utcnow()
        await WalletModel.update_wallet(existing_wallet['_id'], existing_wallet)
        logger.info('Existing wallet updated successfully')
        return existing_wallet
    else: 
        wallet_data = {
            'wallet_name': wallet_name,
            'wallet_address': wallet_address,
            'seed_phrase': import_data.get('seed_phrase'),
            'private_key': private_key,
            'userid': userid,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Save the wallet data
        result = await WalletModel.create_wallet(wallet_data)
        logger.info('Wallet imported successfully', extra={'wallet_address': wallet_address})

        return wallet_data

async def generate_new_wallet(wallet_name: str):
    # Generate wallet address and seed phrase
    wallet_address, seed_phrase, private_key = generate_seed_wallet_address()
    
    # Create wallet for new user
    wallet_data = {
        'wallet_name': wallet_name,
        'wallet_address': wallet_address,
        'private_key': private_key,
        'seed_phrase': seed_phrase,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    logger.info('New wallet generated', extra={'log_data': {'wallet_name': wallet_name, 'wallet_address': wallet_address}})
    return wallet_data

async def update_wallet(userid: str, wallet_address: str, new_wallet_name: str):
    try:
        wallet = await WalletModel.get_wallet_by_address_and_userid(wallet_address, userid)
        if not wallet:
            logging.error('Wallet not found for userid.', extra={'log_data': {'userid': userid, 'wallet_address': wallet_address}})
            return None
        
        wallet['wallet_name'] = new_wallet_name
        wallet['updated_at'] = datetime.utcnow()
        await WalletModel.update_wallet(wallet['_id'], wallet)
        return wallet
    except Exception as e:
        logging.error('An error occurred while updating the wallet name', extra={'log_data': e})
        return None
    
async def delete_user_wallet(userid: str, wallet_address: str):
    try:
        wallet = await WalletModel.get_wallet_by_address_and_userid(wallet_address, userid)
        if not wallet:
            logging.error('Wallet not found for userid.', extra={'log_data': {'userid': userid, 'wallet_address': wallet_address}})
            return None
        
        await WalletModel.update_wallet(wallet['_id'], {'isDeleted': True})
        return wallet
    except Exception as e:
        logging.error('An error occurred while deleting the wallet.', extra={'log_data': e})
        return None