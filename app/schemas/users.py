from typing import Union, List, Annotated
from fastapi import Body
from pydantic import BaseModel, EmailStr, Field, constr, PrivateAttr, root_validator
from datetime import datetime
from enum import Enum
from app.schemas.wallet import WalletListResponse

class UserType(str, Enum):
    admin = 'admin'
    user = 'user'

# Signup method details
class SignUpMethod(str, Enum):
    social = 'social'
    wallet = 'wallet'
    seed_import = 'seed_import'
    private_key_import = 'private_key_import'

# Social signup details
class SocialPlatform(str, Enum):
    apple = 'apple'
    gmail = 'gmail'
    twitter = 'twitter'

class CommonSignUpRequest(BaseModel):
    signup_method: SignUpMethod = Field(..., title='Signup Method', description='The method used for signing up')
    # Phone login details
    phone_login_enabled: bool = Field(None, title='Phone Login Enabled', description='Indicates if phone-based login is enabled')
    phone_unique_id: constr(max_length=100) = Field(None, title='Phone Unique ID', description='The unique identifier for the user phone')
    # Private attributes
    _user_type: UserType = PrivateAttr()
    _created_at: datetime = PrivateAttr(default_factory=datetime.now)
    _updated_at: datetime = PrivateAttr(default_factory=datetime.now)

class SocialSignUpRequest(CommonSignUpRequest):
    first_name: constr(min_length=1, max_length=50) = Field(None, title='First Name', description='The first name of the user')
    last_name: constr(min_length=1, max_length=50) = Field(None, title='Last Name', description='The last name of the user')
    email_address: EmailStr = Field(None, title='Email Address', description='The users email address')
    social_platform: SocialPlatform = Field(..., title='Social Platform', description='The social platform used for signing up')
    social_id: str = Field(..., title='Social ID', description='The users unique identifier on the social platform')

    @root_validator
    def validate_social_signup(cls, values):
        signup_method = values.get('signup_method')
        social_platform = values.get('social_platform')
        social_id = values.get('social_id')

        if signup_method == SignUpMethod.social:
            if not social_platform:
                raise ValueError('social_platform is required when signup_method is social')
            if not social_id:
                raise ValueError('social_id is required when signup_method is social')

        return values

class WalletSignUpRequest(CommonSignUpRequest):
    wallet_name: constr(min_length=1, max_length=50) = Field(None, title='Wallet Name', description='The name of the wallet')

class SeedImportSignUpRequest(CommonSignUpRequest):
    seed_phrase: str = Field(..., title='Seed Phrase', description='The seed phrase of the wallet to import')

    @root_validator
    def validate_seed_phrase(cls, values):
        signup_method = values.get('signup_method')
        seed_phrase = values.get('seed_phrase')

        if signup_method != SignUpMethod.seed_import:
            raise ValueError('signup_method must be seed_import for SeedImportSignUpRequest')
        if not seed_phrase:
            raise ValueError('seed_phrase is required when signup_method is seed_import')

        return values

class PrivateKeyImportSignUpRequest(CommonSignUpRequest):
    private_key: str = Field(..., title='Private Key', description='The private key of the wallet to import')

    @root_validator
    def validate_private_key(cls, values):
        signup_method = values.get('signup_method')
        private_key = values.get('private_key')

        if signup_method != SignUpMethod.private_key_import:
            raise ValueError('signup_method must be private_key_import for PrivateKeyImportSignUpRequest')
        if not private_key:
            raise ValueError('private_key is required when signup_method is private_key_import')

        return values

SignUpRequest = Union[SocialSignUpRequest, WalletSignUpRequest, SeedImportSignUpRequest, PrivateKeyImportSignUpRequest]

class SignUpTokenResponse(BaseModel):
    access_token: str = Field(..., title='Access Token', description='The access token for authentication')
    token_type: str = Field(..., title='Token Type', description='The type of the token')
    wallets: List[WalletListResponse] = Field(None, title='Wallets', description='List of wallets associated with the user')

    class Config:
        schema_extra = {
            'example': {
                'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                'token_type': 'bearer',
                'wallets': [{
                    'wallet_address': '0x1234567890abcdef1234567890abcdef12345678',
                    'seed_phrase': 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about',
                    'private_key': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1',
                    'created_at': '2023-10-01T12:00:00Z',
                    'updated_at': '2023-10-01T12:00:00Z'
                }]
            }
        }

