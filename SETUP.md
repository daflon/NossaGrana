# Setup Nossa Grana

## Inicialização

### Backend (Django)
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 127.0.0.1:8001
```

### Frontend (Demo Interface)
```bash
cd demo-interface
node server.js
```

## Problemas Comuns

### 1. Erro 500 no Login
**Causa**: Usuários duplicados com mesmo email
**Solução**:
```bash
python manage.py shell --command="from django.contrib.auth.models import User; User.objects.filter(email='EMAIL_DUPLICADO').exclude(id=ID_MANTER).delete()"
```

### 2. Erro de Importação (GoalNotification)
**Causa**: Referências a modelos inexistentes
**Solução**: Remover importações de `GoalNotification` dos arquivos:
- `goals/admin.py`
- `goals/serializers.py`

### 3. Erro 404 na Raiz
**Causa**: URL raiz não configurada
**Solução**: Já corrigido em `nossa_grana/urls.py`

## URLs Principais
- Backend: http://127.0.0.1:8001/
- Admin: http://127.0.0.1:8001/admin/
- Frontend: http://localhost:3000/

## Credenciais Admin
- Username: admin
- Email: admin@test.com
- Password: (definida no admin)