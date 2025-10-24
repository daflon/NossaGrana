from django.core.management.base import BaseCommand
from transactions.models import Category


class Command(BaseCommand):
    help = 'Cria as categorias padrão do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a recriação das categorias padrão, mesmo se já existirem',
        )

    def handle(self, *args, **options):
        default_categories = [
            {
                'name': 'Alimentação',
                'color': '#FF6B6B',
                'icon': 'restaurant'
            },
            {
                'name': 'Transporte',
                'color': '#4ECDC4',
                'icon': 'directions_car'
            },
            {
                'name': 'Lazer',
                'color': '#45B7D1',
                'icon': 'sports_esports'
            },
            {
                'name': 'Saúde',
                'color': '#96CEB4',
                'icon': 'local_hospital'
            },
            {
                'name': 'Educação',
                'color': '#FFEAA7',
                'icon': 'school'
            },
            {
                'name': 'Casa',
                'color': '#DDA0DD',
                'icon': 'home'
            },
            {
                'name': 'Trabalho',
                'color': '#98D8C8',
                'icon': 'work'
            },
            {
                'name': 'Investimentos',
                'color': '#F7DC6F',
                'icon': 'trending_up'
            },
            {
                'name': 'Compras',
                'color': '#BB8FCE',
                'icon': 'shopping_cart'
            },
            {
                'name': 'Serviços',
                'color': '#85C1E9',
                'icon': 'build'
            },
            {
                'name': 'Impostos',
                'color': '#F1948A',
                'icon': 'account_balance'
            },
            {
                'name': 'Outros',
                'color': '#BDC3C7',
                'icon': 'category'
            }
        ]

        created_count = 0
        updated_count = 0

        for category_data in default_categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'color': category_data['color'],
                    'icon': category_data['icon'],
                    'is_default': True
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Categoria "{category.name}" criada com sucesso.')
                )
            else:
                if options['force']:
                    # Atualizar categoria existente
                    category.color = category_data['color']
                    category.icon = category_data['icon']
                    category.is_default = True
                    category.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Categoria "{category.name}" atualizada.')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Categoria "{category.name}" já existe.')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nResumo: {created_count} categorias criadas, {updated_count} atualizadas.'
            )
        )

        # Verificar se todas as categorias padrão estão marcadas corretamente
        default_names = [cat['name'] for cat in default_categories]
        Category.objects.filter(name__in=default_names).update(is_default=True)

        self.stdout.write(
            self.style.SUCCESS('Comando executado com sucesso!')
        )