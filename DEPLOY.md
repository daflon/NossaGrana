# 🚀 Deploy em Produção - Nossa Grana

## **Arquitetura de Produção**

### **Containers Docker:**
- **Nginx**: Proxy reverso + SSL + Load balancer
- **Backend**: Django + Gunicorn (3 workers)
- **Frontend**: React build otimizado
- **PostgreSQL**: Banco de dados principal
- **Redis**: Cache + sessões
- **Celery**: Processamento assíncrono

## **Processo de Deploy**

### **1. Preparação:**
```bash
# Configurar variáveis de ambiente
cp .env.prod.example .env.prod
# Editar: domínio, senhas, chaves secretas

# Gerar certificados SSL
./generate-ssl.sh
```

### **2. Deploy Automatizado:**
```bash
./deploy.sh
```

**O script faz:**
- Para containers existentes
- Backup automático do banco
- Build das imagens Docker
- Executa migrações
- Coleta arquivos estáticos
- Cria superusuário admin
- Inicia todos os serviços

### **3. Monitoramento:**
```bash
./monitor.sh  # Status completo do sistema
```

## **URLs de Produção**

- **App**: `https://seudominio.com`
- **API**: `https://seudominio.com/api/`
- **Admin**: `https://seudominio.com/admin/`

## **Recursos de Produção**

### **Segurança:**
- HTTPS obrigatório (redirect automático)
- Headers de segurança (HSTS, XSS, etc.)
- Rate limiting (API: 10req/s, Login: 5req/min)
- Usuário não-root nos containers

### **Performance:**
- Gzip compression
- Cache de arquivos estáticos (1 ano)
- 3 workers Gunicorn
- Redis para cache/sessões

### **Backup & Monitoramento:**
- Backup automático antes do deploy
- Logs centralizados
- Health checks automáticos
- Monitoramento de recursos

## **Comandos Essenciais**

```bash
# Deploy completo
./deploy.sh

# Monitorar sistema
./monitor.sh

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Backup manual
./backup.sh

# Parar sistema
docker-compose -f docker-compose.prod.yml down
```

**Sistema pronto para produção com alta disponibilidade, segurança e monitoramento automatizado.**