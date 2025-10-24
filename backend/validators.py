import re
import hashlib
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone

class SecurityValidators:
    """Validadores de segurança para dados financeiros"""
    
    @staticmethod
    def validate_amount(value):
        """Valida valores monetários"""
        if value is None:
            raise ValidationError('Valor é obrigatório')
        
        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise ValidationError('Valor deve ser um número válido')
        
        if decimal_value <= 0:
            raise ValidationError('Valor deve ser maior que zero')
        
        if decimal_value > Decimal('999999999.99'):
            raise ValidationError('Valor muito alto')
        
        # Verificar número de casas decimais
        if decimal_value.as_tuple().exponent < -2:
            raise ValidationError('Máximo 2 casas decimais')
        
        return decimal_value
    
    @staticmethod
    def validate_description(description):
        """Valida descrições de transações"""
        if not description or not description.strip():
            raise ValidationError('Descrição é obrigatória')
        
        description = description.strip()
        
        if len(description) < 3:
            raise ValidationError('Descrição deve ter pelo menos 3 caracteres')
        
        if len(description) > 200:
            raise ValidationError('Descrição deve ter no máximo 200 caracteres')
        
        # Verificar caracteres suspeitos
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe',
            r'<object',
            r'<embed'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                raise ValidationError('Descrição contém caracteres não permitidos')
        
        return description
    
    @staticmethod
    def validate_user_ownership(user, obj):
        """Valida se o objeto pertence ao usuário"""
        if not user or not user.is_authenticated:
            raise ValidationError('Usuário não autenticado')
        
        if hasattr(obj, 'user') and obj.user != user:
            raise ValidationError('Acesso negado: objeto não pertence ao usuário')
        
        return True
    
    @staticmethod
    def validate_date_range(start_date, end_date=None):
        """Valida intervalos de data"""
        from datetime import date, timedelta
        
        if not start_date:
            raise ValidationError('Data inicial é obrigatória')
        
        # Data não pode ser muito antiga (mais de 10 anos)
        min_date = date.today() - timedelta(days=3650)
        if start_date < min_date:
            raise ValidationError('Data muito antiga')
        
        # Data não pode ser futura (mais de 1 dia)
        max_date = date.today() + timedelta(days=1)
        if start_date > max_date:
            raise ValidationError('Data não pode ser futura')
        
        if end_date:
            if end_date < start_date:
                raise ValidationError('Data final deve ser posterior à inicial')
            
            # Intervalo máximo de 5 anos
            if (end_date - start_date).days > 1825:
                raise ValidationError('Intervalo máximo de 5 anos')
        
        return True
    
    @staticmethod
    def validate_account_balance(account, amount, operation='debit'):
        """Valida operações de saldo"""
        if not account:
            raise ValidationError('Conta é obrigatória')
        
        if operation == 'debit' and not account.can_debit(amount):
            raise ValidationError(f'Saldo insuficiente. Disponível: R$ {account.current_balance}')
        
        return True
    
    @staticmethod
    def validate_credit_limit(credit_card, amount):
        """Valida limite de cartão de crédito"""
        if not credit_card:
            raise ValidationError('Cartão é obrigatório')
        
        if not credit_card.can_charge(amount):
            raise ValidationError(f'Limite insuficiente. Disponível: R$ {credit_card.available_limit}')
        
        return True
    
    @staticmethod
    def sanitize_input(value, max_length=None):
        """Sanitiza entrada de dados"""
        if not isinstance(value, str):
            return value
        
        # Remove caracteres de controle
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        
        # Remove espaços extras
        sanitized = ' '.join(sanitized.split())
        
        # Aplica limite de tamanho
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    

    
    @staticmethod
    def validate_transaction_frequency(user, amount, time_window=300):
        """Valida frequência de transações para detectar atividade suspeita"""
        cache_key = f"tx_freq_{user.id}_{int(timezone.now().timestamp() // time_window)}"
        
        transactions = cache.get(cache_key, [])
        transactions.append({
            'amount': float(amount),
            'timestamp': timezone.now().timestamp()
        })
        
        # Verificar se há muitas transações em pouco tempo
        if len(transactions) > 20:
            raise ValidationError('Muitas transações em pouco tempo')
        
        # Verificar valores suspeitos (muito altos ou padrão repetitivo)
        amounts = [tx['amount'] for tx in transactions]
        if len(amounts) > 5:
            avg_amount = sum(amounts) / len(amounts)
            if amount > avg_amount * 10:
                raise ValidationError('Valor muito acima do padrão usual')
        
        cache.set(cache_key, transactions, time_window)
        return True
    
    @staticmethod
    def validate_account_access_pattern(user, account_id, request_ip=None):
        """Valida padrões de acesso a contas"""
        cache_key = f"acc_access_{user.id}_{account_id}"
        access_data = cache.get(cache_key, {'ips': [], 'count': 0})
        
        if request_ip:
            if request_ip not in access_data['ips']:
                access_data['ips'].append(request_ip)
                # Máximo 3 IPs diferentes por hora
                if len(access_data['ips']) > 3:
                    raise ValidationError('Acesso de muitos IPs diferentes detectado')
        
        access_data['count'] += 1
        # Máximo 100 acessos por hora por conta
        if access_data['count'] > 100:
            raise ValidationError('Muitos acessos à conta em pouco tempo')
        
        cache.set(cache_key, access_data, 3600)  # 1 hora
        return True
    
    @staticmethod
    def validate_sensitive_operation(user, operation_type, additional_data=None):
        """Valida operações sensíveis (transferências, alterações de limite)"""
        sensitive_ops = ['transfer', 'limit_change', 'account_delete', 'bulk_import']
        
        if operation_type not in sensitive_ops:
            return True
        
        # Verificar se o usuário fez login recentemente (últimas 2 horas)
        if hasattr(user, 'last_login') and user.last_login:
            time_since_login = timezone.now() - user.last_login
            if time_since_login > timedelta(hours=2):
                raise ValidationError('Operação sensível requer login recente')
        
        # Rate limiting para operações sensíveis
        cache_key = f"sensitive_ops_{user.id}_{operation_type}"
        ops_count = cache.get(cache_key, 0)
        
        limits = {
            'transfer': 10,
            'limit_change': 3,
            'account_delete': 1,
            'bulk_import': 2
        }
        
        if ops_count >= limits.get(operation_type, 5):
            raise ValidationError(f'Limite de operações {operation_type} excedido hoje')
        
        cache.set(cache_key, ops_count + 1, 86400)  # 24 horas
        return True
    
    @staticmethod
    def validate_data_integrity(data_hash, expected_hash=None):
        """Valida integridade de dados críticos"""
        if expected_hash and data_hash != expected_hash:
            raise ValidationError('Dados foram alterados durante o processamento')
        return True
    
    @staticmethod
    def generate_data_hash(data):
        """Gera hash para validação de integridade"""
        if isinstance(data, dict):
            data_str = str(sorted(data.items()))
        else:
            data_str = str(data)
        
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    @staticmethod
    def validate_business_rules(transaction_data):
        """Valida regras de negócio específicas"""
        amount = transaction_data.get('amount', 0)
        category = transaction_data.get('category', '')
        transaction_type = transaction_data.get('type', '')
        
        # Regras por categoria
        category_limits = {
            'investimento': Decimal('50000.00'),
            'transferencia': Decimal('10000.00'),
            'saque': Decimal('5000.00')
        }
        
        if category.lower() in category_limits:
            if amount > category_limits[category.lower()]:
                raise ValidationError(f'Valor excede limite para categoria {category}')
        
        # Validar horário para certas operações
        if transaction_type == 'transfer':
            current_hour = timezone.now().hour
            if current_hour < 6 or current_hour > 22:
                raise ValidationError('Transferências só são permitidas entre 6h e 22h')
        
        return True
    
    @staticmethod
    def validate_device_fingerprint(user, device_info):
        """Valida fingerprint do dispositivo para detectar acessos suspeitos"""
        if not device_info:
            return True
        
        cache_key = f"device_fp_{user.id}"
        known_devices = cache.get(cache_key, [])
        
        device_hash = hashlib.md5(str(device_info).encode()).hexdigest()
        
        if device_hash not in known_devices:
            known_devices.append(device_hash)
            # Máximo 5 dispositivos conhecidos
            if len(known_devices) > 5:
                known_devices = known_devices[-5:]
            
            cache.set(cache_key, known_devices, 86400 * 30)  # 30 dias
            
            # Log para novo dispositivo
            import logging
            logger = logging.getLogger('security')
            logger.warning(f'Novo dispositivo detectado para usuário {user.id}')
        
        return True


