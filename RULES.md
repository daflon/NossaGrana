# Regras de Desenvolvimento - Nossa Grana

## 🎉 Status Atual: Sistema 100% Funcional

**✅ SISTEMA TESTADO E APROVADO**
- Testes automatizados: 5/5 aprovados
- Backend: 100% funcional
- Frontend: 100% funcional
- Compatibilidade Windows: 100%

## 🚫 Nunca Fazer
- Criar usuários com emails duplicados
- Importar modelos inexistentes (ex: GoalNotification)
- Executar migrate sem makemigrations
- Modificar banco em produção sem backup
- Usar emojis em scripts Python (problemas no Windows)
- Conflitos de nomes em imports (ex: transaction vs db_transaction)

## ✅ Sempre Fazer
- Executar `python run_all_tests.py` antes de deploy
- Testar login após mudanças no auth
- Verificar logs após deploy
- Usar filter().first() ao invés de get() para emails
- Validar dados antes de salvar no banco
- Testar transferências entre contas
- Verificar compatibilidade Windows

## 🔧 Comandos Essenciais

### **Testes e Validação**
```bash
# Executar todos os testes (PRINCIPAL)
python run_all_tests.py

# Teste rápido do backend
cd backend
python test_simple.py

# Verificar migrações
cd backend
python manage.py showmigrations

# Verificar integridade do sistema
cd backend
python manage.py check
```

### **Iniciar Serviços**
```bash
# Backend (Terminal 1)
cd backend
python manage.py runserver 8000

# Demo Interface (Terminal 2)
cd demo-interface
node server.js

# Frontend React (Terminal 3 - opcional)
cd frontend
npm start
```

### **Manutenção**
```bash
# Backup do banco
copy backend\db.sqlite3 backup_db_%date%.sqlite3

# Limpar cache de sessões
cd backend
python manage.py clearsessions

# Verificar usuários duplicados
cd backend
python manage.py shell --command="from django.contrib.auth.models import User; print(User.objects.values('email').annotate(count=models.Count('email')).filter(count__gt=1))"
```

## 📁 Estrutura de Arquivos
- `backend/` - Django API (100% funcional)
- `demo-interface/` - Frontend demo (100% funcional - porta 3002)
- `frontend/` - React.js (estrutura completa - porta 3000)
- `logs/` - Arquivos de log
- `*.md` - Documentação atualizada
- `run_all_tests.py` - Script de testes principal
- `test_system.py` - Testes do sistema

## 🔐 Segurança
- Senhas sempre hasheadas
- Tokens JWT para autenticação
- CORS configurado para desenvolvimento
- Logs de segurança em `logs/security.log`
- Transferências com validação de saldo
- Middleware de segurança ativo

## 🎯 URLs de Acesso
- **Demo Interface**: http://localhost:3002 (Principal)
- **Backend API**: http://localhost:8000/api
- **Admin Django**: http://localhost:8000/admin
- **Frontend React**: http://localhost:3000 (Opcional)

## 📊 Métricas de Sucesso Atingidas
- ✅ Testes automatizados: 100% aprovados
- ✅ Backend: Todas as APIs funcionando
- ✅ Frontend: Interface completa
- ✅ Transferências: Corrigidas e testadas
- ✅ Compatibilidade: Windows 100%
- ✅ Banco de dados: Configurado e atualizado