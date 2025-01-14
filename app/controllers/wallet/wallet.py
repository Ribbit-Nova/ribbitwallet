from fastapi import APIRouter, HTTPException, Depends, Query
from app.core.generate_seed_wallet_address import encrypt_seed_phrase
from app.schemas.wallet import WalletCreateRequest, WalletCreateResponse, WalletList, WalletListResponse
import logging
from fastapi import Depends
from app.common.header import authorization_required
from app.services.wallet_service import create_wallet, get_wallet_addresses_by_userid, update_wallet, delete_user_wallet

router = APIRouter(
    prefix="/wallet",
    tags=["wallet"]
)

@router.get("", response_model=WalletList, summary="Get Wallet List", description="Retrieves a list of wallets for the authenticated user.")
async def get_wallet_list(current_user: dict = Depends(authorization_required), limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
    try:
        # Fetch the wallets associated with the current user using the service function
        wallets, total_count = await get_wallet_addresses_by_userid(current_user["sub"], limit, offset)
        logging.info("Fetched wallets for user",{current_user['sub']})

        # Transform the wallets into the response format
        wallet_list = [
            WalletListResponse(
                wallet_name=wallet["wallet_name"],
                wallet_address=wallet["wallet_address"], 
                seed_phrase=wallet["seed_phrase"], 
                created_at=wallet["created_at"].isoformat(), 
                updated_at=wallet["updated_at"].isoformat()
            )
            for wallet in wallets
        ]

        return WalletList(
            total_count=total_count,
            wallets=wallet_list
        )
    except Exception as e:
        logging.error("Error fetching wallet list:", {str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@router.put("", response_model=WalletCreateResponse, summary="Create Wallet", description="Create a new wallet")
async def generate_wallet(request: WalletCreateRequest, current_user: dict = Depends(authorization_required)):
    try:
        wallet = await create_wallet(current_user["sub"], request)

        return WalletCreateResponse(
            message="Wallet created successfully.",
            wallet=WalletListResponse(
                wallet_name=wallet["wallet_name"],
                wallet_address=wallet["wallet_address"], 
                seed_phrase=wallet["seed_phrase"], 
                created_at=wallet["created_at"].isoformat(), 
                updated_at=wallet["updated_at"].isoformat()
            )
        )
    except Exception as e:
        logging.error("Error generating wallet:", {str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{wallet_id}", response_model=WalletCreateResponse, summary="Patch Wallet", description="Patch wallet name based on wallet id")
async def patch_wallet(wallet_id: str, request: WalletCreateRequest, current_user: dict = Depends(authorization_required)):
    try:
        # Assuming there is a service function to update the wallet name
        wallet = await update_wallet(current_user["sub"], wallet_id, request.wallet_name)
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        return WalletCreateResponse(
            message="Wallet updated successfully",
            wallet=WalletListResponse(
                wallet_name=wallet["wallet_name"],
                wallet_address=wallet["wallet_address"], 
                seed_phrase=wallet["seed_phrase"], 
                created_at=wallet["created_at"].isoformat(), 
                updated_at=wallet["updated_at"].isoformat()
            )
        )
    except Exception as e:
        logging.error("Error updating wallet:", {str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{wallet_id}", response_model=WalletCreateResponse, summary="Delete Wallet", description="Delete wallet by setting isDeleted flag to true")
async def delete_wallet(wallet_id: str, current_user: dict = Depends(authorization_required)):
    try:
        # Assuming there is a service function to set the isDeleted flag
        wallet = await delete_user_wallet(current_user["sub"], wallet_id)
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        return WalletCreateResponse(
            message="Wallet deleted successfully",
            wallet=WalletListResponse(
                wallet_name=wallet["wallet_name"] if wallet["wallet_name"] else "",
                wallet_address=wallet["wallet_address"],
                seed_phrase=wallet["seed_phrase"],
                created_at=wallet["created_at"].isoformat(),
                updated_at=wallet["updated_at"].isoformat() 
            )
        )
    except Exception as e:
        logging.error("Error deleting wallet:", {str(e)})
        raise HTTPException(status_code=500, detail=str(e))