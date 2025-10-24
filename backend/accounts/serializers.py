from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['family_name']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    family_name = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'family_name']

    def validate_email(self, value):
        """
        Verifica se o email já está em uso
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value

    def validate_username(self, value):
        """
        Verifica se o username já está em uso
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value

    def validate(self, attrs):
        """
        Verifica se as senhas coincidem
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs

    def create(self, validated_data):
        """
        Cria um novo usuário com perfil
        """
        # Remove campos que não pertencem ao modelo User
        family_name = validated_data.pop('family_name')
        validated_data.pop('password_confirm')
        
        # Cria o usuário
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Atualiza o perfil (criado automaticamente pelo signal)
        user.profile.family_name = family_name
        user.profile.save()
        
        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile']

    def update(self, instance, validated_data):
        """
        Atualiza o usuário e seu perfil
        """
        profile_data = validated_data.pop('profile', {})
        
        # Atualiza dados do usuário
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        
        # Atualiza dados do perfil
        if profile_data:
            profile = instance.profile
            profile.family_name = profile_data.get('family_name', profile.family_name)
            profile.save()
        
        return instance


class EmailLoginSerializer(serializers.Serializer):
    """
    Serializer para login com email
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = User.objects.filter(email=email).first()
            if not user:
                raise serializers.ValidationError('Credenciais inválidas.')
            
            user = authenticate(username=user.username, password=password)
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('Conta desativada.')
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError('Credenciais inválidas.')
        else:
            raise serializers.ValidationError('Email e senha são obrigatórios.')