class UpdateUserRequest(BaseModel):
    first_name: constr(min_length=1, max_length=50) = Field(None, title='First Name', description='The first name of the user')
    last_name: constr(min_length=1, max_length=50) = Field(None, title='Last Name', description='The last name of the user')
    email_address: EmailStr = Field(None, title='Email Address', description='The users email address')
    biography: constr(max_length=160) = Field(None, title='Biography', description='A brief biography of the user')
    personal_website: constr(max_length=100) = Field(None, title='Personal Website', description='The users personal or professional website')
    twitter_handle: constr(max_length=50) = Field(None, title='Twitter Handle', description='The users Twitter username')
    reddit_handle: constr(max_length=20) = Field(None, title='Reddit Handle', description='The users Reddit username')
    github_username: constr(max_length=39) = Field(None, title='GitHub Username', description='The users GitHub username')
    phone_login_enabled: bool = Field(None, title='Phone Login Enabled', description='Indicates if phone-based login is enabled')
    phone_unique_id: constr(max_length=100) = Field(None, title='Phone Unique ID', description='The unique identifier for the users phone')

    @root_validator
    def check_required_fields(cls, values):
        password = values.get('password')
        confirm_password = values.get('confirm_password')
        social_platform = values.get('social_platform')
        social_id = values.get('social_id')
        phone_login_enabled = values.get('phone_login_enabled')
        phone_unique_id = values.get('phone_unique_id')

        if password and not confirm_password:
            raise ValueError('confirm_password is required when password is provided')
        if social_platform and not social_id:
            raise ValueError('social_id is required when social_platform is provided')
        if phone_login_enabled and not phone_unique_id:
            raise ValueError('phone_unique_id is required when phone_login_enabled is True')

        return values

    class Config:
        schema_extra = {
            'example': {
                'first_name': 'John',
                'last_name': 'Doe',
                'email_address': 'john.doe@example.com',
                'biography': 'A brief biography of John Doe.',
                'personal_website': 'https://johndoe.com',
                'twitter_handle': 'johndoe',
                'reddit_handle': 'johndoe123',
                'github_username': 'johndoe',
                'signup_method': 'wallet',
                'social_platform': 'gmail',
                'social_id': 'john.doe@gmail.com',
                'phone_login_enabled': True,
                'phone_unique_id': 'unique-phone-id'
            }
        }
        json_encoders = {
            UserType: lambda v: v.value
        }
        allow_population_by_field_name = True
        exclude = {'userType', 'createdAt', 'modifiedAt'}

class UpdateUserResponse(BaseModel):
        access_token: str = Field(..., title='Access Token', description='The access token for authentication')
        token_type: str = Field(..., title='Token Type', description='The type of the token')

        class Config:
            schema_extra = {
                'example': {
                    'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                    'token_type': 'bearer'
                }
            }

class UserDetailsResponse(BaseModel):
    userid: str = Field(..., title='User ID', description='The unique identifier for the user')
    first_name: constr(min_length=1, max_length=50) = Field(None, title='First Name', description='The first name of the user')
    last_name: constr(min_length=1, max_length=50) = Field(None, title='Last Name', description='The last name of the user')
    email_address: EmailStr = Field(None, title='Email Address', description='The users email address')
    biography: constr(max_length=160) = Field(None, title='Biography', description='A brief biography of the user')
    personal_website: constr(max_length=100) = Field(None, title='Personal Website', description='The users personal or professional website')
    twitter_handle: constr(max_length=50) = Field(None, title='Twitter Handle', description='The users Twitter username')
    reddit_handle: constr(max_length=20) = Field(None, title='Reddit Handle', description='The users Reddit username')
    github_username: constr(max_length=39) = Field(None, title='GitHub Username', description='The users GitHub username')
    phone_login_enabled: bool = Field(None, title='Phone Login Enabled', description='Indicates if phone-based login is enabled')
    social_platform: SocialPlatform = Field(None, title='Social Platform', description='The social platform used for signing up')
    signup_method: SignUpMethod = Field(None, title='Signup Method', description='The method used for signing up')
    user_type: UserType = Field(None, title='User Type', description='The type of user')
    created_at: datetime = Field(None, title='Created At', description='The date and time the user was created')
    updated_at: datetime = Field(None, title='Updated At', description='The date and time the user was last updated')