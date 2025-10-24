from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta


class Goal(models.Model):
    """
    Metas de poupança
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    name = models.CharField(max_length=100, verbose_name='Nome da Meta')
    description = models.TextField(blank=True, verbose_name='Descrição')
    target_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor Alvo'
    )
    current_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor Atual'
    )
    target_date = models.DateField(verbose_name='Data Objetivo')
    achieved = models.BooleanField(default=False, verbose_name='Meta Atingida')
    achieved_date = models.DateTimeField(null=True, blank=True, verbose_name='Data de Conquista')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Meta de Poupança'
        verbose_name_plural = 'Metas de Poupança'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - R$ {self.current_amount}/{self.target_amount}'

    @property
    def remaining_amount(self):
        """Calcula o valor restante para atingir a meta"""
        return max(self.target_amount - self.current_amount, Decimal('0.00'))

    @property
    def percentage_completed(self):
        """Calcula a porcentagem completada da meta"""
        if self.target_amount == 0:
            return 0
        return min(float((self.current_amount / self.target_amount) * 100), 100)

    @property
    def days_remaining(self):
        """Calcula quantos dias restam para a meta"""
        if self.achieved:
            return 0
        today = timezone.now().date()
        if self.target_date <= today:
            return 0
        return (self.target_date - today).days

    @property
    def is_overdue(self):
        """Verifica se a meta está atrasada"""
        return not self.achieved and self.target_date < timezone.now().date()

    def contribute(self, amount):
        """Adiciona uma contribuição à meta"""
        if amount <= 0:
            raise ValueError("O valor da contribuição deve ser positivo")

        self.current_amount += Decimal(str(amount))
        
        # Verifica se a meta foi atingida
        if not self.achieved and self.current_amount >= self.target_amount:
            self.achieved = True
            self.achieved_date = timezone.now()
            self.current_amount = self.target_amount  # Não permite exceder o valor alvo

        self.save()
        return self.achieved

    def clean(self):
        """Validações customizadas"""
        from django.core.exceptions import ValidationError
        
        # Data objetivo não pode ser passada (apenas para novas metas)
        if not self.pk and self.target_date and self.target_date < timezone.now().date():
            raise ValidationError({'target_date': 'A data objetivo não pode ser no passado.'})
        
        # Valor atual não pode ser maior que o valor alvo
        if self.current_amount > self.target_amount:
            raise ValidationError({'current_amount': 'O valor atual não pode ser maior que o valor alvo.'})
        
        # Nome deve ser único por usuário
        if Goal.objects.filter(user=self.user, name=self.name).exclude(pk=self.pk).exists():
            raise ValidationError({'name': 'Você já possui uma meta com este nome.'})

    def save(self, *args, **kwargs):
        # Verifica se a meta foi atingida
        if not self.achieved and self.current_amount >= self.target_amount:
            self.achieved = True
            if not self.achieved_date:
                self.achieved_date = timezone.now()
        elif self.achieved and self.current_amount < self.target_amount:
            self.achieved = False
            self.achieved_date = None

        self.full_clean()
        super().save(*args, **kwargs)


class GoalContribution(models.Model):
    """
    Histórico de contribuições para metas
    """
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='contributions', verbose_name='Meta')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor da Contribuição'
    )
    description = models.CharField(max_length=200, blank=True, verbose_name='Descrição')
    date = models.DateField(default=timezone.now, verbose_name='Data')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contribuição para Meta'
        verbose_name_plural = 'Contribuições para Metas'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.goal.name} - R$ {self.amount} ({self.date})'