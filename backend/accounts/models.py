from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Perfil estendido do usuário para informações familiares
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    family_name = models.CharField(max_length=100, verbose_name='Nome da Família')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil do Usuário'
        verbose_name_plural = 'Perfis dos Usuários'

    def __str__(self):
        return f'{self.user.get_full_name()} - {self.family_name}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Cria automaticamente um perfil quando um usuário é criado
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Salva o perfil quando o usuário é salvo
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()