class ComplianceValidators:
    """Validadores para conformidade regulatória e auditoria"""
    
    @staticmethod
    def validate_pci_compliance(card_data):
        """Valida conformidade PCI para dados de cartão"""
        if not card_data:
            return True
        
        # Nunca armazenar dados sensíveis do cartão
        forbidden_fields = ['cvv', 'security_code', 'full_number']
        for field in forbidden_fields:
            if field in card_data:
                raise ValidationError(f'Campo {field} não pode ser armazenado')
        
        # Validar formato do número mascarado
        if 'masked_number' in card_data:
            masked = card_data['masked_number']
            if not re.match(r'\*{4,12}\d{4}', masked):
                raise ValidationError('Formato de número mascarado inválido')
        
        return True
    
    @staticmethod
    def validate_audit_trail(operation_data, user):
        """Valida e registra trilha de auditoria"""
        required_fields = ['operation_type', 'timestamp', 'amount']
        
        for field in required_fields:
            if field not in operation_data:
                raise ValidationError(f'Campo {field} obrigatório para auditoria')
        
        # Registrar na trilha de auditoria
        audit_data = {
            'user_id': user.id,
            'operation': operation_data['operation_type'],
            'amount': operation_data.get('amount'),
            'timestamp': timezone.now(),
            'ip_address': operation_data.get('ip_address'),
            'user_agent': operation_data.get('user_agent', '')[:200]
        }
        
        # Aqui seria salvo no sistema de auditoria
        import logging
        audit_logger = logging.getLogger('audit')
        audit_logger.info(f'Financial operation: {audit_data}')
        
        return True
    
    @staticmethod
    def validate_data_retention(data_type, creation_date):
        """Valida políticas de retenção de dados"""
        retention_policies = {
            'transaction': 2555,  # 7 anos em dias
            'audit_log': 2555,
            'user_session': 90,
            'temporary_data': 30
        }
        
        if data_type not in retention_policies:
            return True
        
        retention_days = retention_policies[data_type]
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        if creation_date < cutoff_date:
            raise ValidationError(f'Dados de {data_type} expirados pela política de retenção')
        
        return True
    
    @staticmethod
    def validate_gdpr_compliance(user_data, consent_data):
        """Valida conformidade com LGPD/GDPR"""
        sensitive_fields = ['cpf', 'rg', 'phone', 'address', 'birth_date']
        
        for field in sensitive_fields:
            if field in user_data and not consent_data.get(f'consent_{field}'):
                raise ValidationError(f'Consentimento necessário para processar {field}')
        
        # Verificar se o consentimento não expirou
        if 'consent_date' in consent_data:
            consent_date = consent_data['consent_date']
            if isinstance(consent_date, str):
                consent_date = datetime.fromisoformat(consent_date)
            
            # Consentimento válido por 2 anos
            if timezone.now() - consent_date > timedelta(days=730):
                raise ValidationError('Consentimento expirado, renovação necessária')
        
        return True
    
    @staticmethod
    def validate_anti_money_laundering(transaction_data, user):
        """Valida regras anti-lavagem de dinheiro"""
        amount = transaction_data.get('amount', 0)
        transaction_type = transaction_data.get('type', '')
        
        # Limite para reportar transações suspeitas
        suspicious_threshold = Decimal('10000.00')
        
        if amount >= suspicious_threshold:
            # Verificar padrões suspeitos
            cache_key = f'aml_pattern_{user.id}'
            recent_transactions = cache.get(cache_key, [])
            
            # Adicionar transação atual
            recent_transactions.append({
                'amount': float(amount),
                'type': transaction_type,
                'timestamp': timezone.now().timestamp()
            })
            
            # Manter apenas últimas 24 horas
            cutoff = timezone.now().timestamp() - 86400
            recent_transactions = [
                tx for tx in recent_transactions 
                if tx['timestamp'] > cutoff
            ]
            
            # Verificar padrões suspeitos
            total_24h = sum(tx['amount'] for tx in recent_transactions)
            if total_24h > 50000:  # R$ 50.000 em 24h
                import logging
                aml_logger = logging.getLogger('aml')
                aml_logger.warning(
                    f'Suspicious activity detected: User {user.id}, '
                    f'Total 24h: R$ {total_24h}'
                )
            
            cache.set(cache_key, recent_transactions, 86400)
        
        return True