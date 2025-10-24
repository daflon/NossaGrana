from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Carrega dados iniciais do sistema'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Carregando categorias padrão...'))
        
        try:
            call_command('loaddata', 'categories.json')
            self.stdout.write(
                self.style.SUCCESS('Dados iniciais carregados com sucesso!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao carregar dados iniciais: {e}')
            )