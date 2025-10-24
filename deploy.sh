#!/bin/bash

# Deploy Script para Nossa Grana
set -e

echo "🚀 Iniciando deploy da aplicação Nossa Grana..."

# Verificar se o arquivo .env.prod existe
if [ ! -f .env.prod ]; then
    echo "❌ Arquivo .env.prod não encontrado!"
    echo "Copie .env.prod.example e configure as variáveis de ambiente."
    exit 1
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose -f docker-compose.prod.yml down

# Fazer backup do banco de dados (se existir)
if docker volume ls | grep -q "nossa_grana_postgres_data"; then
    echo "💾 Fazendo backup do banco de dados..."
    mkdir -p backups
    docker run --rm \
        -v nossa_grana_postgres_data:/data \
        -v $(pwd)/backups:/backup \
        alpine tar czf /backup/db-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
fi

# Construir imagens
echo "🔨 Construindo imagens Docker..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Iniciar serviços
echo "🚀 Iniciando serviços..."
docker-compose -f docker-compose.prod.yml up -d

# Aguardar banco de dados
echo "⏳ Aguardando banco de dados..."
sleep 10

# Executar migrações
echo "🔄 Executando migrações..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput

# Criar superusuário (se não existir)
echo "👤 Verificando superusuário..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Criando superusuário...')
    User.objects.create_superuser('admin', 'admin@nossagrana.com', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
"

# Verificar status dos containers
echo "📊 Status dos containers:"
docker-compose -f docker-compose.prod.yml ps

# Verificar logs
echo "📝 Últimos logs:"
docker-compose -f docker-compose.prod.yml logs --tail=20

echo "✅ Deploy concluído com sucesso!"
echo "🌐 Aplicação disponível em: https://localhost"
echo "🔧 Admin disponível em: https://localhost/admin"
echo ""
echo "📋 Comandos úteis:"
echo "  Ver logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Parar: docker-compose -f docker-compose.prod.yml down"
echo "  Reiniciar: docker-compose -f docker-compose.prod.yml restart"