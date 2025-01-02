from fastapi import HTTPException, Request # type: ignore
from datetime import datetime
import logging
from app.core.generate_seed_wallet_address import generate_seed_wallet_address, get_wallet_address_from_seed_phrase
from app.schemas.users import SignUpMethod, SignUpRequest, UserType
from app.models.users import UserModel
from app.models.wallet import WalletModel
from app.core.jwt_handler import generate_jwt_token
import uuid

logger = logging.getLogger(__name__)

async def sign_up_user(user: Request):
    try:
        logging.info(f"Received user sign-up request: {user}")
        request_data = await user.json()
        
        # Sanitize the request data
        user_dict = {k: v.strip() if isinstance(v, str) else v for k, v in request_data.items()}

        print(user_dict, "################## user_dict 1")
        
        is_new_user = True
        wallet_list = None
        wallet_data = {}

        if user_dict["signup_method"] == SignUpMethod.social:
            logging.info("Processing social sign-up")
            user_dict, wallet_data, is_new_user, wallet_list = await signup_by_social(user_dict['social_platform'], user_dict['social_id'])

        elif user_dict["signup_method"] == SignUpMethod.wallet:
            logging.info("Processing wallet sign-up")
            wallet_name = user_dict.get('wallet_name', '')
            wallet_data = await new_wallet_data(wallet_name)

        elif user_dict["signup_method"] == SignUpMethod.seed_import:
            logging.info("Processing seed import sign-up")
            wallet_data, user_dict, is_new_user = await signup_by_seed(user_dict['seed_phrase']) 

        else:
            raise HTTPException(status_code=400, detail="Invalid sign-up method")
        
        if is_new_user:
            user_dict.update({
                "userid": str(uuid.uuid4()),  # Use UUID version 4
                "user_type": UserType.user.value,  # Ensure user_type is a string
            })
            logging.info(f"user_dict details: {user_dict}")

            # Insert user information into user collection
            userResult = await UserModel.create_user(user_dict)
            logging.info(f"User creation result: {userResult}")

            if not userResult.inserted_id:
                raise HTTPException(status_code=500, detail="User could not be created")
    
        # Check if wallet data exists and add userid
        if wallet_data and 'userid' not in wallet_data:
            wallet_data['userid'] = user_dict['userid']
            
            # add wallet in db
            result = await WalletModel.create_wallet(wallet_data)
            logging.info(f"Wallet creation result: {result}")
        
            if not result.inserted_id:
                raise HTTPException(status_code=500, detail="Wallet could not be created")
            
            wallet_list = [wallet_data]
        
        elif wallet_data: 
            wallet_list = [wallet_data]
        
        access_token = generate_jwt_token(user_dict['userid'], user_dict['user_type'])
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "wallets": wallet_list
        }
    except Exception as e:
        logging.error(f"Error during sign-up: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def signup_by_social(social_platform, social_id):
    if not social_platform or not social_id:
        raise HTTPException(status_code=400, detail="Social platform and social ID are required for social sign-up")

    # Check if social ID already exists
    existing_user = await UserModel.get_user_by_social_id(social_id)
    logging.info(f"Existing user found: {existing_user}")
    if existing_user:
        logging.info(f"User with social ID {social_id} already exists, assigning existing user details")
        wallets, total_counts = await WalletModel.get_wallet_addresses_by_userid(existing_user['userid'])
        return existing_user, {}, False, wallets
    else:
        wallet_data = await new_wallet_data(f"{social_platform} Wallet")
        return {
            "signup_method": SignUpMethod.social,
            "social_platform": social_platform,
            "social_id": social_id,
        }, wallet_data, True, []

async def new_wallet_data(wallet_name: str):
    # Generate wallet address and seed phrase
    wallet_address, seed_phrase = generate_seed_wallet_address()
    
    # Create wallet for new user
    wallet_data = {
        "wallet_name": wallet_name,
        "wallet_address": wallet_address,
        "seed_phrase": seed_phrase,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    return wallet_data

async def signup_by_seed(seed_phrase):
    if not seed_phrase:
        raise HTTPException(status_code=400, detail="Seed phrase is required for seed import sign-up")
    
    wallet_address = get_wallet_address_from_seed_phrase(seed_phrase)
    logging.info(f"Wallet address imported: {wallet_address}")
    existing_wallet = await WalletModel.get_wallet_by_address(wallet_address)
    if existing_wallet:
        logger.info(f"Wallet with address {wallet_address} already exists.")
        existing_user = await UserModel.get_user_by_userid(existing_wallet['userid'])
        logging.info(f"Existing user found: {existing_user}")

        if existing_user:
            logging.info(f"User with userid {existing_user['userid']} already exists, assigning existing user details")
            return existing_wallet, existing_user, False
        else:
            return existing_wallet, existing_user, False
    else:
        wallet_data = {
            "wallet_name": "Imported Wallet",
            "wallet_address": wallet_address,
            "seed_phrase": seed_phrase,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        return wallet_data, {
            "signup_method": SignUpMethod.seed_import
        }, True

async def update_user_by_id(userid: str, update_data: dict):
    try:
        result = await UserModel.update_user(userid, update_data)
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found or no changes made")
        return result
    except Exception as e:
        logging.error(f"Error updating user by id: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_user_by_userid(userid: str):
    try:
        user = await UserModel.get_user_by_userid(userid)
        if user:
            return user
        else:
            logger.error(f"User not found with userid: {userid}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user by userid: {str(e)}")
        raise e