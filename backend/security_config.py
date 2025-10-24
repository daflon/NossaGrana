"""
Configurações de segurança para validadores financeiros
"""

# Limites de transações
TRANSACTION_LIMITS = {
    'daily_amount': 50000.00,
    'hourly_amount': 20000.00,
    'daily_count': 200,
    'hourly_count': 50,
    'single_transaction': 10000.00
}

# Configurações de rate limiting
RATE_LIMITING = {
    'financial_operations': {
        'window': 300,  # 5 minutos
        'max_requests': 100
    },
    'sensitive_operations': {
        'transfer': {'daily': 10, 'hourly': 3},
        'limit_change': {'daily': 3, 'hourly': 1},
        'account_delete': {'daily': 1, 'hourly': 1},
        'bulk_import': {'daily': 2, 'hourly': 1}
    }
}

# Configurações de detecção de fraude
FRAUD_DETECTION = {
    'velocity_check': {
        'time_window': 3600,  # 1 hora
        'max_amount': 20000.00,
        'max_count': 50
    },
    'behavioral_analysis': {
        'amount_multiplier_threshold': 5,  # 5x a média usual
        'min_transactions_for_analysis': 10
    },
    'risk_scoring': {
        'thresholds': {
            'low': 30,
            'medium': 60,
            'high': 80
        },
        'factors': {
            'high_amount': 20,
            'unusual_time': 15,
            'new_device': 25,
            'new_location': 30,
            'high_frequency': 20
        }
    }
}

# Configurações de conformidade
COMPLIANCE = {
    'data_retention': {
        'transaction': 2555,  # 7 anos
        'audit_log': 2555,
        'user_session': 90,
        'temporary_data': 30
    },
    'pci_compliance': {
        'forbidden_fields': ['cvv', 'security_code', 'full_number'],
        'required_masking': True
    },
    'gdpr_lgpd': {
        'consent_validity_days': 730,  # 2 anos
        'sensitive_fields': ['cpf', 'rg', 'phone', 'address', 'birth_date']
    }
}

# Configurações de criptografia
ENCRYPTION = {
    'algorithm': 'Fernet',
    'key_rotation_days': 90,
    'hash_iterations': 100000,
    'token_length': 32
}

# Configurações de auditoria
AUDIT = {
    'log_all_financial_operations': True,
    'log_failed_validations': True,
    'log_suspicious_activities': True,
    'retention_days': 2555  # 7 anos
}

# Padrões suspeitos para detecção
SUSPICIOUS_PATTERNS = {
    'sql_injection': [
        'union select', 'drop table', 'delete from',
        'insert into', 'update set', '--', ';'
    ],
    'xss_patterns': [
        '<script', 'javascript:', 'eval(',
        'on\\w+\\s*=', '<iframe', '<object', '<embed'
    ],
    'path_traversal': [
        '../', '..\\\\', '..\\', '..\\'
    ]
}

# Configurações de validação de dados
DATA_VALIDATION = {
    'amount': {
        'min_value': 0.01,
        'max_value': 999999999.99,
        'decimal_places': 2
    },
    'description': {
        'min_length': 3,
        'max_length': 200,
        'required': True
    },
    'bulk_operations': {
        'max_items': 100
    }
}

# Configurações de sessão e autenticação
SESSION_SECURITY = {
    'max_concurrent_sessions': 3,
    'session_timeout_minutes': 120,
    'require_recent_login_for_sensitive_ops': True,
    'recent_login_threshold_hours': 2
}

# Configurações de monitoramento
MONITORING = {
    'alert_thresholds': {
        'failed_validations_per_hour': 50,
        'suspicious_activities_per_hour': 10,
        'high_risk_transactions_per_hour': 5
    },
    'notification_channels': ['email', 'log', 'webhook']
}