#!/bin/bash

# Script de Backup para Nossa Grana
set -e

BACKUP_DIR="backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="nossa-grana-backup-$DATE"

echo "💾 Iniciando backup da aplicação Nossa Grana..."

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
echo "📊 Fazendo backup do banco de dados..."
if docker-compose -f docker-compose.prod.yml ps db | grep -q "Up"; then
    docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U nossa_grana_user nossa_grana_prod > "$BACKUP_DIR/database-$DATE.sql"
    echo "✅ Backup do banco salvo em: $BACKUP_DIR/database-$DATE.sql"
else
    echo "⚠️  Container do banco não está rodando"
fi

# Backup dos volumes Docker
echo "📦 Fazendo backup dos volumes..."
if docker volume ls | grep -q "nossa_grana_postgres_data"; then
    docker run --rm \
        -v nossa_grana_postgres_data:/data:ro \
        -v $(pwd)/$BACKUP_DIR:/backup \
        alpine tar czf /backup/postgres-volume-$DATE.tar.gz -C /data .
    echo "✅ Volume PostgreSQL salvo em: $BACKUP_DIR/postgres-volume-$DATE.tar.gz"
fi

if docker volume ls | grep -q "nossa_grana_static_volume"; then
    docker run --rm \
        -v nossa_grana_static_volume:/data:ro \
        -v $(pwd)/$BACKUP_DIR:/backup \
        alpine tar czf /backup/static-volume-$DATE.tar.gz -C /data .
    echo "✅ Volume static salvo em: $BACKUP_DIR/static-volume-$DATE.tar.gz"
fi

if docker volume ls | grep -q "nossa_grana_media_volume"; then
    docker run --rm \
        -v nossa_grana_media_volume:/data:ro \
        -v $(pwd)/$BACKUP_DIR:/backup \
        alpine tar czf /backup/media-volume-$DATE.tar.gz -C /data .
    echo "✅ Volume media salvo em: $BACKUP_DIR/media-volume-$DATE.tar.gz"
fi

# Backup das configurações
echo "⚙️  Fazendo backup das configurações..."
tar czf "$BACKUP_DIR/config-$DATE.tar.gz" \
    .env.prod \
    docker-compose.prod.yml \
    nginx/ \
    --exclude=nginx/ssl/*.key 2>/dev/null || true
echo "✅ Configurações salvas em: $BACKUP_DIR/config-$DATE.tar.gz"

# Criar arquivo de informações do backup
cat > "$BACKUP_DIR/backup-info-$DATE.txt" << EOF
Backup da Aplicação Nossa Grana
===============================
Data: $(date)
Versão: $(git rev-parse HEAD 2>/dev/null || echo "N/A")
Branch: $(git branch --show-current 2>/dev/null || echo "N/A")

Arquivos incluídos:
- database-$DATE.sql (dump do PostgreSQL)
- postgres-volume-$DATE.tar.gz (volume completo do PostgreSQL)
- static-volume-$DATE.tar.gz (arquivos estáticos)
- media-volume-$DATE.tar.gz (arquivos de mídia)
- config-$DATE.tar.gz (configurações)

Para restaurar:
1. Restaurar banco: psql -U usuario -d database < database-$DATE.sql
2. Restaurar volumes: docker run --rm -v volume_name:/data -v \$(pwd):/backup alpine tar xzf /backup/volume-file.tar.gz -C /data
3. Restaurar configurações: tar xzf config-$DATE.tar.gz
EOF

echo "✅ Informações do backup salvas em: $BACKUP_DIR/backup-info-$DATE.txt"

# Limpar backups antigos (manter apenas os últimos 7 dias)
echo "🧹 Limpando backups antigos..."
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete 2>/dev/null || true
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete 2>/dev/null || true
find $BACKUP_DIR -name "*.txt" -mtime +7 -delete 2>/dev/null || true

# Mostrar tamanho total dos backups
BACKUP_SIZE=$(du -sh $BACKUP_DIR 2>/dev/null | cut -f1)
echo "📊 Tamanho total dos backups: $BACKUP_SIZE"

echo ""
echo "✅ Backup concluído com sucesso!"
echo "📁 Arquivos salvos em: $BACKUP_DIR/"
echo ""
echo "💡 Dica: Configure um cron job para executar backups automaticamente:"
echo "   0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1"