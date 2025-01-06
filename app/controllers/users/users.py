from fastapi import APIRouter, HTTPException, Depends, Request
from app.core.jwt_handler import generate_jwt_token
from app.schemas.wallet import WalletListResponse
import logging
from app.schemas.users import SeedImportSignUpRequest, SignUpRequest, SignUpTokenResponse, SocialSignUpRequest, UpdateUserRequest, UpdateUserResponse, UserDetailsResponse, WalletSignUpRequest
from app.common.header import authorization_required
from app.services.user_service import sign_up_user, get_user_by_userid, update_user_by_id

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@router.put("/signup", response_model=SignUpTokenResponse, summary="Sign Up", description="Sign up using either Wallet or Social method.")
async def sign_up(user: SignUpRequest, request: Request):
    try:
        logger.info("Sign up request received")
        user = await sign_up_user(request)
        
        # Transform the wallets into the response format
        wallet_list = [
            WalletListResponse(
                wallet_name=wallet["wallet_name"],
                wallet_address=wallet["wallet_address"], 
                seed_phrase=wallet["seed_phrase"], 
                created_at=wallet["created_at"].isoformat(), 
                updated_at=wallet["updated_at"].isoformat()
            )
            for wallet in user["wallets"]
        ]

        logger.info("User signed up successfully")
        return SignUpTokenResponse(
            access_token=user["access_token"],
            token_type="bearer",
            wallets=wallet_list
        )
    except Exception as e:
        logger.error("Error signing up user:", {str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("", response_model=UpdateUserResponse)
async def update(user: UpdateUserRequest, request: Request, current_user: dict = Depends(authorization_required)):
    try:
        logger.info("Update user request received")
        user_dict = {k: v for k, v in user.dict().items() if v is not None}
        if not user_dict:
            raise HTTPException(status_code=400, detail="No fields to update")

        result = await update_user_by_id(current_user["sub"], user_dict)
        
        if result.modified_count == 1:
            updated_user = await get_user_by_userid(current_user["sub"])
            additional_claims = {
                "first_name": updated_user["first_name"],
                "last_name": updated_user["last_name"],
                "user_type": updated_user["user_type"]
            }
            accessToken = generate_jwt_token(updated_user["userid"], additional_claims)
            logger.info("User updated successfully")
            return SignUpTokenResponse(
                access_token=accessToken, 
                token_type="bearer"
            )
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error("Error updating user:", {str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me", response_model=UserDetailsResponse, summary="Get User Details", description="Get user details using a valid JWT token.")
async def get_user_details(current_user: dict = Depends(authorization_required)):
    try:
        logger.info("Get user details request received")
        userid = current_user["sub"]
        user = await get_user_by_userid(userid)
        if user:
            logger.info("User details fetched successfully")
            return user
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error("Error fetching user details:", {str(e)})
        raise HTTPException(status_code=500, detail=str(e))