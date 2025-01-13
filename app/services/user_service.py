from fastapi import HTTPException, Request # type: ignore
from datetime import datetime
import logging
from app.core.generate_seed_wallet_address import generate_seed_wallet_address, get_wallet_address_from_seed_phrase, get_wallet_address_from_private_key
from app.schemas.users import SignUpMethod, SignUpRequest, UserType
from app.models.users import UserModel
from app.models.wallet import WalletModel
from app.core.jwt_handler import generate_jwt_token
import uuid
from app.services.wallet_service import generate_new_wallet

logger = logging.getLogger(__name__)

async def sign_up_user(user: Request):
    try:
        logging.info('Received user sign-up request.')
        request_data = await user.json()
        
        # Sanitize the request data
        user_dict = {k: v.strip() if isinstance(v, str) else v for k, v in request_data.items()}
        is_new_user = True
        wallet_list = None
        wallet_data = {}
        user_data = {}
        if user_dict['signup_method'] == SignUpMethod.social:
            logging.info('Processing social sign-up')
            user_data, wallet_data, is_new_user, wallet_list = await signup_by_social(user_dict['social_platform'], user_dict['social_id'])

        elif user_dict['signup_method'] == SignUpMethod.wallet:
            logging.info('Processing wallet sign-up')
            wallet_name = user_dict.get('wallet_name', '')
            wallet_data = await generate_new_wallet(wallet_name)

        elif user_dict['signup_method'] == SignUpMethod.seed_import:
            logging.info('Processing seed import sign-up')
            user_data, wallet_data, is_new_user = await signup_by_seed(user_dict['seed_phrase'])

        elif user_dict['signup_method'] == SignUpMethod.private_key_import:
            logging.info('Processing private key import sign-up')
            user_data, wallet_data, is_new_user = await signup_by_private_key(user_dict['private_key'])
            
        else:
            raise HTTPException(status_code=400, detail='Invalid sign-up method')
        
        # Add common parameters if available in request_data
        common_params = ['email_address', 'first_name', 'last_name', 'phone_login_enabled', 'phone_unique_id']
        for param in common_params:
            if param in request_data:
                user_data[param] = request_data[param]

        if is_new_user:
            user_data.update({
                'userid': str(uuid.uuid4()),  # Use UUID version 4
                'user_type': UserType.user.value,  # Ensure user_type is a string
            })
            logging.info('Prepared user details for sign up.', extra={'log_data':  str(user_data)})

            # Insert user information into user collection
            userResult = await UserModel.create_user(user_data)
            logging.info('User creation result:', extra={'log_data': str(userResult)})

            if not userResult.inserted_id:
                raise HTTPException(status_code=500, detail='User could not be created')
        if not is_new_user:
            logging.info('User already exists, updating user details.', extra={'log_data': str(user_data)})
            await update_user_by_id(user_data['userid'], user_data)
    
        # Check if wallet data exists and add userid
        if wallet_data and 'userid' not in wallet_data:
            wallet_data['userid'] = user_data['userid']
            
            # add wallet in db
            result = await WalletModel.create_wallet(wallet_data)
            logging.info('Wallet creation result.', extra={'log_data':  str(result)})
        
            if not result.inserted_id:
                raise HTTPException(status_code=500, detail='Wallet could not be created')
            
            wallet_list = [wallet_data]
        
        elif wallet_data: 
            wallet_list = [wallet_data]
        
        access_token = generate_jwt_token(user_data['userid'], user_data['user_type'])
        return {
            'access_token': access_token,
            'token_type': 'bearer',
            'wallets': wallet_list
        }
    except Exception as e:
        logging.error('Error during sign-up', extra={'log_data': e})
        raise HTTPException(status_code=500, detail=str(e))

async def signup_by_social(social_platform, social_id):
    if not social_platform or not social_id:
        raise HTTPException(status_code=400, detail='Social platform and social ID are required for social sign-up')

    # Check if social ID already exists
    existing_user = await UserModel.get_user_by_social_id(social_id)
    logging.info('Existing user found.', extra={'log_data': str(existing_user)})
    if existing_user:
        logging.info('User with social ID already exists, assigning existing user details.', extra={'log_data': {'social_id': social_id}})
        wallets, total_counts = await WalletModel.get_wallet_addresses_by_userid(existing_user['userid'])
        return existing_user, {}, False, wallets
    else:
        wallet_data = await generate_new_wallet(f'{social_platform} Wallet')
        return {
            'signup_method': SignUpMethod.social,
            'social_platform': social_platform,
            'social_id': social_id,
        }, wallet_data, True, []

async def signup_by_seed(seed_phrase):
    if not seed_phrase:
        raise HTTPException(status_code=400, detail='Seed phrase is required for seed import sign-up')
    
    wallet_address, private_key = get_wallet_address_from_seed_phrase(seed_phrase)
    logging.info('Wallet address imported:', extra={'log_data': {'wallet_address': wallet_address}})
    existing_wallet = await WalletModel.get_wallet_by_address(wallet_address)
    if existing_wallet:
        logging.info('Wallet with address already exists.', extra={'log_data': {'wallet_address': wallet_address}})
        existing_user = await UserModel.get_user_by_userid(existing_wallet['userid'])
        logging.info('Existing user found: %s', existing_user)

        if existing_user:
            logging.info('User with userid already exists, assigning existing user details.', extra={'log_data': {'userid': existing_wallet['userid']}})
            return existing_user, existing_wallet, False
        else:
            return existing_user, existing_wallet, False
    else:
        wallet_data = {
            'wallet_name': 'Imported Wallet',
            'wallet_address': wallet_address,
            'private_key': private_key,
            'seed_phrase': seed_phrase,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        return {
            'signup_method': SignUpMethod.seed_import
        }, wallet_data, True

async def signup_by_private_key(private_key):
    if not private_key:
        raise HTTPException(status_code=400, detail='Private key is required for private key import sign-up')

    wallet_address, private_key = get_wallet_address_from_private_key(private_key)
    logging.info('Wallet address imported:', extra={'log_data': {'wallet_address': wallet_address}})
    existing_wallet = await WalletModel.get_wallet_by_address(wallet_address)
    if existing_wallet:
        logging.info('Wallet with address already exists.', extra={'log_data': {'wallet_address': wallet_address}})
        existing_user = await UserModel.get_user_by_userid(existing_wallet['userid'])
        logging.info('Existing user found.',   extra={'log_data':str(existing_user)})

        if existing_user:
            logging.info('User with userid already exists, assigning existing user details.', extra={'log_data': {'userid': existing_wallet['userid']}})
            return existing_user, existing_wallet, False
        else:
            return existing_user, existing_wallet, False
    else:
        wallet_data = {
            'wallet_name': 'Imported Wallet',
            'wallet_address': wallet_address,
            'private_key': private_key,
            'seed_phrase': '',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        return {
            'signup_method': SignUpMethod.private_key_import
        }, wallet_data, True

async def update_user_by_id(userid: str, update_data: dict):
    try:
        result = await UserModel.update_user(userid, update_data)
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail='User not found or no changes made')
        return result
    except Exception as e:
        logging.error('Error updating user by id', extra={'log_data': e})
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_user_by_userid(userid: str):
    try:
        user = await UserModel.get_user_by_userid(userid)
        if user:
            return user
        else:
            logging.error('User not found with userid', extra={'log_data': e})
            return None
    except Exception as e:
        logging.error('Error fetching user by userid', extra={'log_data': e})
        raise e