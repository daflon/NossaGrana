from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models import Sum
from transactions.models import Category, Transaction
from datetime import datetime, date


class Budget(models.Model):
    """
    Orçamentos mensais por categoria
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Categoria')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor Orçado'
    )
    month = models.DateField(verbose_name='Mês (primeiro dia)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'
        unique_together = ['user', 'category', 'month']
        ordering = ['-month', 'category__name']

    def __str__(self):
        return f'{self.category.name} - {self.month.strftime("%m/%Y")} - R$ {self.amount}'

    @property
    def spent_amount(self):
        """
        Calcula o valor gasto na categoria no mês
        """
        start_date = self.month
        if self.month.month == 12:
            end_date = datetime(self.month.year + 1, 1, 1).date()
        else:
            end_date = datetime(self.month.year, self.month.month + 1, 1).date()

        spent = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            type='expense',
            date__gte=start_date,
            date__lt=end_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        return spent

    @property
    def remaining_amount(self):
        """
        Calcula o valor restante do orçamento
        """
        return self.amount - self.spent_amount

    @property
    def percentage_used(self):
        """
        Calcula a porcentagem utilizada do orçamento
        """
        if self.amount == 0:
            return 0
        return float((self.spent_amount / self.amount) * 100)

    @property
    def is_over_budget(self):
        """
        Verifica se o orçamento foi excedido
        """
        return self.spent_amount > self.amount

    @property
    def is_near_limit(self):
        """
        Verifica se está próximo do limite (80%)
        """
        return self.percentage_used >= 80

    @property
    def daily_average_spent(self):
        """
        Calcula a média diária de gastos no mês atual
        """
        from datetime import date
        
        current_date = date.today()
        start_date = self.month
        
        # Se o orçamento é do mês atual, usar data atual, senão usar último dia do mês
        if self.month.year == current_date.year and self.month.month == current_date.month:
            days_passed = current_date.day
        else:
            # Calcular último dia do mês do orçamento
            if self.month.month == 12:
                last_day = 31
            else:
                from calendar import monthrange
                last_day = monthrange(self.month.year, self.month.month)[1]
            days_passed = last_day
        
        if days_passed == 0:
            return Decimal('0.00')
        
        return self.spent_amount / days_passed

    @property
    def projected_monthly_spending(self):
        """
        Projeta o gasto total do mês baseado na média diária atual
        """
        from calendar import monthrange
        from datetime import date
        
        current_date = date.today()
        
        # Se não é o mês atual, retornar o gasto real
        if not (self.month.year == current_date.year and self.month.month == current_date.month):
            return self.spent_amount
        
        # Calcular total de dias no mês
        total_days = monthrange(self.month.year, self.month.month)[1]
        
        # Projeção baseada na média diária
        daily_avg = self.daily_average_spent
        return daily_avg * total_days

    @property
    def projected_overspend(self):
        """
        Calcula quanto o orçamento pode ser excedido baseado na projeção
        """
        projected = self.projected_monthly_spending
        if projected > self.amount:
            return projected - self.amount
        return Decimal('0.00')

    @property
    def days_until_limit(self):
        """
        Calcula quantos dias restam até atingir o limite do orçamento
        """
        from datetime import date
        from calendar import monthrange
        
        current_date = date.today()
        
        # Se não é o mês atual ou já excedeu, retornar 0
        if not (self.month.year == current_date.year and self.month.month == current_date.month):
            return 0
        
        if self.is_over_budget:
            return 0
        
        daily_avg = self.daily_average_spent
        if daily_avg == 0:
            return monthrange(self.month.year, self.month.month)[1] - current_date.day
        
        remaining_budget = self.remaining_amount
        days_until_limit = int(remaining_budget / daily_avg)
        
        # Não pode ser maior que os dias restantes no mês
        days_remaining_in_month = monthrange(self.month.year, self.month.month)[1] - current_date.day
        return min(days_until_limit, days_remaining_in_month)

    @property
    def spending_trend(self):
        """
        Analisa a tendência de gastos (acelerando, normal, desacelerando)
        """
        from datetime import date, timedelta
        
        current_date = date.today()
        
        # Se não é o mês atual, retornar 'completed'
        if not (self.month.year == current_date.year and self.month.month == current_date.month):
            return 'completed'
        
        # Se ainda não há gastos suficientes para análise
        if current_date.day < 7:
            return 'insufficient_data'
        
        # Calcular gastos da primeira e segunda metade do período atual
        mid_point = current_date.day // 2
        mid_date = self.month.replace(day=mid_point)
        
        # Gastos da primeira metade
        first_half_spent = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            type='expense',
            date__gte=self.month,
            date__lt=mid_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Gastos da segunda metade
        second_half_spent = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            type='expense',
            date__gte=mid_date,
            date__lt=current_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Calcular médias diárias
        first_half_days = mid_point
        second_half_days = current_date.day - mid_point
        
        if first_half_days == 0 or second_half_days == 0:
            return 'insufficient_data'
        
        first_half_avg = first_half_spent / first_half_days
        second_half_avg = second_half_spent / second_half_days
        
        # Determinar tendência
        if second_half_avg > first_half_avg * Decimal('1.2'):  # 20% maior
            return 'accelerating'
        elif second_half_avg < first_half_avg * Decimal('0.8'):  # 20% menor
            return 'decelerating'
        else:
            return 'stable'

    @property
    def alert_level(self):
        """
        Determina o nível de alerta baseado em múltiplos fatores
        """
        if self.is_over_budget:
            return 'critical'
        
        if self.percentage_used >= 90:
            return 'high'
        
        if self.percentage_used >= 80:
            return 'medium'
        
        # Verificar projeção
        if self.projected_overspend > 0:
            return 'medium'
        
        # Verificar tendência
        trend = self.spending_trend
        if trend == 'accelerating' and self.percentage_used >= 60:
            return 'medium'
        
        return 'low'

    def get_alert_message(self):
        """
        Retorna mensagem de alerta personalizada
        """
        alert_level = self.alert_level
        
        if alert_level == 'critical':
            overspend = self.spent_amount - self.amount
            return f"Orçamento excedido em R$ {overspend:.2f}!"
        
        elif alert_level == 'high':
            return f"Atenção! Você já gastou {self.percentage_used:.1f}% do orçamento."
        
        elif alert_level == 'medium':
            if self.projected_overspend > 0:
                return f"Cuidado! Projeção indica possível excesso de R$ {self.projected_overspend:.2f}."
            else:
                return f"Atenção! Você já gastou {self.percentage_used:.1f}% do orçamento."
        
        return "Orçamento sob controle."

    def get_recommendations(self):
        """
        Retorna recomendações baseadas na análise do orçamento
        """
        recommendations = []
        
        if self.is_over_budget:
            recommendations.append("Reduza gastos nesta categoria imediatamente.")
            recommendations.append("Considere realocar recursos de outras categorias.")
        
        elif self.alert_level == 'high':
            days_left = self.days_until_limit
            if days_left <= 5:
                recommendations.append(f"Apenas {days_left} dias até o limite. Controle os gastos!")
            recommendations.append("Monitore cada gasto nesta categoria.")
        
        elif self.alert_level == 'medium':
            if self.projected_overspend > 0:
                recommendations.append("Reduza a média diária de gastos para evitar exceder o orçamento.")
            
            trend = self.spending_trend
            if trend == 'accelerating':
                recommendations.append("Seus gastos estão acelerando. Revise seus hábitos.")
        
        else:
            recommendations.append("Continue mantendo o controle dos gastos.")
            if self.percentage_used < 50:
                recommendations.append("Você está no caminho certo! Orçamento bem controlado.")
        
        return recommendations

    def clean(self):
        """
        Validações customizadas
        """
        from django.core.exceptions import ValidationError
        
        # O mês deve ser o primeiro dia do mês
        if self.month and self.month.day != 1:
            raise ValidationError({'month': 'A data deve ser o primeiro dia do mês.'})

    def save(self, *args, **kwargs):
        # Garantir que seja sempre o primeiro dia do mês
        if self.month:
            self.month = self.month.replace(day=1)
        self.full_clean()
        super().save(*args, **kwargs)


class BudgetAlert(models.Model):
    """
    Alertas automáticos para orçamentos
    """
    ALERT_TYPES = [
        ('near_limit', 'Próximo do Limite (80%)'),
        ('over_budget', 'Orçamento Excedido'),
        ('projection_warning', 'Projeção de Excesso'),
        ('trend_warning', 'Tendência Preocupante'),
    ]
    
    ALERT_LEVELS = [
        ('low', 'Baixo'),
        ('medium', 'Médio'),
        ('high', 'Alto'),
        ('critical', 'Crítico'),
    ]

    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    alert_level = models.CharField(max_length=10, choices=ALERT_LEVELS)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Alerta de Orçamento'
        verbose_name_plural = 'Alertas de Orçamento'
        ordering = ['-created_at']
        unique_together = ['budget', 'alert_type', 'is_active']

    def __str__(self):
        return f'{self.budget.category.name} - {self.get_alert_type_display()}'

    def resolve(self):
        """
        Marca o alerta como resolvido
        """
        self.is_active = False
        self.resolved_at = datetime.now()
        self.save()

    @classmethod
    def create_or_update_alert(cls, budget, alert_type, alert_level, message):
        """
        Cria ou atualiza um alerta para o orçamento
        """
        # Verificar se já existe um alerta ativo deste tipo
        existing_alert = cls.objects.filter(
            budget=budget,
            alert_type=alert_type,
            is_active=True
        ).first()

        if existing_alert:
            # Atualizar alerta existente
            existing_alert.alert_level = alert_level
            existing_alert.message = message
            existing_alert.save()
            return existing_alert
        else:
            # Criar novo alerta
            return cls.objects.create(
                budget=budget,
                alert_type=alert_type,
                alert_level=alert_level,
                message=message
            )

    @classmethod
    @transaction.atomic
    def check_and_create_alerts(cls, budget):
        """
        Verifica e cria alertas automáticos para um orçamento com lock
        """
        # Lock no orçamento para evitar criação duplicada de alertas
        budget = Budget.objects.select_for_update().get(id=budget.id)
        alerts_created = []

        # Alerta de orçamento excedido
        if budget.is_over_budget:
            alert = cls.create_or_update_alert(
                budget=budget,
                alert_type='over_budget',
                alert_level='critical',
                message=f"Orçamento excedido em R$ {(budget.spent_amount - budget.amount):.2f}"
            )
            alerts_created.append(alert)
        else:
            # Resolver alerta de orçamento excedido se existir
            cls.objects.filter(
                budget=budget,
                alert_type='over_budget',
                is_active=True
            ).update(is_active=False, resolved_at=datetime.now())

        # Alerta de proximidade do limite
        if budget.is_near_limit and not budget.is_over_budget:
            alert = cls.create_or_update_alert(
                budget=budget,
                alert_type='near_limit',
                alert_level='high',
                message=f"Você já gastou {budget.percentage_used:.1f}% do orçamento"
            )
            alerts_created.append(alert)
        else:
            # Resolver alerta de proximidade se não aplicável
            if not budget.is_near_limit:
                cls.objects.filter(
                    budget=budget,
                    alert_type='near_limit',
                    is_active=True
                ).update(is_active=False, resolved_at=datetime.now())

        # Alerta de projeção de excesso
        if budget.projected_overspend > 0 and not budget.is_over_budget:
            alert = cls.create_or_update_alert(
                budget=budget,
                alert_type='projection_warning',
                alert_level='medium',
                message=f"Projeção indica possível excesso de R$ {budget.projected_overspend:.2f}"
            )
            alerts_created.append(alert)
        else:
            # Resolver alerta de projeção se não aplicável
            if budget.projected_overspend == 0:
                cls.objects.filter(
                    budget=budget,
                    alert_type='projection_warning',
                    is_active=True
                ).update(is_active=False, resolved_at=datetime.now())

        # Alerta de tendência preocupante
        trend = budget.spending_trend
        if trend == 'accelerating' and budget.percentage_used >= 60:
            alert = cls.create_or_update_alert(
                budget=budget,
                alert_type='trend_warning',
                alert_level='medium',
                message="Seus gastos estão acelerando. Revise seus hábitos."
            )
            alerts_created.append(alert)
        else:
            # Resolver alerta de tendência se não aplicável
            if trend != 'accelerating' or budget.percentage_used < 60:
                cls.objects.filter(
                    budget=budget,
                    alert_type='trend_warning',
                    is_active=True
                ).update(is_active=False, resolved_at=datetime.now())

        return alerts_created