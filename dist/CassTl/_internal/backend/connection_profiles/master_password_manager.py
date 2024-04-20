import sqlite3
import hashlib
import os
from typing import Any, Tuple, Union
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from constants.common import MASTER_PASSWORD_DB_PATH, MASTER_PASSWORD_TABLE


class MasterPasswordManager:
    def __init__(self: 'MasterPasswordManager') -> None:
        self.__db_path: str = MASTER_PASSWORD_DB_PATH

        # NOTE Will be set after successful authentication.
        self.__salt: bytes = None
        self.__master_password: str = None
        self.__symmetric_key: bytes = None

        self.__create_table()


    # Private

    def __delete_master_password(self: 'MasterPasswordManager') -> None:
        connection = sqlite3.connect(self.__db_path)
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM {MASTER_PASSWORD_TABLE} WHERE user = ?', ("master",))
        connection.commit()
        connection.close()

    def __hash_password(self: 'MasterPasswordManager', password: str, salt: bytes) -> str:
        salted_password = password.encode('utf-8') + salt
        return hashlib.sha256(salted_password).hexdigest()

    def __save_to_db(self: 'MasterPasswordManager', hashed_password: str, salt: bytes) -> None:
        connection = sqlite3.connect(self.__db_path)
        cursor = connection.cursor()
        cursor.execute(f'''
            INSERT INTO {MASTER_PASSWORD_TABLE} (user, hashed_password, salt)
            VALUES (?, ?, ?)
        ''', ("master", hashed_password, salt))
        connection.commit()
        connection.close()

    def __create_table(self: 'MasterPasswordManager') -> None:
        connection = sqlite3.connect(self.__db_path)
        cursor = connection.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {MASTER_PASSWORD_TABLE} (
                user TEXT PRIMARY KEY NOT NULL,
                hashed_password TEXT NOT NULL,
                salt BLOB NOT NULL
            )
        ''')
        connection.commit()
        connection.close()

    def __derive_key_from__master_password(self: 'MasterPasswordManager', iterations: int = 100000, key_length: int = 32) -> None:
        if self.__master_password and self.__salt:
            self.__symmetric_key = hashlib.pbkdf2_hmac('sha256', self.__master_password.encode(), self.__salt, iterations, key_length)

    def __get_master_password(self: 'MasterPasswordManager') -> Tuple[str, bytes]:
        connection = sqlite3.connect(self.__db_path)
        cursor = connection.cursor()
        cursor.execute(f'SELECT hashed_password, salt FROM {MASTER_PASSWORD_TABLE} WHERE user = ?', ("master",))
        result = cursor.fetchone()
        connection.close()
        return result


    # Public

    def is_master_password_created(self: 'MasterPasswordManager') -> bool:
        result = self.__get_master_password()
        return result is not None

    def create_master_password(self: 'MasterPasswordManager', password1: str, password2: str) -> Union[None, Exception]:
        if password1 != password2 or password1 == "":
            raise Exception(f"Passwords doesn't match.")
        salt = os.urandom(32)
        hashed_password = self.__hash_password(password1, salt)
        self.__save_to_db(hashed_password, salt)

    def change_master_password(self: 'MasterPasswordManager',
                               old_password: str,
                               new_password1: str,
                               new_password2: str) -> Union[None, Exception]:
        if self.authenticate(old_password) is not True:
            raise Exception(f"Authentication failed.")
        if new_password1 != new_password2:
            raise Exception(f"Passwords doesn't match.")
        self.__delete_master_password()
        self.create_master_password(new_password1, new_password2)

    def authenticate(self: 'MasterPasswordManager', password: str) -> bool:
        is_authenticated: bool = False

        result = self.__get_master_password()

        if not result:
            return is_authenticated

        stored_encrypted_password, stored_salt = result
        input_encrypted_password = self.__hash_password(password, stored_salt)
        is_authenticated = input_encrypted_password == stored_encrypted_password
        self.__salt = stored_salt if is_authenticated else None
        self.__master_password = password if is_authenticated else None
        self.__derive_key_from__master_password()

        return is_authenticated

    def encrypt_aes_256(self: 'MasterPasswordManager', password: str) -> bytes:
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.__symmetric_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(password.encode()) + padder.finalize()

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        return iv + ciphertext

    def decrypt_aes_256(self: 'MasterPasswordManager', encrypted_password: bytes, symmetric_key: bytes = None) -> str:
        iv = encrypted_password[:16]
        ciphertext = encrypted_password[16:]

        symmetric_key = symmetric_key or self.__symmetric_key
        cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        message = unpadder.update(padded_data) + unpadder.finalize()

        return message.decode()

    @property
    def symmetric_key(self: 'MasterPasswordManager') -> bytes:
        return self.__symmetric_key

    @symmetric_key.setter
    def symmetric_key(self: 'MasterPasswordManager', value: Any) -> Exception:
        raise Exception(f"You can't set value {value} for read-only property symmetric_key.")