"""
Encryption utilities for sensitive data (resume storage).
"""

import os
import base64
from typing import Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import hashlib
import logging

logger = logging.getLogger(__name__)


class DataEncryption:
    """Handle encryption and decryption of sensitive data."""

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption handler.

        Args:
            encryption_key: Encryption key (if None, uses environment variable)
        """
        if encryption_key:
            self.key = encryption_key.encode()
        else:
            self.key = self._get_or_generate_key()

        # Derive Fernet key from provided key
        self.fernet = self._create_fernet(self.key)

    def _get_or_generate_key(self) -> bytes:
        """Get encryption key from environment or generate new one."""
        key = os.getenv("ENCRYPTION_KEY")

        if not key:
            # Generate a new key (should be saved to environment in production)
            key = Fernet.generate_key().decode()
            logger.warning(
                "No ENCRYPTION_KEY found in environment. "
                f"Generated new key. Save this key securely: {key}"
            )

        return key.encode()

    def _create_fernet(self, key: bytes) -> Fernet:
        """
        Create Fernet instance with derived key.

        Args:
            key: Base key

        Returns:
            Fernet instance
        """
        # Derive a proper Fernet key using PBKDF2
        salt = b"cf_copilot_salt"  # In production, use random salt per user

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )

        derived_key = base64.urlsafe_b64encode(kdf.derive(key))

        return Fernet(derived_key)

    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        Encrypt data.

        Args:
            data: Data to encrypt (string or bytes)

        Returns:
            Base64-encoded encrypted data
        """
        if isinstance(data, str):
            data = data.encode()

        encrypted = self.fernet.encrypt(data)

        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data.

        Args:
            encrypted_data: Base64-encoded encrypted data

        Returns:
            Decrypted data as string
        """
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.fernet.decrypt(encrypted_bytes)

        return decrypted.decode()

    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Encrypt a file.

        Args:
            file_path: Path to file to encrypt
            output_path: Path for encrypted file (if None, appends .encrypted)

        Returns:
            Path to encrypted file
        """
        if output_path is None:
            output_path = f"{file_path}.encrypted"

        # Read file
        with open(file_path, 'rb') as f:
            data = f.read()

        # Encrypt
        encrypted = self.fernet.encrypt(data)

        # Write encrypted file
        with open(output_path, 'wb') as f:
            f.write(encrypted)

        logger.info(f"Encrypted file saved to: {output_path}")

        return output_path

    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file.

        Args:
            encrypted_file_path: Path to encrypted file
            output_path: Path for decrypted file

        Returns:
            Path to decrypted file
        """
        if output_path is None:
            output_path = encrypted_file_path.replace('.encrypted', '')

        # Read encrypted file
        with open(encrypted_file_path, 'rb') as f:
            encrypted_data = f.read()

        # Decrypt
        decrypted = self.fernet.decrypt(encrypted_data)

        # Write decrypted file
        with open(output_path, 'wb') as f:
            f.write(decrypted)

        logger.info(f"Decrypted file saved to: {output_path}")

        return output_path


class SecureResumeStorage:
    """Secure storage for resume files."""

    def __init__(self, storage_dir: str = "./secure_storage"):
        """
        Initialize secure resume storage.

        Args:
            storage_dir: Directory for encrypted resume storage
        """
        self.storage_dir = storage_dir
        self.encryption = DataEncryption()

        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)

    def store_resume(self, user_id: str, resume_data: bytes) -> str:
        """
        Store resume securely (encrypted).

        Args:
            user_id: User ID
            resume_data: Resume file data (bytes)

        Returns:
            Storage path/ID
        """
        # Generate file hash for integrity checking
        file_hash = hashlib.sha256(resume_data).hexdigest()

        # Encrypt data
        encrypted_data = self.encryption.fernet.encrypt(resume_data)

        # Save to file
        file_name = f"{user_id}_{file_hash[:16]}.enc"
        file_path = os.path.join(self.storage_dir, file_name)

        with open(file_path, 'wb') as f:
            f.write(encrypted_data)

        logger.info(f"Resume stored securely for user {user_id}")

        return file_name

    def retrieve_resume(self, storage_id: str) -> bytes:
        """
        Retrieve and decrypt resume.

        Args:
            storage_id: Storage path/ID

        Returns:
            Decrypted resume data
        """
        file_path = os.path.join(self.storage_dir, storage_id)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume not found: {storage_id}")

        # Read encrypted data
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()

        # Decrypt
        decrypted_data = self.encryption.fernet.decrypt(encrypted_data)

        logger.info(f"Resume retrieved: {storage_id}")

        return decrypted_data

    def delete_resume(self, storage_id: str):
        """
        Delete stored resume.

        Args:
            storage_id: Storage path/ID
        """
        file_path = os.path.join(self.storage_dir, storage_id)

        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Resume deleted: {storage_id}")
        else:
            logger.warning(f"Resume not found for deletion: {storage_id}")


def hash_sensitive_data(data: str, salt: Optional[str] = None) -> str:
    """
    Hash sensitive data (one-way).

    Args:
        data: Data to hash
        salt: Optional salt

    Returns:
        Hashed data (hex)
    """
    if salt:
        data = f"{data}{salt}"

    return hashlib.sha256(data.encode()).hexdigest()


def mask_email(email: str) -> str:
    """
    Mask email for display.

    Args:
        email: Email address

    Returns:
        Masked email (e.g., j***@example.com)
    """
    if '@' not in email:
        return email

    username, domain = email.split('@')

    if len(username) <= 2:
        masked_username = username[0] + '*'
    else:
        masked_username = username[0] + '*' * (len(username) - 2) + username[-1]

    return f"{masked_username}@{domain}"


def mask_phone(phone: str) -> str:
    """
    Mask phone number for display.

    Args:
        phone: Phone number

    Returns:
        Masked phone (e.g., ***-***-1234)
    """
    # Extract digits
    digits = ''.join(c for c in phone if c.isdigit())

    if len(digits) < 4:
        return '*' * len(digits)

    return f"***-***-{digits[-4:]}"
