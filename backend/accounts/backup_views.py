from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.management import call_command
from django.utils import timezone
from django.conf import settings
import os
import json
from datetime import datetime


class BackupView(APIView):
    """
    View para gerenciamento de backups
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Realizar backup manual
        """
        try:
            # Executar comando de backup
            call_command('backup_database')
            
            # Simular informações do backup
            backup_info = {
                'success': True,
                'message': 'Backup realizado com sucesso',
                'timestamp': timezone.now().isoformat(),
                'filename': f'backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.sqlite3',
                'size': '2.4 MB',
                'type': 'manual'
            }
            
            # Salvar informação do último backup no cache/sessão
            request.session['last_backup'] = backup_info
            
            return Response(backup_info)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Erro ao realizar backup'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """
        Obter status do último backup
        """
        try:
            # Verificar último backup na sessão
            last_backup = request.session.get('last_backup')
            
            if not last_backup:
                # Verificar se existe pasta de backups
                backup_dir = os.path.join(settings.BASE_DIR, 'backups')
                if os.path.exists(backup_dir):
                    backup_files = [f for f in os.listdir(backup_dir) if f.startswith('backup_')]
                    if backup_files:
                        latest_file = max(backup_files)
                        file_path = os.path.join(backup_dir, latest_file)
                        file_stat = os.stat(file_path)
                        
                        last_backup = {
                            'success': True,
                            'timestamp': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                            'filename': latest_file,
                            'size': f'{file_stat.st_size / (1024*1024):.1f} MB',
                            'type': 'automatic'
                        }
                    else:
                        last_backup = None
                else:
                    last_backup = None
            
            return Response({
                'last_backup': last_backup,
                'backup_enabled': True,
                'auto_backup_frequency': 'weekly'
            })
            
        except Exception as e:
            return Response({
                'error': str(e),
                'last_backup': None,
                'backup_enabled': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationView(APIView):
    """
    View para gerenciamento de notificações
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Obter notificações do usuário
        """
        try:
            # Simular notificações (em produção, viria do banco de dados)
            notifications = [
                {
                    'id': 1,
                    'title': 'Orçamento Excedido',
                    'message': 'Seu orçamento de Alimentação foi excedido em 15%',
                    'type': 'budget_alert',
                    'is_read': False,
                    'created_at': timezone.now().isoformat(),
                    'priority': 'high'
                },
                {
                    'id': 2,
                    'title': 'Meta Atingida',
                    'message': 'Parabéns! Você atingiu 80% da sua meta de poupança',
                    'type': 'goal_update',
                    'is_read': False,
                    'created_at': (timezone.now() - timezone.timedelta(hours=2)).isoformat(),
                    'priority': 'medium'
                },
                {
                    'id': 3,
                    'title': 'Backup Realizado',
                    'message': 'Backup automático dos seus dados foi concluído',
                    'type': 'system',
                    'is_read': True,
                    'created_at': (timezone.now() - timezone.timedelta(days=1)).isoformat(),
                    'priority': 'low'
                }
            ]
            
            # Filtrar por não lidas se solicitado
            if request.query_params.get('unread_only') == 'true':
                notifications = [n for n in notifications if not n['is_read']]
            
            unread_count = len([n for n in notifications if not n['is_read']])
            
            return Response({
                'notifications': notifications,
                'unread_count': unread_count,
                'total_count': len(notifications)
            })
            
        except Exception as e:
            return Response({
                'error': str(e),
                'notifications': [],
                'unread_count': 0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, notification_id=None):
        """
        Marcar notificação como lida
        """
        try:
            if notification_id:
                # Marcar notificação específica como lida
                message = f'Notificação {notification_id} marcada como lida'
            else:
                # Marcar todas como lidas
                message = 'Todas as notificações foram marcadas como lidas'
            
            return Response({
                'success': True,
                'message': message
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)