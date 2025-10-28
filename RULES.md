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

## 🔍 Troubleshooting Rápido

### Problemas Comuns e Soluções
```bash
# Erro de migração
cd backend
python manage.py migrate --fake-initial

# Porta ocupada
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Cache corrompido
cd backend
python manage.py collectstatic --clear

# Sessões inválidas
cd backend
python manage.py clearsessions
```

### Logs de Debug
- Backend: `logs/backend.log`
- Segurança: `logs/security.log`
- Transferências: `logs/transactions.log`
- Sistema: `logs/system.log`

## ⚡ Performance e Monitoramento

### Comandos de Monitoramento
```bash
# Verificar performance do banco
cd backend
python manage.py dbshell --command=".timer on; .stats on;"

# Monitorar uso de memória
tasklist | findstr python

# Verificar conexões ativas
netstat -an | findstr :8000
```

### Otimizações Aplicadas
- Cache de sessões configurado
- Queries otimizadas com select_related
- Middleware de compressão ativo
- Static files servidos eficientemente

## 🔄 Workflow de Desenvolvimento

### Antes de Qualquer Mudança
1. `python run_all_tests.py` - Verificar estado atual
2. `copy backend\db.sqlite3 backup_db.sqlite3` - Backup
3. Fazer mudanças incrementais
4. Testar cada mudança isoladamente

### Após Mudanças
1. `python run_all_tests.py` - Validar tudo
2. Testar manualmente as funcionalidades afetadas
3. Verificar logs para erros
4. Documentar mudanças significativas

### Deploy Checklist
- [ ] Todos os testes passando
- [ ] Backup do banco realizado
- [ ] Logs verificados
- [ ] Performance testada
- [ ] Funcionalidades críticas testadas

## 🎯 Próximas Melhorias Sugeridas
- Implementar cache Redis (opcional)
- Adicionar métricas de performance
- Configurar CI/CD pipeline
- Implementar testes de carga
- Adicionar monitoramento de saúde

## 📝 Notas de Versão
- **v1.0**: Sistema base funcional
- **v1.1**: Correções de transferências
- **v1.2**: Otimizações de performance
- **v1.3**: Melhorias de segurança
- **Atual**: Sistema estável e testado