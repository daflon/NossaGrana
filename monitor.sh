#!/bin/bash

# Script de Monitoramento para Nossa Grana
set -e

echo "📊 Monitor da Aplicação Nossa Grana"
echo "=================================="

# Função para verificar status do container
check_container() {
    local container=$1
    local status=$(docker-compose -f docker-compose.prod.yml ps -q $container 2>/dev/null)
    
    if [ -n "$status" ]; then
        local health=$(docker inspect --format='{{.State.Status}}' $(docker-compose -f docker-compose.prod.yml ps -q $container) 2>/dev/null)
        echo "✅ $container: $health"
    else
        echo "❌ $container: não encontrado"
    fi
}

# Verificar containers
echo "🐳 Status dos Containers:"
check_container "nginx"
check_container "backend"
check_container "frontend"
check_container "db"
check_container "redis"
check_container "celery"

echo ""

# Verificar uso de recursos
echo "💾 Uso de Recursos:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" $(docker-compose -f docker-compose.prod.yml ps -q) 2>/dev/null || echo "Nenhum container rodando"

echo ""

# Verificar volumes
echo "📦 Volumes:"
docker volume ls | grep nossa_grana || echo "Nenhum volume encontrado"

echo ""

# Verificar conectividade
echo "🌐 Testes de Conectividade:"

# Teste HTTP
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200\|301\|302"; then
    echo "✅ HTTP (porta 80): OK"
else
    echo "❌ HTTP (porta 80): Falha"
fi

# Teste HTTPS (se SSL estiver configurado)
if curl -k -s -o /dev/null -w "%{http_code}" https://localhost 2>/dev/null | grep -q "200\|301\|302"; then
    echo "✅ HTTPS (porta 443): OK"
else
    echo "⚠️  HTTPS (porta 443): Não configurado ou falha"
fi

# Teste API
if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health/ 2>/dev/null | grep -q "200"; then
    echo "✅ API Health Check: OK"
else
    echo "❌ API Health Check: Falha"
fi

echo ""

# Verificar logs de erro recentes
echo "🚨 Logs de Erro Recentes (últimas 10 linhas):"
docker-compose -f docker-compose.prod.yml logs --tail=10 2>/dev/null | grep -i error || echo "Nenhum erro encontrado"

echo ""

# Verificar espaço em disco
echo "💽 Espaço em Disco:"
df -h / | tail -1 | awk '{print "Usado: " $3 " / " $2 " (" $5 ")"}'

echo ""

# Verificar backup mais recente
echo "💾 Backup mais recente:"
if [ -d "backups" ]; then
    ls -lt backups/ | head -2 | tail -1 | awk '{print $9 " - " $6 " " $7 " " $8}' || echo "Nenhum backup encontrado"
else
    echo "Diretório de backup não existe"
fi

echo ""
echo "📋 Comandos úteis:"
echo "  Ver logs completos: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Reiniciar serviço: docker-compose -f docker-compose.prod.yml restart [serviço]"
echo "  Backup manual: ./backup.sh"
echo "  Deploy: ./deploy.sh"