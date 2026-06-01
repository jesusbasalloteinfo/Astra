"""
ASTRA - Automated Smart Telescope Remote Assistant
Copyright (C) 2026 Jesus Basallote

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import jwt
from typing import Optional
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from core.logging_utils import get_logger
from models.auth import JWTPayload


LOG = get_logger("AUTH-KEYS")

KEYS_DIR = os.getenv("KEYS_DIR", "keys")
PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, "private_key.pem")
PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, "public_key.pem")

ALGORITHM = "RS256"

def generate_keys_if_not_exists():
    """Generates RS256 keypair if they don't exist.
    
    This function checks if the keys directory and the private/public key files
    exist. If they don't, it generates a new 2048-bit RSA keypair and saves
    them in PEM format.
    """
    
    if not os.path.exists(KEYS_DIR):
        os.makedirs(KEYS_DIR)

    if os.path.exists(PRIVATE_KEY_PATH) and os.path.exists(PUBLIC_KEY_PATH):
        LOG.info("RS256 Keys already exist. Skipping generation.")
        return

    LOG.info("Generating new RS256 Keypair...")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Serialize private key
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Generate public key
    public_key = private_key.public_key()
    
    # Serialize public key
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Save to files
    with open(PRIVATE_KEY_PATH, 'wb') as f:
        f.write(pem_private)
    
    with open(PUBLIC_KEY_PATH, 'wb') as f:
        f.write(pem_public)

    LOG.info(f"Keys generated successfully in {KEYS_DIR}/")

def get_private_key() -> bytes:
    """Read the RS256 private key from the file system.

    Returns:
        bytes: The content of the private key file.
    """
    with open(PRIVATE_KEY_PATH, 'rb') as f:
        return f.read()

def get_public_key() -> bytes:
    """Read the RS256 public key from the file system.

    Returns:
        bytes: The content of the public key file.
    """
    with open(PUBLIC_KEY_PATH, 'rb') as f:
        return f.read()

def create_access_token(username: str, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed RS256 JWT using JWTPayload model.

    Args:
        username (str): The subject (username) of the token.
        email (str): The email address of the user.
        expires_delta (Optional[timedelta]): Optional expiration time. Defaults to 7 days.

    Returns:
        str: The encoded JWT string.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)

    payload = JWTPayload(
        sub=username,
        email=email,
        iat=datetime.now(timezone.utc),
        exp=expire
    )

    private_key = get_private_key()
    encoded_jwt = jwt.encode(payload.model_dump(), private_key, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> JWTPayload:
    """Decode and validate a JWT returning a JWTPayload object.

    Args:
        token (str): The JWT string to decode.

    Returns:
        JWTPayload: The decoded payload as a Pydantic model.

    Raises:
        jwt.PyJWTError: If the token is invalid or expired.
    """
    public_key = get_public_key()
    decoded = jwt.decode(token, public_key, algorithms=[ALGORITHM])
    return JWTPayload(**decoded)

