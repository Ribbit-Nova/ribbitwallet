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
    logging.info('HD wallet features enabled')

    # Generate a 12-word mnemonic phrase
    mnemo = Mnemonic('english')
    mnemonic_phrase = mnemo.generate(strength=128)  # 128 bits of entropy for 12 words
    logging.info('Generated mnemonic phrase')
    
    # Derive a wallet address from the mnemonic phrase
    account = Account.from_mnemonic(mnemonic_phrase)
    logging.info('Derived account from mnemonic phrase')
    
    address = account.address
    logging.info('Derived address from account')

    # Derive the private key
    seed = mnemo.to_seed(mnemonic_phrase)
    private_key = account.key.hex()
    logging.info('Derived private from seed_phrase')
    return address, encrypt_key(mnemonic_phrase), encrypt_key(private_key)

def get_wallet_address_from_seed_phrase(seed_phrase: str) -> str:
    Account.enable_unaudited_hdwallet_features()
    mnemonic_phrase = decrypt_key(seed_phrase)
    account = Account.from_mnemonic(mnemonic_phrase)
    wallet_address = account.address
    logging.info('Derived wallet address from seed_phrase')
    
    private_key = account.key.hex()
    logging.info('Derived private from seed_phrase')
    return wallet_address, encrypt_key(private_key)

def get_wallet_address_from_private_key(private_key: str) -> str:
    decrypted_private_key = decrypt_key(private_key)
    Account.enable_unaudited_hdwallet_features()
    account = Account.from_key(decrypted_private_key)
    wallet_address = account.address
    logging.info('Derived wallet address from private_key.')
    return wallet_address, private_key

def encrypt_key(seed_phrase: str) -> str:
    SECRET_KEY = os.getenv('SECRET_KEY').encode()
    aesgcm = AESGCM(SECRET_KEY)
    iv = os.urandom(12)  # GCM recommended IV size is 12 bytes
    ciphertext = aesgcm.encrypt(iv, seed_phrase.encode(), None)
    encrypted_data = {
        'ciphertext': b64encode(ciphertext).decode(),
        'iv': b64encode(iv).decode(),
    }
    encrypted_string = b64encode(str(encrypted_data).encode()).decode()
    logging.info('Encrypted key successfully.')
    return encrypted_string

def decrypt_key(encrypted_string: str) -> str:
    SECRET_KEY = os.getenv('SECRET_KEY').encode()
    aesgcm = AESGCM(SECRET_KEY)
    encrypted_data = eval(b64decode(encrypted_string).decode())
    iv = b64decode(encrypted_data['iv'])
    ciphertext = b64decode(encrypted_data['ciphertext'])
    plaintext = aesgcm.decrypt(iv, ciphertext, None)
    logging.info('Decrypted key successfully.')
    return plaintext.decode()