# Regras de Desenvolvimento - Nossa Grana

## 🚫 Nunca Fazer
- Criar usuários com emails duplicados
- Importar modelos inexistentes (ex: GoalNotification)
- Executar migrate sem makemigrations
- Modificar banco em produção sem backup

## ✅ Sempre Fazer
- Testar login após mudanças no auth
- Verificar logs após deploy
- Usar filter().first() ao invés de get() para emails
- Validar dados antes de salvar no banco

## 🔧 Comandos Essenciais
```bash
# Verificar usuários duplicados
python manage.py shell --command="from django.contrib.auth.models import User; print(User.objects.values('email').annotate(count=models.Count('email')).filter(count__gt=1))"

# Limpar cache de sessões
python manage.py clearsessions

# Verificar integridade do banco
python manage.py check

# Backup do banco
copy db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3
```

## 📁 Estrutura de Arquivos
- `backend/` - Django API
- `demo-interface/` - Frontend demo
- `logs/` - Arquivos de log
- `*.md` - Documentação

## 🔐 Segurança
- Senhas sempre hasheadas
- Tokens JWT para autenticação
- CORS configurado para desenvolvimento
- Logs de segurança em `logs/security.log`