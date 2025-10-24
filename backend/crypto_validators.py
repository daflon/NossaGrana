import hashlib
import secrets
import base64
from cryptography.fernet import Fernet
from django.core.exceptions import ValidationError
from django.conf import settings


class CryptoValidators:
    """Validadores para criptografia e tokenização de dados sensíveis"""
    
    @staticmethod
    def generate_token():
        """Gera token seguro para operações sensíveis"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_token_format(token):
        """Valida formato do token"""
        if not token or len(token) < 32:
            raise ValidationError('Token inválido')
        
        try:
            base64.urlsafe_b64decode(token + '==')
        except Exception:
            raise ValidationError('Formato de token inválido')
        
        return True
    
    @staticmethod
    def encrypt_sensitive_data(data, key=None):
        """Criptografa dados sensíveis"""
        if not key:
            key = getattr(settings, 'ENCRYPTION_KEY', Fernet.generate_key())
        
        f = Fernet(key)
        encrypted_data = f.encrypt(str(data).encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data, key=None):
        """Descriptografa dados sensíveis"""
        if not key:
            key = getattr(settings, 'ENCRYPTION_KEY', None)
            if not key:
                raise ValidationError('Chave de criptografia não configurada')
        
        try:
            f = Fernet(key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = f.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception:
            raise ValidationError('Erro ao descriptografar dados')
    
    @staticmethod
    def hash_sensitive_field(value, salt=None):
        """Gera hash seguro para campos sensíveis"""
        if not salt:
            salt = secrets.token_hex(16)
        
        hash_obj = hashlib.pbkdf2_hmac('sha256', 
                                      str(value).encode(), 
                                      salt.encode(), 
                                      100000)
        return f"{salt}:{hash_obj.hex()}"
    
    @staticmethod
    def verify_hash(value, hashed_value):
        """Verifica hash de campo sensível"""
        try:
            salt, hash_hex = hashed_value.split(':')
            hash_obj = hashlib.pbkdf2_hmac('sha256',
                                          str(value).encode(),
                                          salt.encode(),
                                          100000)
            return hash_obj.hex() == hash_hex
        except Exception:
            return False
    
    @staticmethod
    def tokenize_card_number(card_number):
        """Tokeniza número de cartão"""
        if not card_number or len(card_number) < 13:
            raise ValidationError('Número de cartão inválido')
        
        # Manter apenas últimos 4 dígitos
        last_four = card_number[-4:]
        token = CryptoValidators.generate_token()
        
        return {
            'token': token,
            'masked_number': f"****-****-****-{last_four}",
            'last_four': last_four
        }
    
    @staticmethod
    def validate_encryption_strength(data):
        """Valida força da criptografia"""
        if len(data) < 32:
            raise ValidationError('Dados criptografados muito curtos')
        
        # Verificar entropia mínima
        entropy = len(set(data)) / len(data)
        if entropy < 0.5:
            raise ValidationError('Baixa entropia nos dados criptografados')
        
        return True