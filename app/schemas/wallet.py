from typing import List
from pydantic import BaseModel, Field

class WalletListResponse(BaseModel):
    wallet_name: str = Field(None, title="Wallet Name", description="The name of the wallet")
    wallet_address: str = Field(..., title="Wallet Address", description="The generated wallet address")
    seed_phrase: str = Field(..., title="Seed Phrase", description="The generated seed phrase", example="encrypted_seed_phrase")
    created_at: str = Field(..., title="Created At", description="The date and time the wallet was created")
    updated_at: str = Field(..., title="Updated At", description="The date and time the wallet was last updated")

    class Config:
        schema_extra = {
            "example": {
                "wallet_name": "My Wallet",
                "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
                "seed_phrase": "U2FsdGVkX1+K4V5fQz8Q9Q==",
                "created_at": "2023-10-01T12:00:00Z",
                "updated_at": "2023-10-01T12:00:00Z"
            }
        }

class WalletList(BaseModel):
    total_count: int = Field(..., title="Total Count", description="The total number of wallets associated with the user")
    wallets: List[WalletListResponse] = Field(..., title="Wallets", description="List of wallets associated with the user")

    class Config:
        schema_extra = {
            "example": {
                "total_count": 100,
                "wallets": [
                    {
                        "wallet_name": "My Wallet",
                        "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
                        "seed_phrase": "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
                        "created_at": "2023-10-01T12:00:00Z",
                        "updated_at": "2023-10-01T12:00:00Z"
                    },
                    {
                        "wallet_name": "My Second Wallet",
                        "wallet_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                        "seed_phrase": "legal winner thank year wave sausage worth useful legal winner thank yellow",
                        "created_at": "2023-10-02T12:00:00Z",
                        "updated_at": "2023-10-02T12:00:00Z"
                    }
                ]
            }
        }

class WalletCreateRequest(BaseModel):
    wallet_name: str = Field(None, title="Wallet Name", description="The name of the wallet")
    
    class Config:
        schema_extra = {
            "example": {
                "wallet_name": "My Wallet"
            }
        }

class WalletCreateResponse(BaseModel):
    message: str = Field(..., title="Message", description="Response message")
    wallet: WalletListResponse = Field(..., title="Wallet", description="The created wallet details")

    class Config:
        schema_extra = {
            "example": {
                "message": "Wallet created successfully",
                "wallet": {
                    "wallet_name": "My Wallet",
                    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
                    "seed_phrase": "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
                    "created_at": "2023-10-01T12:00:00Z",
                    "updated_at": "2023-10-01T12:00:00Z"
                }
            }
        }