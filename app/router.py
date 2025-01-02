from fastapi import APIRouter
from app.controllers.users import users
from app.controllers.wallet import wallet

router = APIRouter()
router.include_router(users.router)
router.include_router(wallet.router)