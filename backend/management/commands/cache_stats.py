from django.core.management.base import BaseCommand
from django.core.cache import cache
from utils.cache_manager import CacheManager

class Command(BaseCommand):
    help = 'Gerencia estatísticas e operações de cache'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Limpa todo o cache')
        parser.add_argument('--stats', action='store_true', help='Mostra estatísticas')
        parser.add_argument('--warm', type=int, help='Aquece cache para usuário ID')

    def handle(self, *args, **options):
        if options['clear']:
            cache.clear()
            self.stdout.write(self.style.SUCCESS('Cache limpo com sucesso'))
        
        if options['stats']:
            stats = CacheManager.get_cache_size()
            self.stdout.write(f"Status do cache: {stats}")
        
        if options['warm']:
            user_id = options['warm']
            endpoints = ['/api/transactions/', '/api/budgets/', '/api/reports/']
            CacheManager.warm_cache(user_id, endpoints)
            self.stdout.write(f'Cache aquecido para usuário {user_id}')