import logging
from eth_account import Account
from mnemonic import Mnemonic
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from base64 import b64encode, b64decode
import os
from dotenv import load_dotenv

load_dotenv()

def generate_seed_wallet_address():
    # Enable mnemonic features
    Account.enable_unaudited_hdwallet_features()
    logging.info("HD wallet features enabled")

    # Generate a 12-word mnemonic phrase
    mnemo = Mnemonic("english")
    logging.info("Mnemonic instance created")
    
    mnemonic_phrase = mnemo.generate(strength=128)  # 128 bits of entropy for 12 words
    logging.info(f"Generated mnemonic phrase: {mnemonic_phrase}")
    
    # Derive a wallet address from the mnemonic phrase
    account = Account.from_mnemonic(mnemonic_phrase)
    logging.info(f"Derived account: {account}")
    
    address = account.address
    logging.info(f"Derived address: {address}")
    
    return address, encrypt_seed_phrase(mnemonic_phrase)

def get_wallet_address_from_seed_phrase(seed_phrase: str) -> str:
    Account.enable_unaudited_hdwallet_features()
    account = Account.from_mnemonic(decrypt_seed_phrase(seed_phrase))
    wallet_address = account.address
    return wallet_address

def encrypt_seed_phrase(seed_phrase: str) -> dict:
    SECRET_KEY = os.getenv("SECRET_KEY").encode()
    aesgcm = AESGCM(SECRET_KEY)
    iv = os.urandom(12)  # GCM recommended IV size is 12 bytes
    ciphertext = aesgcm.encrypt(iv, seed_phrase.encode(), None)
    encrypted_data = {
        "ciphertext": b64encode(ciphertext).decode(),
        "iv": b64encode(iv).decode(),
    }
    encrypted_string = b64encode(str(encrypted_data).encode()).decode()
    return encrypted_string

def decrypt_seed_phrase(encrypted_string: str) -> str:
    SECRET_KEY = os.getenv("SECRET_KEY").encode()
    aesgcm = AESGCM(SECRET_KEY)
    encrypted_data = eval(b64decode(encrypted_string).decode())
    iv = b64decode(encrypted_data["iv"])
    ciphertext = b64decode(encrypted_data["ciphertext"])
    plaintext = aesgcm.decrypt(iv, ciphertext, None)
    return plaintext.decode()