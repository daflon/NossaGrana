import os
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Cria backup automático do banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-days',
            type=int,
            default=30,
            help='Número de dias para manter backups (padrão: 30)'
        )

    def handle(self, *args, **options):
        try:
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'backup_{timestamp}.sqlite3'
            backup_path = os.path.join(backup_dir, backup_filename)
            
            db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
            
            if not os.path.exists(db_path):
                self.stdout.write(self.style.ERROR('Banco de dados não encontrado!'))
                return
            
            shutil.copy2(db_path, backup_path)
            self._cleanup_old_backups(backup_dir, options['keep_days'])
            
            self.stdout.write(self.style.SUCCESS(f'Backup criado: {backup_filename}'))
            logger.info(f'Backup automático criado: {backup_filename}')
            
        except Exception as e:
            error_msg = f'Erro ao criar backup: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(error_msg)

    def _cleanup_old_backups(self, backup_dir, keep_days):
        try:
            import time
            current_time = time.time()
            
            for filename in os.listdir(backup_dir):
                if filename.startswith('backup_') and filename.endswith('.sqlite3'):
                    file_path = os.path.join(backup_dir, filename)
                    file_age = current_time - os.path.getctime(file_path)
                    
                    if file_age > (keep_days * 24 * 60 * 60):
                        os.remove(file_path)
                        self.stdout.write(f'Backup antigo removido: {filename}')
                        
        except Exception as e:
            logger.warning(f'Erro ao limpar backups antigos: {str(e)}')