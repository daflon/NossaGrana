import re
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.utils import timezone
import logging

logger = logging.getLogger('fraud_detection')


class FraudValidators:
    """Validadores para detecção de fraudes financeiras"""
    
    @staticmethod
    def validate_velocity_check(user, amount, time_window=3600):
        """Verifica velocidade de transações (velocity check)"""
        cache_key = f"velocity_{user.id}"
        transactions = cache.get(cache_key, [])
        
        current_time = timezone.now().timestamp()
        cutoff_time = current_time - time_window
        
        # Filtrar transações dentro da janela de tempo
        recent_transactions = [
            tx for tx in transactions 
            if tx['timestamp'] > cutoff_time
        ]
        
        # Adicionar transação atual
        recent_transactions.append({
            'amount': float(amount),
            'timestamp': current_time
        })
        
        # Verificar limites
        total_amount = sum(tx['amount'] for tx in recent_transactions)
        transaction_count = len(recent_transactions)
        
        # Limites por hora
        if total_amount > 20000:  # R$ 20.000/hora
            raise ValidationError('Limite de valor por hora excedido')
        
        if transaction_count > 50:  # 50 transações/hora
            raise ValidationError('Limite de transações por hora excedido')
        
        # Salvar no cache
        cache.set(cache_key, recent_transactions, time_window)
        return True
    
    @staticmethod
    def validate_geolocation_risk(user, request_ip, location_data=None):
        """Valida risco baseado em geolocalização"""
        cache_key = f"geo_locations_{user.id}"
        known_locations = cache.get(cache_key, [])
        
        current_location = {
            'ip': request_ip,
            'timestamp': timezone.now().timestamp(),
            'country': location_data.get('country') if location_data else 'BR'
        }
        
        # Verificar se é uma localização conhecida
        is_known_location = any(
            loc['ip'] == request_ip for loc in known_locations
        )
        
        if not is_known_location:
            # Verificar se há mudança geográfica suspeita
            if known_locations:
                last_location = max(known_locations, key=lambda x: x['timestamp'])
                time_diff = current_location['timestamp'] - last_location['timestamp']
                
                # Se última transação foi há menos de 1 hora e país diferente
                if (time_diff < 3600 and 
                    last_location.get('country') != current_location['country']):
                    logger.warning(
                        f"Suspicious location change for user {user.id}: "
                        f"{last_location.get('country')} -> {current_location['country']}"
                    )
                    raise ValidationError('Mudança de localização suspeita detectada')
            
            # Adicionar nova localização
            known_locations.append(current_location)
            # Manter apenas últimas 10 localizações
            known_locations = known_locations[-10:]
            cache.set(cache_key, known_locations, 86400 * 30)  # 30 dias
        
        return True
    
    @staticmethod
    def validate_behavioral_pattern(user, transaction_data):
        """Valida padrões comportamentais do usuário"""
        cache_key = f"behavior_{user.id}"
        behavior_data = cache.get(cache_key, {
            'avg_amount': 0,
            'common_categories': [],
            'usual_times': [],
            'transaction_count': 0
        })
        
        amount = float(transaction_data.get('amount', 0))
        category = transaction_data.get('category', '')
        hour = timezone.now().hour
        
        # Atualizar dados comportamentais
        behavior_data['transaction_count'] += 1
        
        # Calcular média de valores
        if behavior_data['transaction_count'] > 1:
            current_avg = behavior_data['avg_amount']
            new_avg = ((current_avg * (behavior_data['transaction_count'] - 1)) + amount) / behavior_data['transaction_count']
            behavior_data['avg_amount'] = new_avg
        else:
            behavior_data['avg_amount'] = amount
        
        # Atualizar categorias comuns
        if category not in behavior_data['common_categories']:
            behavior_data['common_categories'].append(category)
        
        # Atualizar horários usuais
        behavior_data['usual_times'].append(hour)
        behavior_data['usual_times'] = behavior_data['usual_times'][-50:]  # Últimas 50
        
        # Verificar anomalias
        if behavior_data['transaction_count'] > 10:
            # Valor muito acima da média
            if amount > behavior_data['avg_amount'] * 5:
                logger.warning(f"Unusual amount for user {user.id}: {amount} vs avg {behavior_data['avg_amount']}")
            
            # Horário incomum
            common_hours = set(behavior_data['usual_times'])
            if len(common_hours) > 5 and hour not in common_hours:
                logger.info(f"Unusual time for user {user.id}: {hour}h")
        
        cache.set(cache_key, behavior_data, 86400 * 7)  # 7 dias
        return True
    
    @staticmethod
    def validate_device_consistency(user, device_fingerprint):
        """Valida consistência do dispositivo"""
        cache_key = f"device_consistency_{user.id}"
        device_data = cache.get(cache_key, {})
        
        if not device_fingerprint:
            return True
        
        current_fp = str(device_fingerprint)
        
        if 'fingerprints' not in device_data:
            device_data['fingerprints'] = []
        
        # Verificar se é um dispositivo conhecido
        is_known = any(
            fp['fingerprint'] == current_fp 
            for fp in device_data['fingerprints']
        )
        
        if not is_known:
            # Novo dispositivo
            device_data['fingerprints'].append({
                'fingerprint': current_fp,
                'first_seen': timezone.now().timestamp(),
                'last_seen': timezone.now().timestamp()
            })
            
            # Manter apenas últimos 5 dispositivos
            device_data['fingerprints'] = device_data['fingerprints'][-5:]
            
            logger.info(f"New device detected for user {user.id}")
        else:
            # Atualizar último acesso
            for fp in device_data['fingerprints']:
                if fp['fingerprint'] == current_fp:
                    fp['last_seen'] = timezone.now().timestamp()
                    break
        
        cache.set(cache_key, device_data, 86400 * 30)  # 30 dias
        return True
    
    @staticmethod
    def validate_transaction_pattern(transactions_list):
        """Valida padrões suspeitos em lista de transações"""
        if len(transactions_list) < 3:
            return True
        
        amounts = [float(tx.get('amount', 0)) for tx in transactions_list]
        
        # Verificar valores idênticos repetidos
        identical_count = {}
        for amount in amounts:
            identical_count[amount] = identical_count.get(amount, 0) + 1
        
        max_identical = max(identical_count.values())
        if max_identical > len(amounts) * 0.7:  # Mais de 70% iguais
            raise ValidationError('Padrão suspeito: muitos valores idênticos')
        
        # Verificar progressão aritmética (possível teste de limites)
        if len(amounts) >= 5:
            diffs = [amounts[i+1] - amounts[i] for i in range(len(amounts)-1)]
            if len(set(diffs)) == 1 and diffs[0] > 0:  # Progressão constante
                logger.warning("Arithmetic progression detected in transactions")
        
        return True
    
    @staticmethod
    def calculate_risk_score(user, transaction_data, context_data):
        """Calcula score de risco da transação"""
        risk_score = 0
        
        amount = float(transaction_data.get('amount', 0))
        
        # Fatores de risco
        if amount > 5000:
            risk_score += 20
        elif amount > 1000:
            risk_score += 10
        
        # Horário
        hour = timezone.now().hour
        if hour < 6 or hour > 22:
            risk_score += 15
        
        # Novo dispositivo
        if context_data.get('new_device'):
            risk_score += 25
        
        # Nova localização
        if context_data.get('new_location'):
            risk_score += 30
        
        # Frequência alta
        if context_data.get('high_frequency'):
            risk_score += 20
        
        # Classificar risco
        if risk_score >= 70:
            return 'HIGH'
        elif risk_score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'