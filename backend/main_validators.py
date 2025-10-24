from django.core.exceptions import ValidationError
from .validators import SecurityValidators, ComplianceValidators
from .crypto_validators import CryptoValidators
from .fraud_validators import FraudValidators


class MainValidator:
    """Validador principal que integra todos os validadores do sistema"""
    
    def __init__(self, user=None, request_data=None):
        self.user = user
        self.request_data = request_data or {}
        self.security = SecurityValidators()
        self.compliance = ComplianceValidators()
        self.crypto = CryptoValidators()
        self.fraud = FraudValidators()
    
    def validate_transaction(self, transaction_data):
        """Validação completa de transação"""
        # Validações básicas de segurança
        amount = self.security.validate_amount(transaction_data['amount'])
        description = self.security.validate_description(transaction_data['description'])
        
        # Validações de fraude
        self.fraud.validate_velocity_check(self.user, amount)
        self.fraud.validate_behavioral_pattern(self.user, transaction_data)
        
        # Validações de compliance
        self.compliance.validate_audit_trail(transaction_data, self.user)
        self.compliance.validate_anti_money_laundering(transaction_data, self.user)
        
        # Calcular score de risco
        context = {
            'new_device': self.request_data.get('new_device', False),
            'new_location': self.request_data.get('new_location', False),
            'high_frequency': self.request_data.get('high_frequency', False)
        }
        risk_score = self.fraud.calculate_risk_score(self.user, transaction_data, context)
        
        return {
            'valid': True,
            'amount': amount,
            'description': description,
            'risk_score': risk_score
        }
    
    def validate_account_operation(self, operation_data):
        """Validação de operações em conta"""
        # Validar propriedade
        account = operation_data.get('account')
        self.security.validate_user_ownership(self.user, account)
        
        # Validar saldo se for débito
        if operation_data.get('type') == 'debit':
            self.security.validate_account_balance(
                account, 
                operation_data['amount'], 
                'debit'
            )
        
        # Validar padrão de acesso
        self.security.validate_account_access_pattern(
            self.user, 
            account.id, 
            self.request_data.get('ip')
        )
        
        return True
    
    def validate_sensitive_data(self, data, data_type='general'):
        """Validação de dados sensíveis"""
        # Criptografar dados sensíveis
        if data_type == 'card':
            self.compliance.validate_pci_compliance(data)
            return self.crypto.tokenize_card_number(data.get('number'))
        
        # Hash para outros dados sensíveis
        if data_type in ['cpf', 'document']:
            return self.crypto.hash_sensitive_field(data)
        
        # Criptografia geral
        return self.crypto.encrypt_sensitive_data(data)
    
    def validate_user_session(self, session_data):
        """Validação de sessão do usuário"""
        # Validar dispositivo
        device_fp = session_data.get('device_fingerprint')
        if device_fp:
            self.fraud.validate_device_consistency(self.user, device_fp)
            self.security.validate_device_fingerprint(self.user, device_fp)
        
        # Validar geolocalização
        if 'ip' in session_data:
            self.fraud.validate_geolocation_risk(
                self.user, 
                session_data['ip'], 
                session_data.get('location')
            )
        
        return True
    
    def validate_bulk_operation(self, operations_list, operation_type):
        """Validação de operações em lote"""
        # Validar operação sensível
        self.security.validate_sensitive_operation(self.user, operation_type)
        
        # Validar padrões suspeitos
        if operation_type == 'bulk_transactions':
            self.fraud.validate_transaction_pattern(operations_list)
        
        # Validar cada operação individualmente
        results = []
        for operation in operations_list:
            try:
                if operation_type == 'bulk_transactions':
                    result = self.validate_transaction(operation)
                else:
                    result = self.validate_account_operation(operation)
                results.append(result)
            except ValidationError as e:
                results.append({'valid': False, 'error': str(e)})
        
        return results
    
    def quick_validate(self, data_type, data):
        """Validação rápida para casos simples"""
        validators = {
            'amount': lambda x: self.security.validate_amount(x),
            'description': lambda x: self.security.validate_description(x),
            'date': lambda x: self.security.validate_date_range(x),
            'token': lambda x: self.crypto.validate_token_format(x)
        }
        
        if data_type in validators:
            return validators[data_type](data)
        
        raise ValidationError(f'Tipo de validação {data_type} não suportado')


def validate_transaction_simple(user, amount, description):
    """Função utilitária para validação simples de transação"""
    validator = MainValidator(user)
    return validator.validate_transaction({
        'amount': amount,
        'description': description,
        'type': 'general'
    })


def validate_with_context(user, data, context=None):
    """Função utilitária para validação com contexto"""
    validator = MainValidator(user, context)
    
    if 'amount' in data and 'description' in data:
        return validator.validate_transaction(data)
    elif 'account' in data:
        return validator.validate_account_operation(data)
    else:
        raise ValidationError('Tipo de dados não identificado para validação')