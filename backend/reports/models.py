from django.db import models
from django.contrib.auth.models import User


class Alert(models.Model):
    """
    Sistema de alertas para usuários
    """
    ALERT_TYPES = [
        ('budget_warning', 'Alerta de Orçamento (80%)'),
        ('budget_exceeded', 'Orçamento Excedido'),
        ('goal_achieved', 'Meta Atingida'),
        ('goal_overdue', 'Meta Atrasada'),
        ('reminder', 'Lembrete'),
    ]

    PRIORITY_LEVELS = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    type = models.CharField(max_length=20, choices=ALERT_TYPES, verbose_name='Tipo')
    title = models.CharField(max_length=100, verbose_name='Título')
    message = models.TextField(verbose_name='Mensagem')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium', verbose_name='Prioridade')
    is_read = models.BooleanField(default=False, verbose_name='Lido')
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Data de Leitura')

    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.user.username}'

    def mark_as_read(self):
        """
        Marca o alerta como lido
        """
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class Reminder(models.Model):
    """
    Lembretes configuráveis pelos usuários
    """
    FREQUENCY_CHOICES = [
        ('once', 'Uma vez'),
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    title = models.CharField(max_length=100, verbose_name='Título')
    description = models.TextField(blank=True, verbose_name='Descrição')
    reminder_date = models.DateTimeField(verbose_name='Data do Lembrete')
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='once', verbose_name='Frequência')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    last_sent = models.DateTimeField(null=True, blank=True, verbose_name='Último Envio')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lembrete'
        verbose_name_plural = 'Lembretes'
        ordering = ['reminder_date']

    def __str__(self):
        return f'{self.title} - {self.reminder_date.strftime("%d/%m/%Y %H:%M")}'