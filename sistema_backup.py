"""
Sistema de Backups Automáticos - Sistema Montero
=================================================
Versión: 1.0
Fecha: 2 de noviembre de 2025
Plataforma: Windows

Características:
- Backup automático de base de datos SQLite
- Backup de archivos de configuración críticos
- Compresión ZIP para ahorrar espacio
- Rotación automática (elimina backups antiguos)
- Sistema de logging completo
- Verificación de integridad
- Compatible con Windows Task Scheduler

Uso:
    python sistema_backup.py
    python sistema_backup.py --full  # Backup completo con todos los archivos
"""

import os
import sys
import shutil
import zipfile
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple


class SistemaBackup:
    """
    Sistema profesional de backups automáticos para Windows.
    
    Atributos:
        dir_proyecto: Directorio raíz del proyecto
        dir_backups: Directorio donde se guardan los backups
        dias_retencion: Días que se mantienen los backups
        archivos_criticos: Lista de archivos que siempre se respaldan
    """
    
    def __init__(self, 
                 dir_proyecto: str = None, 
                 dir_backups: str = None,
                 dias_retencion: int = 30):
        """
        Inicializa el sistema de backups.
        
        Args:
            dir_proyecto: Ruta del proyecto (por defecto: directorio actual)
            dir_backups: Directorio de backups (por defecto: ./backups)
            dias_retencion: Días para mantener backups antiguos
        """
        # Configurar directorios
        if dir_proyecto is None:
            self.dir_proyecto = Path(__file__).parent.absolute()
        else:
            self.dir_proyecto = Path(dir_proyecto).absolute()
            
        if dir_backups is None:
            self.dir_backups = self.dir_proyecto / "backups"
        else:
            self.dir_backups = Path(dir_backups).absolute()
            
        self.dias_retencion = dias_retencion
        
        # Crear directorio de backups si no existe
        self.dir_backups.mkdir(exist_ok=True)
        
        # Archivos críticos que siempre se respaldan
        self.archivos_criticos = [
            "mi_sistema.db",
            "_env",
            "encryption.py",
            "logger.py",
            "auth.py",
            "app.py",
            "requirements.txt",
            "alembic.ini",
        ]
        
        # Directorios críticos
        self.directorios_criticos = [
            "migrations",
            "routes",
            "templates",
            "static",
        ]
        
        # Configurar logging
        self._configurar_logging()
        
    def _configurar_logging(self):
        """Configura el sistema de logging para backups."""
        log_file = self.dir_backups / "backup.log"
        
        # Formato del log
        formato = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formato)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formato)
        
        # Configurar logger
        self.logger = logging.getLogger('SistemaBackup')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def generar_nombre_backup(self) -> str:
        """
        Genera un nombre único para el archivo de backup.
        
        Returns:
            Nombre del archivo en formato: backup_YYYYMMDD_HHMMSS.zip
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{timestamp}.zip"
    
    def obtener_archivos_backup(self, backup_completo: bool = False) -> List[Tuple[Path, str]]:
        """
        Obtiene la lista de archivos a respaldar.
        
        Args:
            backup_completo: Si es True, incluye todos los archivos del proyecto
            
        Returns:
            Lista de tuplas (ruta_completa, ruta_relativa)
        """
        archivos = []
        
        if backup_completo:
            # Backup completo: incluir todo excepto backups y __pycache__
            for archivo in self.dir_proyecto.rglob('*'):
                # Excluir directorios especiales
                partes = archivo.parts
                if any(excluir in partes for excluir in ['backups', '__pycache__', '.git', 'venv', 'env']):
                    continue
                    
                if archivo.is_file():
                    ruta_relativa = archivo.relative_to(self.dir_proyecto)
                    archivos.append((archivo, str(ruta_relativa)))
        else:
            # Backup estándar: solo archivos críticos
            # Archivos individuales
            for nombre_archivo in self.archivos_criticos:
                archivo = self.dir_proyecto / nombre_archivo
                if archivo.exists():
                    archivos.append((archivo, nombre_archivo))
                    
            # Directorios completos
            for nombre_dir in self.directorios_criticos:
                dir_path = self.dir_proyecto / nombre_dir
                if dir_path.exists() and dir_path.is_dir():
                    for archivo in dir_path.rglob('*'):
                        if archivo.is_file() and '__pycache__' not in str(archivo):
                            ruta_relativa = archivo.relative_to(self.dir_proyecto)
                            archivos.append((archivo, str(ruta_relativa)))
        
        return archivos
    
    def crear_backup(self, backup_completo: bool = False) -> bool:
        """
        Crea un backup comprimido del sistema.
        
        Args:
            backup_completo: Si es True, respalda todo el proyecto
            
        Returns:
            True si el backup fue exitoso, False en caso contrario
        """
        try:
            self.logger.info("="*60)
            self.logger.info(f"Iniciando backup {'completo' if backup_completo else 'estándar'}...")
            
            # Generar nombre del backup
            nombre_backup = self.generar_nombre_backup()
            ruta_backup = self.dir_backups / nombre_backup
            
            # Obtener archivos a respaldar
            archivos = self.obtener_archivos_backup(backup_completo)
            
            if not archivos:
                self.logger.warning("No se encontraron archivos para respaldar")
                return False
            
            self.logger.info(f"Archivos a respaldar: {len(archivos)}")
            
            # Crear archivo ZIP
            with zipfile.ZipFile(ruta_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for archivo_origen, archivo_destino in archivos:
                    try:
                        zipf.write(archivo_origen, archivo_destino)
                        self.logger.debug(f"✓ {archivo_destino}")
                    except Exception as e:
                        self.logger.error(f"✗ Error al respaldar {archivo_destino}: {e}")
            
            # Verificar integridad del backup
            if self._verificar_backup(ruta_backup):
                tamano = ruta_backup.stat().st_size
                tamano_mb = tamano / (1024 * 1024)
                
                self.logger.info(f"✓ Backup creado exitosamente: {nombre_backup}")
                self.logger.info(f"  Tamaño: {tamano_mb:.2f} MB")
                self.logger.info(f"  Ubicación: {ruta_backup}")
                self.logger.info(f"  Archivos: {len(archivos)}")
                
                return True
            else:
                self.logger.error("✗ Verificación de integridad falló")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Error durante el backup: {e}")
            return False
        finally:
            self.logger.info("="*60)
    
    def _verificar_backup(self, ruta_backup: Path) -> bool:
        """
        Verifica la integridad de un archivo de backup.
        
        Args:
            ruta_backup: Ruta al archivo ZIP
            
        Returns:
            True si el backup es válido, False en caso contrario
        """
        try:
            with zipfile.ZipFile(ruta_backup, 'r') as zipf:
                # Verificar integridad del ZIP
                resultado = zipf.testzip()
                if resultado is not None:
                    self.logger.error(f"Archivo corrupto detectado: {resultado}")
                    return False
                
                # Verificar que contiene archivos
                if len(zipf.namelist()) == 0:
                    self.logger.error("El backup está vacío")
                    return False
                    
                return True
        except Exception as e:
            self.logger.error(f"Error al verificar backup: {e}")
            return False
    
    def limpiar_backups_antiguos(self) -> int:
        """
        Elimina backups más antiguos que el período de retención.
        
        Returns:
            Número de backups eliminados
        """
        try:
            self.logger.info("Limpiando backups antiguos...")
            
            # Calcular fecha límite
            fecha_limite = datetime.now() - timedelta(days=self.dias_retencion)
            
            eliminados = 0
            backups = list(self.dir_backups.glob("backup_*.zip"))
            
            for backup in backups:
                # Obtener fecha del backup desde el nombre del archivo
                try:
                    # backup_YYYYMMDD_HHMMSS.zip
                    nombre = backup.stem
                    fecha_str = nombre.split('_')[1]
                    fecha_backup = datetime.strptime(fecha_str, "%Y%m%d")
                    
                    if fecha_backup < fecha_limite:
                        backup.unlink()
                        eliminados += 1
                        self.logger.info(f"  ✓ Eliminado: {backup.name}")
                        
                except Exception as e:
                    self.logger.warning(f"  ✗ No se pudo procesar {backup.name}: {e}")
                    
            if eliminados > 0:
                self.logger.info(f"✓ {eliminados} backup(s) antiguo(s) eliminado(s)")
            else:
                self.logger.info("No hay backups antiguos para eliminar")
                
            return eliminados
            
        except Exception as e:
            self.logger.error(f"Error al limpiar backups: {e}")
            return 0
    
    def listar_backups(self) -> List[dict]:
        """
        Lista todos los backups disponibles con su información.
        
        Returns:
            Lista de diccionarios con información de cada backup
        """
        backups = []
        
        for archivo in sorted(self.dir_backups.glob("backup_*.zip"), reverse=True):
            try:
                tamano = archivo.stat().st_size
                tamano_mb = tamano / (1024 * 1024)
                fecha_mod = datetime.fromtimestamp(archivo.stat().st_mtime)
                
                backups.append({
                    'nombre': archivo.name,
                    'ruta': archivo,
                    'tamano_mb': tamano_mb,
                    'fecha': fecha_mod
                })
            except Exception as e:
                self.logger.warning(f"Error al procesar {archivo.name}: {e}")
                
        return backups
    
    def mostrar_backups(self):
        """Muestra en consola todos los backups disponibles."""
        backups = self.listar_backups()
        
        if not backups:
            print("\n❌ No hay backups disponibles\n")
            return
            
        print("\n" + "="*70)
        print(f"{'BACKUPS DISPONIBLES':^70}")
        print("="*70)
        print(f"{'Nombre':<30} {'Tamaño':<15} {'Fecha':<25}")
        print("-"*70)
        
        for backup in backups:
            print(f"{backup['nombre']:<30} "
                  f"{backup['tamano_mb']:>6.2f} MB     "
                  f"{backup['fecha'].strftime('%Y-%m-%d %H:%M:%S')}")
                  
        print("="*70)
        print(f"Total: {len(backups)} backup(s)")
        print(f"Directorio: {self.dir_backups}\n")


class RestauradorBackup:
    """
    Clase para restaurar backups del sistema.
    """
    
    def __init__(self, dir_backups: str = None):
        """
        Inicializa el restaurador.
        
        Args:
            dir_backups: Directorio donde están los backups
        """
        if dir_backups is None:
            self.dir_backups = Path(__file__).parent.absolute() / "backups"
        else:
            self.dir_backups = Path(dir_backups).absolute()
            
        # Configurar logging
        self.logger = logging.getLogger('RestauradorBackup')
        
    def listar_backups(self) -> List[Path]:
        """Lista todos los backups disponibles."""
        return sorted(self.dir_backups.glob("backup_*.zip"), reverse=True)
    
    def restaurar_backup(self, 
                        archivo_backup: str, 
                        dir_destino: str = None,
                        sobrescribir: bool = False) -> bool:
        """
        Restaura un backup específico.
        
        Args:
            archivo_backup: Nombre o ruta del archivo de backup
            dir_destino: Directorio donde restaurar (por defecto: directorio del script)
            sobrescribir: Si True, sobrescribe archivos existentes
            
        Returns:
            True si la restauración fue exitosa
        """
        try:
            # Determinar ruta del backup
            if Path(archivo_backup).exists():
                ruta_backup = Path(archivo_backup)
            else:
                ruta_backup = self.dir_backups / archivo_backup
                
            if not ruta_backup.exists():
                self.logger.error(f"Backup no encontrado: {archivo_backup}")
                return False
            
            # Determinar directorio destino
            if dir_destino is None:
                dir_destino = Path(__file__).parent.absolute()
            else:
                dir_destino = Path(dir_destino).absolute()
                
            self.logger.info("="*60)
            self.logger.info(f"Restaurando backup: {ruta_backup.name}")
            self.logger.info(f"Destino: {dir_destino}")
            
            # Verificar integridad
            with zipfile.ZipFile(ruta_backup, 'r') as zipf:
                if zipf.testzip() is not None:
                    self.logger.error("El archivo de backup está corrupto")
                    return False
                
                # Listar archivos
                archivos = zipf.namelist()
                self.logger.info(f"Archivos a restaurar: {len(archivos)}")
                
                # Restaurar archivos
                restaurados = 0
                omitidos = 0
                
                for archivo in archivos:
                    ruta_destino = dir_destino / archivo
                    
                    # Verificar si existe
                    if ruta_destino.exists() and not sobrescribir:
                        self.logger.warning(f"⚠ Omitido (existe): {archivo}")
                        omitidos += 1
                        continue
                    
                    # Crear directorio si no existe
                    ruta_destino.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Extraer archivo
                    with zipf.open(archivo) as source, open(ruta_destino, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    
                    restaurados += 1
                    self.logger.debug(f"✓ Restaurado: {archivo}")
                
                self.logger.info(f"✓ Restauración completada")
                self.logger.info(f"  Archivos restaurados: {restaurados}")
                self.logger.info(f"  Archivos omitidos: {omitidos}")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error durante la restauración: {e}")
            return False
        finally:
            self.logger.info("="*60)


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description='Sistema de Backups Automáticos - Sistema Montero',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python sistema_backup.py                    # Backup estándar
  python sistema_backup.py --full             # Backup completo
  python sistema_backup.py --list             # Listar backups
  python sistema_backup.py --clean            # Limpiar backups antiguos
  python sistema_backup.py --restore latest   # Restaurar último backup
        """
    )
    
    parser.add_argument('--full', action='store_true',
                       help='Crear backup completo del proyecto')
    parser.add_argument('--list', action='store_true',
                       help='Listar backups disponibles')
    parser.add_argument('--clean', action='store_true',
                       help='Limpiar backups antiguos')
    parser.add_argument('--restore', metavar='BACKUP',
                       help='Restaurar un backup específico (nombre o "latest")')
    parser.add_argument('--dir-backups', metavar='DIR',
                       help='Directorio personalizado para backups')
    parser.add_argument('--retention', type=int, default=30,
                       help='Días de retención de backups (default: 30)')
    
    args = parser.parse_args()
    
    # Crear sistema de backup
    sistema = SistemaBackup(
        dir_backups=args.dir_backups,
        dias_retencion=args.retention
    )
    
    # Ejecutar acción solicitada
    if args.list:
        sistema.mostrar_backups()
        
    elif args.clean:
        sistema.limpiar_backups_antiguos()
        
    elif args.restore:
        restaurador = RestauradorBackup(dir_backups=args.dir_backups)
        
        if args.restore.lower() == 'latest':
            backups = restaurador.listar_backups()
            if backups:
                archivo_backup = backups[0]
            else:
                print("❌ No hay backups disponibles")
                return 1
        else:
            archivo_backup = args.restore
            
        restaurador.restaurar_backup(archivo_backup, sobrescribir=False)
        
    else:
        # Crear backup
        exito = sistema.crear_backup(backup_completo=args.full)
        
        if exito:
            # Limpiar backups antiguos automáticamente
            sistema.limpiar_backups_antiguos()
            return 0
        else:
            return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
