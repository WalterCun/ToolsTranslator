# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" translator/tools/docker_tools.py """
import subprocess
import logging
import json
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Iterator
from pathlib import Path
import tempfile
import os
from colorlog import basicConfig

basicConfig(
    level=logging.INFO,
    format='%(log_color)s[%(asctime)s] [%(levelname)s] [%(name)s] -> %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'black,bg_cyan',
    }

)
log = logging.getLogger(__name__)


def is_docker_running():
    log.warning("*** Check if Docker is running ***")
    try:
        log.critical("Execute: docker info")
        result = subprocess.run(["docker", "info"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log.info(f'Result: {result}')
        result = result.returncode == 0
        log.info(f'Docker Running: {result}')
        return result
    except (subprocess.CalledProcessError, FileNotFoundError):
        log.error("Docker not running")
        return False


def is_docker_installed():
    log.warning("*** Check if Docker is installed ***")
    try:
        log.critical("Execute: docker --version")
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log.info("Docker installed")
        return True
    except FileNotFoundError:
        log.error("Docker not installed")
        return False
    except subprocess.CalledProcessError:
        log.error("Docker installed but not running")
        return False


# ---------------------------------------------------------------------------------------------------------------------

class ContainerStatus(Enum):
    """Estados posibles del contenedor"""
    RUNNING = "running"
    STOPPED = "stopped"
    NOT_FOUND = "not_found"
    DOCKER_NOT_RUNNING = "docker_not_running"
    ERROR = "error"


def get_libretranslate_status() -> Dict[str, Any]:
    """
    Obtiene el estado completo de LibreTranslate y las acciones recomendadas.
    
    :return: Diccionario con estado y acciones recomendadas
    """
    log.warning("*** Get LibreTranslate Status ***")
    status_info = {
        'status': None,
        'action_needed': None,
        'containers_found': [],
        'running_containers': [],
        'stopped_containers': [],
        'message': '',
        'can_start': False,
        'can_install': False
    }
    log.info(f'Status Info Star: {status_info}')

    if not is_docker_installed():
        log.info("Docker no está instalado.")
        # noinspection PyTypeChecker
        status_info.update({
            'status': ContainerStatus.ERROR,
            'action_needed': 'install_docker',
            'message': 'Docker no está instalado en el sistema',
            'can_install': True
        })
        log.info(f'Status Docker Installed: {status_info}')
        return status_info
    log.info("Docker está instalado.")

    if not is_docker_running():
        log.warning("Docker no está corriendo.")
        # noinspection PyTypeChecker
        status_info.update({
            'status': ContainerStatus.DOCKER_NOT_RUNNING,
            'action_needed': 'start_docker',
            'message': 'Docker está instalado pero no está ejecutándose',
        })
        log.info(f'Status Docker Running: {status_info}')
        return status_info
    log.info("Docker está corriendo.")

    # Buscar todos los contenedores LibreTranslate
    log.info("Buscando todos los contenedores LibreTranslate...")
    all_containers = find_all_libretranslate_containers()
    log.info(f'All Containers: {all_containers}')
    running_containers = [c for c in all_containers if c['state'].lower() in ['running', 'up']]
    log.info(f'Running Containers: {running_containers}')
    stopped_containers = [c for c in all_containers if c['state'].lower() in ['exited', 'stopped', 'created']]
    log.info(f'Stopped Containers: {stopped_containers}')

    status_info.update({
        'containers_found': all_containers,
        'running_containers': running_containers,
        'stopped_containers': stopped_containers
    })
    log.info(f'Status Info Update: {status_info}')

    if running_containers:
        # noinspection PyTypeChecker
        status_info.update({
            'status': ContainerStatus.RUNNING,
            'action_needed': None,
            'message': f'LibreTranslate está ejecutándose. {len(running_containers)} contenedor(es) activo(s)'
        })
        log.info(f'Status Info Running Containers: {status_info}')

    elif stopped_containers:
        # noinspection PyTypeChecker
        status_info.update({
            'status': ContainerStatus.STOPPED,
            'action_needed': 'start_container',
            'message': f'LibreTranslate está instalado pero detenido. {len(stopped_containers)} contenedor(es) disponible(s)',
            'can_start': True
        })
        log.info(f'Status Info Stopped Containers: {status_info}')

    else:
        # noinspection PyTypeChecker
        status_info.update({
            'status': ContainerStatus.NOT_FOUND,
            'action_needed': 'install_libretranslate',
            'message': 'No se encontraron contenedores LibreTranslate instalados',
            'can_install': True
        })
        log.info(f'Status Info Not Found Containers: {status_info}')

    return status_info


def find_all_libretranslate_containers() -> List[Dict]:
    """
    Encuentra todos los contenedores LibreTranslate con diferentes filtros.
    
    :return: Lista de contenedores encontrados
    """
    containers = []

    if not is_docker_running():
        return containers

    # Diferentes patrones de búsqueda para LibreTranslate
    search_patterns = [
        "libretranslate/libretranslate",
        "libretranslate-libretranslate",
        "libretranslate-libretranslate-cud"
    ]

    for pattern in search_patterns:
        try:
            result = subprocess.run([
                "docker", "ps", "-a", "--filter", f"ancestor={pattern}",
                "--format", "{{json .}}"
            ], capture_output=True, text=True, check=True)

            if result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    try:
                        container_data = json.loads(line)
                        container_info = {
                            'id': container_data.get('ID', '')[:12],
                            'name': container_data.get('Names', ''),
                            'status': container_data.get('Status', ''),
                            'ports': container_data.get('Ports', ''),
                            'state': container_data.get('State', 'unknown'),
                            'image': container_data.get('Image', ''),
                            'ancestor_pattern': pattern
                        }

                        # Evitar duplicados
                        if not any(c['id'] == container_info['id'] for c in containers):
                            containers.append(container_info)

                    except json.JSONDecodeError:
                        continue

        except subprocess.CalledProcessError as e:
            log.error(f"Error al buscar contenedores con patrón {pattern}: {e}")

    # También buscar por nombre
    try:
        result = subprocess.run([
            "docker", "ps", "-a", "--filter", "name=libretranslate",
            "--format", "{{json .}}"
        ], capture_output=True, text=True, check=True)

        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                try:
                    container_data = json.loads(line)
                    container_info = {
                        'id': container_data.get('ID', '')[:12],
                        'name': container_data.get('Names', ''),
                        'status': container_data.get('Status', ''),
                        'ports': container_data.get('Ports', ''),
                        'state': container_data.get('State', 'unknown'),
                        'image': container_data.get('Image', ''),
                        'found_by': 'name_filter'
                    }

                    # Evitar duplicados
                    if not any(c['id'] == container_info['id'] for c in containers):
                        containers.append(container_info)

                except json.JSONDecodeError:
                    continue

    except subprocess.CalledProcessError as e:
        log.error(f"Error al buscar contenedores por nombre: {e}")

    return containers


def start_libretranslate_container(container_id: str = None, status_data: dict = None) -> Dict:
    """
    Inicia un contenedor LibreTranslate específico o el primero disponible.
    
    :param container_id: ID específico del contenedor a iniciar
    :param status_data: Info de estado de LibreTranslate
    :return: Resultado de la operación
    """
    log.warning(f'*** Start LibreTranslate Container ***')
    log.info(f'Container ID: {container_id}')
    log.info(f'Status Data: {status_data}')

    result = {'success': False, 'message': '', 'container_id': None}
    log.info(f'Start LibreTranslate Container Result: {result}')

    # Si no se especifica un contenedor, buscar uno detenido
    if not container_id:
        log.info(f'Not Container ID Specified, looking for stopped containers...')
        status = get_libretranslate_status() if status_data is None else status_data
        if status['stopped_containers']:
            container_id = status['stopped_containers'][0]['id']
            log.info(f'Found stopped container {container_id}')
        else:
            result['message'] = 'No se encontraron contenedores detenidos para iniciar'
            return result

    try:
        log.critical(f'Executed: docker start {container_id}')
        subprocess.run([
            "docker", "start", container_id
        ], capture_output=True, text=True, check=True)

        result.update({
            'success': True,
            'message': f'Contenedor {container_id} iniciado correctamente',
            'container_id': container_id
        })
        log.info(f'Start LibreTranslate Container Result: {result}')

    except subprocess.CalledProcessError as e:
        result['message'] = f'Error al iniciar contenedor {container_id}: {e.stderr}'
        log.info(f"Error al iniciar contenedor: {e}")

    return result


# def get_libretranslate_container_info(container_name: str = "libretranslate") -> Dict:
#     """
#     Obtiene información detallada del contenedor de LibreTranslate.
#
#     :param container_name: Nombre del contenedor
#     :return: Diccionario con información del contenedor
#     """
#     info = {
#         'running': False,
#         'container_id': None,
#         'ports': [],
#         'status': None,
#         'image': None,
#         'error': ''
#     }
#
#     if not is_docker_running():
#         info['error'] = 'Docker no está ejecutándose'
#         return info
#
#     try:
#         # Obtener información del contenedor
#         result = subprocess.run([
#             "docker", "ps", "--filter", f"name={container_name}",
#             "--format", "{{json .}}"
#         ], capture_output=True, text=True, check=True)
#
#         if result.stdout.strip():
#             container_data = json.loads(result.stdout.strip().split('\n')[0])
#             info.update({
#                 'running': True,
#                 'container_id': container_data.get('ID', '')[:12],
#                 'ports': container_data.get('Ports', ''),
#                 'status': container_data.get('Status', ''),
#                 'image': container_data.get('Image', ''),
#                 'names': container_data.get('Names', '')
#             })
#
#     except (subprocess.CalledProcessError, json.JSONDecodeError, IndexError) as e:
#         log.error(f"Error al obtener información del contenedor: {e}")
#         info['error'] = str(e)
#
#     return info


# ---------------------------------------------------------------------------------------------------------------------

def clone_libretranslate_repo(temp_dir: Path) -> Dict[str, Any]:
    """
    Clona el repositorio de LibreTranslate en un directorio temporal.
    
    :param temp_dir: Directorio temporal donde clonar
    :return: Resultado de la operación
    """
    log.warning(f"*** Clonando repositorio LibreTranslate en {temp_dir} ***")

    result = {'success': False, 'message': '', 'repo_path': None}

    repo_url = "https://github.com/LibreTranslate/LibreTranslate.git"
    repo_path = temp_dir

    try:
        log.info(f"Clonando repositorio LibreTranslate en {repo_path}")

        # Verificar si git está disponible
        log.info('Verificando git...')
        subprocess.run(["git", "--version"], check=True, capture_output=True)

        # Clonar el repositorio
        log.critical(f"Executed: git clone {repo_url} {repo_path}")
        subprocess.run([
            "git", "clone", repo_url, str(repo_path)
        ], check=True, capture_output=True, text=True)

        result.update({
            'success': True,
            'message': f'Repositorio clonado correctamente en {repo_path}',
            'repo_path': repo_path
        })
        log.info(f"Result Clone Repo: {result}")

    except FileNotFoundError:
        msg = 'Git no está instalado en el sistema'
        result['message'] = msg
        log.error(msg)
    except subprocess.CalledProcessError as e:
        result['message'] = f'Error al clonar repositorio: {e.stderr}'
        log.error(f"Error clonando repositorio: {e}")

    return result


class StreamTimer:
    """Clase para manejar el contador de tiempo durante el streaming"""

    def __init__(self, update_interval: int = 1):
        self.start_time = None
        self.last_output_time = None
        self.update_interval = update_interval
        self.running = False
        self.timer_thread = None
        self.lock = threading.Lock()

    def start(self):
        """Inicia el contador"""
        with self.lock:
            self.start_time = datetime.now()
            self.last_output_time = self.start_time
            self.running = True

        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()

    def stop(self):
        """Detiene el contador"""
        with self.lock:
            self.running = False

    def update_activity(self):
        """Actualiza el timestamp de la última actividad"""
        with self.lock:
            self.last_output_time = datetime.now()

    def _timer_loop(self):
        """Loop del contador en thread separado"""
        while self.running:
            time.sleep(self.update_interval)

            if not self.running:
                break

            with self.lock:
                current_time = datetime.now()
                total_elapsed = current_time - self.start_time
                since_last_output = current_time - self.last_output_time

            # Mostrar contador solo si han pasado más de 3 segundos sin output
            if since_last_output.total_seconds() > 3:
                self._print_timer_info(total_elapsed, since_last_output)

    def _print_timer_info(self, total_elapsed: timedelta, since_last: timedelta):
        """Imprime la información del timer"""
        total_str = self._format_duration(total_elapsed)
        since_str = self._format_duration(since_last)

        # Usar \r para sobrescribir la línea
        print(f"\r⏳ Tiempo total: {total_str} | Sin output: {since_str} | Construyendo...",
              end='', flush=True)

    @staticmethod
    def _format_duration(duration: timedelta) -> str:
        """Formatea la duración en formato legible"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


def stream_command_output(command: list, cwd: str = None) -> Iterator[str]:
    """
    Ejecuta un comando y devuelve la salida línea por línea en tiempo real.

    :param command: Lista con el comando a ejecutar
    :param cwd: Directorio de trabajo
    :yield: Líneas de salida del comando
    """
    timer = StreamTimer(update_interval=1)

    try:
        # Configurar environment para UTF-8
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'  # Para Python
        env['PYTHONUTF8'] = '1'  # Forzar UTF-8 en Python 3.7+

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combinar stderr con stdout
            text=True,
            bufsize=1,  # Línea por línea
            universal_newlines=True,
            encoding='utf-8',  # ✅ Forzar UTF-8
            errors='replace',  # ✅ Reemplazar caracteres problemáticos
            cwd=cwd,
            env=env  # ✅ Environment con UTF-8
        )

        # Iniciar contador
        timer.start()
        log.debug(f"🚀 Iniciando comando: {' '.join(command)}")

        # Leer línea por línea
        for line in iter(process.stdout.readline, ''):
            # Actualizar actividad (detiene el contador temporalmente)
            timer.update_activity()

            # Limpiar línea de contador si existe
            log.debug('\r' + ' ' * 80 + '\r', end='')  # Limpiar línea

            # Mostrar output real
            clean_line = line.rstrip()
            if clean_line:
                yield clean_line

        # Detener contador
        timer.stop()

        # Limpiar línea final
        log.debug('\r' + ' ' * 80 + '\r', end='')

        # Esperar a que termine el proceso
        process.wait()

        # Verificar si hubo error
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)


    except Exception as e:
        timer.stop()
        log.debug('\r' + ' ' * 80 + '\r', end='')  # Limpiar línea
        yield f"ERROR: {str(e)}"
        raise

    finally:
        timer.stop()


def build_libretranslate_cuda_image(
    repo_path: Path, 
    image_name: str = "libretranslate",
    image_tag: str = "latest"
) -> Dict[str, Any]:
    """
    Construye la imagen Docker de LibreTranslate con soporte CUDA.
    
    :param repo_path: Ruta al repositorio clonado
    :param image_name: Nombre personalizado para la imagen
    :param image_tag: Tag para la imagen (ej: latest, v1.0, cuda)
    :return: Resultado de la construcción
    """
    log.warning(f"*** Construyendo imagen Docker de LibreTranslate con soporte CUDA ***")

    full_image_name = f"{image_name}"
    
    result = {
        'success': False,
        'message': '',
        'image_name': full_image_name,
        'build_output': [],
        'build_info': {}
    }

    try:
        os.chdir(repo_path)
        log.info(f"Cambiado al directorio: {repo_path}")

        dockerfile_path = Path("docker-compose.cuda.yml")
        exists = dockerfile_path.exists()
        log.warning(f'Validando el {dockerfile_path} para construir la imagen: {exists}')

        if exists:
            try:
                log.info(f"Construyendo LibreTranslate Docker con nombre: {full_image_name}")
                log.debug('*'*100)
                log.debug(str(dockerfile_path))
                log.debug('*'*100)
                # Modificar docker-compose para usar nombre personalizado# docker compose -f docker-compose.cuda.yml up -d --build
                build_command = [
                    "docker", "compose",
                    "-f", str(dockerfile_path),
                    "-p", image_name,  # Proyecto personalizado
                    "up", '-d',
                    "--build"
                ]

                log.critical(f"Execute: {' '.join(build_command)}")
                log.debug("\n" + "=" * 60)
                log.debug(f"🔨 CONSTRUYENDO IMAGEN: {full_image_name}")
                log.debug("=" * 60)

                build_output = []
                try:
                    for line in stream_command_output(build_command, cwd=str(repo_path)):
                        log.debug(f"📦 {line}")
                        build_output.append(line)

                        if any(keyword in line.lower() for keyword in ['error', 'failed', 'warning']):
                            if 'error' in line.lower() or 'failed' in line.lower():
                                log.error(f"BUILD ERROR: {line}")
                            else:
                                log.warning(f"BUILD WARNING: {line}")
                        elif any(keyword in line.lower() for keyword in ['successfully', 'complete', 'done']):
                            log.info(f"BUILD SUCCESS: {line}")

                    # Después de construir, renombrar la imagen si es necesario
                    rename_result = rename_docker_image_after_build(image_name, full_image_name)
                    if rename_result['success']:
                        log.info(f"Imagen renombrada exitosamente a: {full_image_name}")

                    log.debug("=" * 60)
                    log.debug("✅ CONSTRUCCIÓN COMPLETADA")
                    log.debug("=" * 60 + "\n")

                    result.update({
                        'success': True,
                        'message': f'Imagen construida correctamente: {full_image_name}',
                        'build_output': build_output,
                        'build_info': {
                            'command': ' '.join(build_command),
                            'lines_output': len(build_output),
                            'image_name': full_image_name
                        }
                    })
                except subprocess.CalledProcessError as e:
                    error_msg = f"❌ Error en construcción: {e}"
                    log.error(error_msg)
                    result['message'] = error_msg
                    result['build_output'] = build_output

            except subprocess.CalledProcessError as e:
                error_msg = f"Error construyendo docker-compose.cuda.yml: {e.stderr}"
                log.info(error_msg)
                result['message'] = error_msg
        else:
            log.info(f"Dockerfile no encontrado: {dockerfile_path}")

        if not result['success']:
            result['message'] = 'No se pudo construir ninguna imagen Docker'
            log.warning(result['message'])

    except Exception as e:
        log.error(f"Error construyendo imagen Docker: {e}")
        result['message'] = str(e)

    return result


def rename_docker_image_after_build(project_name: str, target_name: str) -> Dict[str, Any]:
    """
    Renombra la imagen construida por docker-compose a un nombre personalizado.
    
    :param project_name: Nombre del proyecto usado en docker-compose
    :param target_name: Nombre final deseado para la imagen
    :return: Resultado de la operación
    """
    result = {'success': False, 'message': ''}
    
    try:
        # Buscar imagen construida por docker-compose
        list_result = subprocess.run([
            "docker", "images", "--filter", f"reference={project_name}*",
            "--format", "{{.Repository}}:{{.Tag}}"
        ], capture_output=True, text=True, check=True)
        
        if list_result.stdout.strip():
            source_image = list_result.stdout.strip().split('\n')[0]
            
            # Renombrar imagen
            subprocess.run([
                "docker", "tag", source_image, target_name
            ], check=True, capture_output=True, text=True)
            
            log.info(f"Imagen renombrada de {source_image} a {target_name}")
            
            result.update({
                'success': True,
                'message': f'Imagen renombrada exitosamente a {target_name}',
                'source_image': source_image,
                'target_image': target_name
            })
        else:
            result['message'] = f'No se encontró imagen construida con prefijo {project_name}'
            
    except subprocess.CalledProcessError as e:
        result['message'] = f'Error renombrando imagen: {e.stderr}'
        log.error(f"Error renombrando imagen: {e}")
    
    return result


def run_libretranslate_container_from_image(
    image_name: str, 
    container_name: str = "libretranslate-custom",
    port_mapping: str = "5000:5000",
    additional_args: List[str] = None
) -> Dict[str, Any]:
    """
    Ejecuta un contenedor LibreTranslate desde una imagen construida.
    
    :param image_name: Nombre de la imagen Docker
    :param container_name: Nombre personalizado para el contenedor
    :param port_mapping: Mapeo de puertos (formato "host:container")
    :param additional_args: Argumentos adicionales para docker run
    :return: Resultado de la ejecución
    """
    log.warning(f"*** Ejecutando contenedor LibreTranslate desde imagen {image_name} ***")

    result = {'success': False, 'message': '', 'container_id': None}

    try:
        # Verificar si ya existe un contenedor con ese nombre
        log.info(f"Verificando si existe un contenedor con el nombre {container_name}")
        existing_check = subprocess.run([
            "docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"
        ], capture_output=True, text=True)

        if container_name in existing_check.stdout:
            log.info(f"Contenedor {container_name} ya existe, removiéndolo...")
            subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)

        log.info(f"Ejecutando contenedor desde imagen: {image_name}")

        # Construir comando base
        run_command = [
            "docker", "run", "-d", 
            "--name", container_name, 
            "-p", port_mapping, 
            "--restart", "unless-stopped"
        ]
        
        # Agregar argumentos adicionales si existen
        if additional_args:
            run_command.extend(additional_args)
            
        # Agregar nombre de imagen al final
        run_command.append(image_name)

        log.info(f"Ejecutando: {' '.join(run_command)}")

        result_run = subprocess.run(
            run_command,
            check=True,
            capture_output=True,
            text=True
        )

        container_id = result_run.stdout.strip()

        result.update({
            'success': True,
            'message': f'Contenedor {container_name} iniciado correctamente desde {image_name}',
            'container_id': container_id[:12],
            'container_name': container_name,
            'port_mapping': port_mapping
        })

    except subprocess.CalledProcessError as e:
        result['message'] = f'Error al ejecutar contenedor: {e.stderr}'
        log.error(f"Error ejecutando contenedor: {e}")

    return result


def install_libretranslate() -> dict[str, bool | str | None] | None:
    """
    Instala LibreTranslate priorizando la construcción desde repositorio con soporte CUDA.
    
    :return: Resultado de la instalación
    """
    log.warning("*** Instalando LibreTranslate ***")
    result = {'success': False, 'message': '', 'method': None, 'cleanup_temp': False}
    log.info(f"Install LibreTranslate Result: {result}")

    try:
        # 1. PRIMERA OPCIÓN: Descargar repositorio y construir imagen CUDA
        log.warning("=== OPCIÓN 1: Construyendo desde repositorio oficial ===")

        temp_dir = Path(tempfile.mkdtemp(prefix="libretranslate_"))
        log.info(f"Directorio temporal creado: {temp_dir}")

        # Clonar repositorio
        clone_result = clone_libretranslate_repo(temp_dir)
        if not clone_result['success']:
            log.info(f"Error clonando repositorio: {clone_result['message']}")
            raise Exception("No se pudo clonar el repositorio")

        # Construir imagen
        build_result = build_libretranslate_cuda_image(clone_result['repo_path'])
        if not build_result['success']:
            log.info(f"Error construyendo imagen: {build_result['message']}")
            # raise Exception("No se pudo construir la imagen")

            # Ejecutar contenedor
            run_result = run_libretranslate_container_from_image(build_result['image_name'])
            if run_result['success']:
                result.update({
                    'success': True,
                    'message': f'LibreTranslate instalado desde repositorio: {run_result["message"]}',
                    'method': 'repository_build',
                    'image_name': build_result['image_name'],
                    'container_name': run_result['container_name'],
                    'cleanup_temp': True
                })
                return result
            else:
                raise Exception(f"No se pudo ejecutar contenedor: {run_result['message']}")

        return result

    except Exception as e:
        log.warning(f"Error en instalación desde repositorio: {e}")

        log.info("=== OPCIÓN 2: Usando imagen oficial de Docker Hub ===")
        try:
            log.warning("Instalando LibreTranslate con imagen oficial")
            subprocess.run([
                "docker", "run", "-d", "--name", "libretranslate",
                "-p", "5000:5000", "--restart", "unless-stopped",
                "libretranslate/libretranslate"
            ], check=True, capture_output=True, text=True)

            result.update({
                'success': True,
                'message': 'LibreTranslate instalado usando imagen oficial de Docker Hub',
                'method': 'docker_run_official',
                'cleanup_temp': True
            })

        except subprocess.CalledProcessError as e:
            result.update({
                'message': f'Error en todas las opciones de instalación. Último error: {e.stderr}',
                'cleanup_temp': True
            })
            log.info(f"Error final en instalación: {e}")

    return result



# ---------------------------------------------------------------------------------------------------------------------

def manage_libretranslate() -> Dict:
    """
    Función principal que gestiona LibreTranslate automáticamente.

    :return: Resultado de las acciones realizadas
    """

    status = get_libretranslate_status()

    log.info(f'Info Status {status["status"]}')

    action_result = {'status': status['status'], 'action_taken': None, 'result': None}

    log.info(f"Action Result: {action_result}")

    if status['action_needed'] == 'install_docker':
        log.info("Intentando instalar Docker...")
        # TODO: Programmer install Docker console windows, linux or mac
        action_result.update({
            'action_taken': 'docker_installation',
            'result': {'success': False, 'message': 'Docker debe instalarse manualmente'}
        })

    elif status['action_needed'] == 'start_docker':
        # TODO: Programmer start Docker console windows, linux or mac
        action_result.update({
            'action_taken': 'docker_start',
            'result': {'success': False, 'message': 'Docker debe iniciarse manualmente'}
        })

    elif status['action_needed'] == 'start_container':
        log.info("Intentando iniciar contenedor LibreTranslate...")
        result = start_libretranslate_container(status_data=status)
        log.info(f'Result method start_libretranslate_container: {result}')
        action_result.update({
            'action_taken': 'start_container',
            'result': result
        })

    elif status['action_needed'] == 'install_libretranslate':
        log.info("Intentando instalar LibreTranslate...")
        result = install_libretranslate()
        action_result.update({
            'action_taken': 'install_libretranslate',
            'result': result
        })

    return action_result


if __name__ == "__main__":
    print(manage_libretranslate())