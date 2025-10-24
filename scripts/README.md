# Scripts de Certificados SSL - NossaGrana

Este diretório contém scripts para gerar e gerenciar certificados SSL para o projeto NossaGrana.

## Scripts Disponíveis

### 1. `generate_ssl_certificates.py` (Python)
Script Python avançado com múltiplas opções.

**Uso:**
```bash
python scripts/generate_ssl_certificates.py --domain localhost --days 365
```

**Opções:**
- `--domain`: Domínio principal (padrão: localhost)
- `--ssl-dir`: Diretório SSL (padrão: nginx/ssl)
- `--key-size`: Tamanho da chave RSA (padrão: 2048)
- `--days`: Validade em dias (padrão: 365)

### 2. `ssl_manager.bat` (Windows)
Script batch para Windows com interface amigável.

**Uso:**
```cmd
scripts\ssl_manager.bat
```

### 3. `../generate-ssl.sh` (Bash)
Script bash melhorado na raiz do projeto.

**Uso:**
```bash
./generate-ssl.sh
```

## Arquivos Gerados

Todos os scripts geram os seguintes arquivos em `nginx/ssl/`:

- `private.key` - Chave privada RSA (600 permissions)
- `certificate.crt` - Certificado auto-assinado (644 permissions)
- `dhparam.pem` - Parâmetros Diffie-Hellman
- `nginx_ssl.conf` - Configuração SSL para Nginx
- `openssl.conf` - Configuração OpenSSL com SAN

## Requisitos

- **OpenSSL** instalado no sistema
- **Windows**: Chocolatey (`choco install openssl`) ou download manual
- **Linux/macOS**: `sudo apt install openssl` ou `brew install openssl`

## Configuração Nginx

Inclua a configuração SSL no seu nginx.conf:

```nginx
server {
    listen 443 ssl http2;
    server_name localhost;
    
    include nginx/ssl/nginx_ssl.conf;
    
    location / {
        proxy_pass http://backend:8000;
    }
}
```

## Produção

Para produção, use certificados válidos:

### Let's Encrypt (Gratuito)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seudominio.com
```

### Renovação Automática
```bash
sudo crontab -e
# Adicionar linha:
0 12 * * * /usr/bin/certbot renew --quiet
```

## Segurança

- Certificados auto-assinados são apenas para desenvolvimento
- Mantenha chaves privadas seguras (permissions 600)
- Use HTTPS em produção
- Configure HSTS headers
- Monitore expiração de certificados

## Troubleshooting

### OpenSSL não encontrado
- Windows: Instale via Chocolatey ou download manual
- Linux: `sudo apt install openssl`
- macOS: `brew install openssl`

### Erro de permissões
```bash
chmod 600 nginx/ssl/private.key
chmod 644 nginx/ssl/certificate.crt
```

### Navegador não aceita certificado
- Adicione exceção de segurança
- Verifique SAN domains
- Use certificado válido em produção