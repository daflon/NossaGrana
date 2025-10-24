#!/bin/bash

echo "========================================"
echo " Nossa Grana - Sanitização para GitHub"
echo "========================================"
echo

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 não encontrado!"
    echo "Instale Python 3.9+ antes de continuar."
    exit 1
fi

echo "Python encontrado: $(python3 --version)"
echo

# Executar sanitização
echo "Executando sanitização..."
python3 sanitize_for_github.py

if [ $? -ne 0 ]; then
    echo
    echo "ERRO: Sanitização falhou!"
    echo "Verifique os logs acima para detalhes."
    exit 1
fi

echo
echo "========================================"
echo " Sanitização Concluída com Sucesso!"
echo "========================================"
echo
echo "Próximos passos:"
echo "1. Revisar arquivos .env.example criados"
echo "2. Testar aplicação após sanitização"
echo "3. Verificar se .gitignore está correto"
echo "4. Fazer upload para GitHub"
echo
echo "Backup salvo em: backup_pre_sanitization/"
echo

# Tornar o script executável
chmod +x "$0"