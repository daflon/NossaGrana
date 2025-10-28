#!/usr/bin/env python3
"""
Script de backup automatizado para produção
"""

import os
import sys
import subprocess
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class ProductionBackup:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configurações
        self.max_backups = 7  # Manter 7 backups
        self.compress = True
        
    def log(self, message):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def run_command(self, command, description=""):
        """Executa comando e retorna resultado"""
        self.log(f"Executando: {description}")
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            self.log(f"✅ {description} - Sucesso")
            return True, result.stdout
        else:
            self.log(f"❌ {description} - Erro: {result.stderr}")
            return False, result.stderr
    
    def backup_database(self):
        """Backup do PostgreSQL"""
        self.log("Iniciando backup do banco de dados...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"db_backup_{timestamp}.sql"
        
        # Comando de backup
        cmd = f"""docker-compose -f docker-compose.prod.yml exec -T db pg_dump \
            -U nossa_grana_user \
            -h localhost \
            -d nossa_grana_prod \
            --no-password \
            --verbose \
            --clean \
            --if-exists \
            --create > {backup_file}"""
        
        success, output = self.run_command(cmd, "Backup PostgreSQL")
        
        if success and backup_file.exists():
            # Comprimir backup
            if self.compress:
                compressed_file = f"{backup_file}.gz"
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove arquivo não comprimido
                backup_file.unlink()
                backup_file = Path(compressed_file)
                self.log(f"Backup comprimido: {backup_file}")
            
            # Verifica tamanho do backup
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            self.log(f"Tamanho do backup: {size_mb:.2f} MB")
            
            return backup_file
        
        return None
    
    def backup_media_files(self):
        """Backup dos arquivos de mídia"""
        self.log("Iniciando backup dos arquivos de mídia...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        media_backup = self.backup_dir / f"media_backup_{timestamp}.tar.gz"
        
        # Verifica se existe volume de mídia
        cmd = "docker volume ls | grep media"
        success, output = self.run_command(cmd, "Verificando volume de mídia")
        
        if success and "media" in output:
            # Backup do volume de mídia
            cmd = f"""docker run --rm \
                -v nossa_grana_media_volume:/data \
                -v {self.backup_dir.absolute()}:/backup \
                alpine tar czf /backup/{media_backup.name} -C /data ."""
            
            success, output = self.run_command(cmd, "Backup arquivos de mídia")
            
            if success and media_backup.exists():
                size_mb = media_backup.stat().st_size / (1024 * 1024)
                self.log(f"Backup de mídia criado: {size_mb:.2f} MB")
                return media_backup
        else:
            self.log("Nenhum arquivo de mídia encontrado")
        
        return None
    
    def backup_redis_data(self):
        """Backup dos dados do Redis"""
        self.log("Iniciando backup do Redis...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        redis_backup = self.backup_dir / f"redis_backup_{timestamp}.rdb"
        
        # Força salvamento do Redis
        cmd = "docker-compose -f docker-compose.prod.yml exec -T redis redis-cli BGSAVE"
        success, output = self.run_command(cmd, "Salvando dados Redis")
        
        if success:
            # Copia arquivo RDB
            cmd = f"""docker-compose -f docker-compose.prod.yml exec -T redis \
                cat /data/dump.rdb > {redis_backup}"""
            
            success, output = self.run_command(cmd, "Copiando backup Redis")
            
            if success and redis_backup.exists():
                size_mb = redis_backup.stat().st_size / (1024 * 1024)
                self.log(f"Backup Redis criado: {size_mb:.2f} MB")
                return redis_backup
        
        return None
    
    def cleanup_old_backups(self):
        """Remove backups antigos"""
        self.log("Limpando backups antigos...")
        
        # Lista todos os backups por tipo
        backup_types = ['db_backup_', 'media_backup_', 'redis_backup_']
        
        for backup_type in backup_types:
            backups = list(self.backup_dir.glob(f"{backup_type}*"))
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove backups excedentes
            if len(backups) > self.max_backups:
                for old_backup in backups[self.max_backups:]:
                    self.log(f"Removendo backup antigo: {old_backup.name}")
                    old_backup.unlink()
    
    def create_backup_manifest(self, backups):
        """Cria manifesto do backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        manifest_file = self.backup_dir / f"backup_manifest_{timestamp}.json"
        
        import json
        
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "backups": []
        }
        
        for backup_file in backups:
            if backup_file and backup_file.exists():
                manifest["backups"].append({
                    "file": backup_file.name,
                    "size_bytes": backup_file.stat().st_size,
                    "type": "database" if "db_backup" in backup_file.name else
                           "media" if "media_backup" in backup_file.name else "redis"
                })
        
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        self.log(f"Manifesto criado: {manifest_file.name}")
        return manifest_file
    
    def run_full_backup(self):
        """Executa backup completo"""
        self.log("🔄 Iniciando backup completo de produção")
        self.log("=" * 50)
        
        backups = []
        
        try:
            # Backup do banco de dados
            db_backup = self.backup_database()
            if db_backup:
                backups.append(db_backup)
            
            # Backup dos arquivos de mídia
            media_backup = self.backup_media_files()
            if media_backup:
                backups.append(media_backup)
            
            # Backup do Redis
            redis_backup = self.backup_redis_data()
            if redis_backup:
                backups.append(redis_backup)
            
            # Cria manifesto
            manifest = self.create_backup_manifest(backups)
            if manifest:
                backups.append(manifest)
            
            # Limpeza de backups antigos
            self.cleanup_old_backups()
            
            # Relatório final
            self.log("=" * 50)
            if backups:
                self.log("✅ Backup concluído com sucesso!")
                self.log(f"Arquivos criados: {len(backups)}")
                
                total_size = sum(b.stat().st_size for b in backups if b.exists())
                self.log(f"Tamanho total: {total_size / (1024*1024):.2f} MB")
            else:
                self.log("⚠️ Nenhum backup foi criado")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erro durante backup: {e}")
            return False

def main():
    """Função principal"""
    backup = ProductionBackup()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--database-only":
            backup.backup_database()
        elif sys.argv[1] == "--media-only":
            backup.backup_media_files()
        elif sys.argv[1] == "--redis-only":
            backup.backup_redis_data()
        elif sys.argv[1] == "--cleanup":
            backup.cleanup_old_backups()
        else:
            print("Uso: python backup_prod.py [--database-only|--media-only|--redis-only|--cleanup]")
    else:
        # Backup completo
        success = backup.run_full_backup()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()