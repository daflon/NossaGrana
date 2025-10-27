from django.core.management.base import BaseCommand
from django.utils import timezone
from budgets.models import Budget, BudgetAlert
from datetime import date


class Command(BaseCommand):
    help = 'Gera alertas automáticos para todos os orçamentos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            help='Mês para gerar alertas (formato: YYYY-MM). Padrão: mês atual'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID do usuário específico (opcional)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem criar alertas (apenas mostra o que seria feito)'
        )

    def handle(self, *args, **options):
        # Determinar mês
        if options['month']:
            try:
                year, month = options['month'].split('-')
                target_month = date(int(year), int(month), 1)
            except (ValueError, TypeError):
                self.stdout.write(
                    self.style.ERROR('Formato de mês inválido. Use YYYY-MM')
                )
                return
        else:
            target_month = date.today().replace(day=1)

        # Filtrar orçamentos
        budgets = Budget.objects.filter(month=target_month)
        
        if options['user_id']:
            budgets = budgets.filter(user_id=options['user_id'])

        budgets = budgets.select_related('user', 'category')

        self.stdout.write(
            f"Processando {budgets.count()} orçamentos para {target_month.strftime('%m/%Y')}"
        )

        total_alerts = 0
        processed_budgets = 0

        for budget in budgets:
            try:
                if options['dry_run']:
                    # Simular geração de alertas
                    alert_level = budget.alert_level
                    alert_message = budget.get_alert_message()
                    
                    self.stdout.write(
                        f"[DRY RUN] {budget.user.username} - {budget.category.name}: "
                        f"{alert_level} - {alert_message}"
                    )
                    
                    # Contar alertas que seriam criados
                    if budget.is_over_budget:
                        total_alerts += 1
                    if budget.is_near_limit and not budget.is_over_budget:
                        total_alerts += 1
                    if budget.projected_overspend > 0 and not budget.is_over_budget:
                        total_alerts += 1
                    if budget.spending_trend == 'accelerating' and budget.percentage_used >= 60:
                        total_alerts += 1
                else:
                    # Gerar alertas reais
                    alerts = BudgetAlert.check_and_create_alerts(budget)
                    total_alerts += len(alerts)
                    
                    if alerts:
                        alert_types = [alert.get_alert_type_display() for alert in alerts]
                        self.stdout.write(
                            f"[OK] {budget.user.username} - {budget.category.name}: "
                            f"{len(alerts)} alertas ({', '.join(alert_types)})"
                        )

                processed_budgets += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Erro ao processar orçamento {budget.id}: {str(e)}"
                    )
                )

        # Resumo
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n[DRY RUN] Processamento concluído:\n"
                    f"- Orçamentos processados: {processed_budgets}\n"
                    f"- Alertas que seriam criados: {total_alerts}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nProcessamento concluído:\n"
                    f"- Orçamentos processados: {processed_budgets}\n"
                    f"- Alertas criados/atualizados: {total_alerts}"
                )
            )

        # Estatísticas adicionais
        if not options['dry_run']:
            active_alerts = BudgetAlert.objects.filter(
                budget__month=target_month,
                is_active=True
            )
            
            if options['user_id']:
                active_alerts = active_alerts.filter(budget__user_id=options['user_id'])
            
            alert_stats = {}
            for alert in active_alerts:
                level = alert.alert_level
                alert_stats[level] = alert_stats.get(level, 0) + 1
            
            self.stdout.write("\nAlertas ativos por nível:")
            for level, count in alert_stats.items():
                self.stdout.write(f"- {level.capitalize()}: {count}")