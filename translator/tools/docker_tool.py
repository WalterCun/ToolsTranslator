#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
translator/tools/docker_tools.py

Optimized Docker management tools for LibreTranslate containers.
Provides intelligent installation, management, and monitoring of LibreTranslate Docker containers.

Author: Walter Cun Bustamante
Version: 2.0
"""

import subprocess
import logging
import json
import time
import os
import tempfile
from enum import Enum
from typing import Dict, List, Any, Iterator, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

import requests
from colorlog import basicConfig

# Configure logging with colors
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

# Constants
LIBRETRANSLATE_REPO_URL = "https://github.com/LibreTranslate/LibreTranslate.git"
DEFAULT_PORT = 5000
DEFAULT_TIMEOUT = 60
DOCKER_COMPOSE_FILE = "docker-compose.cuda.yml"
PROJECT_NAME = "libretranslate"


class ContainerStatus(Enum):
    """Possible container states"""
    RUNNING = "running"
    STOPPED = "stopped"
    NOT_FOUND = "not_found"
    DOCKER_NOT_RUNNING = "docker_not_running"
    ERROR = "error"


@dataclass
class ContainerInfo:
    """Container information data class"""
    id: str
    name: str
    status: str
    ports: str
    state: str
    image: str
    ancestor_pattern: Optional[str] = None
    found_by: Optional[str] = None

    def is_running(self) -> bool:
        """Check if container is running"""
        return self.state.lower() in ['running', 'up']

    def is_stopped(self) -> bool:
        """Check if container is stopped"""
        return self.state.lower() in ['exited', 'stopped', 'created']


@dataclass
class ImageInfo:
    """Docker image information data class"""
    id: str
    repository: str
    tag: str
    size: str
    created: str

    @property
    def full_name(self) -> str:
        """Get full image name"""
        return f"{self.repository}:{self.tag}"


@dataclass
class OperationResult:
    """Standard operation result"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class DockerException(Exception):
    """Custom exception for Docker operations"""
    pass


class DockerManager:
    """Manages Docker operations and utilities"""

    @staticmethod
    def is_docker_installed() -> bool:
        """
        Check if Docker is installed on the system.

        Returns:
            bool: True if Docker is installed, False otherwise
        """
        log.debug("Checking if Docker is installed")
        try:
            subprocess.run(
                ["docker", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            log.info("Docker is installed")
            return True
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            log.error("Docker is not installed or not accessible")
            return False

    @staticmethod
    def is_docker_running() -> bool:
        """
        Check if the Docker daemon is running.

        Returns:
            bool: True if Docker is running, False otherwise
        """
        log.debug("Checking if Docker daemon is running")
        try:
            result = subprocess.run(
                ["docker", "info"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            is_running = result.returncode == 0
            log.info(f"Docker daemon running: {is_running}")
            return is_running
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            log.error("Docker daemon is not running")
            return False

    @staticmethod
    def execute_docker_command(command: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """
        Execute a Docker command with proper error handling.

        Args:
            command: Docker command as list of strings
            timeout: Command timeout in seconds

        Returns:
            subprocess.CompletedProcess: Command result

        Raises:
            DockerException: If Docker is not available or command fails
        """
        if not DockerManager.is_docker_running():
            raise DockerException("Docker daemon is not running")

        try:
            log.debug(f"Executing Docker command: {' '.join(command)}")
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.CalledProcessError as e:
            error_msg = f"Docker command failed: {e.stderr}"
            log.error(error_msg)
            raise DockerException(error_msg)
        except subprocess.TimeoutExpired:
            error_msg = f"Docker command timed out after {timeout} seconds"
            log.error(error_msg)
            raise DockerException(error_msg)


class LibreTranslateManager:
    """Manages LibreTranslate Docker containers and images"""

    def __init__(self, docker_manager: Optional[DockerManager] = None):
        self.docker = docker_manager or DockerManager()
        self.search_patterns = [
            "libretranslate/libretranslate",
            "libretranslate-libretranslate",
            "libretranslate"
        ]

    def find_all_containers(self) -> List[ContainerInfo]:
        """
        Find all LibreTranslate containers using multiple search patterns.

        Returns:
            List[ContainerInfo]: List of found containers
        """
        log.info("Searching for LibreTranslate containers")
        containers = []

        try:
            # Search by ancestor patterns
            for pattern in self.search_patterns:
                containers.extend(self._search_containers_by_ancestor(pattern))

            # Search by name
            containers.extend(self._search_containers_by_name())

            # Remove duplicates
            unique_containers = self._remove_duplicate_containers(containers)

            log.info(f"Found {len(unique_containers)} unique LibreTranslate containers")
            return unique_containers

        except DockerException as e:
            log.error(f"Error finding containers: {e}")
            return []

    def _search_containers_by_ancestor(self, pattern: str) -> List[ContainerInfo]:
        """Search containers by ancestor pattern"""
        containers = []
        try:
            result = self.docker.execute_docker_command([
                "docker", "ps", "-a",
                "--filter", f"ancestor={pattern}",
                "--format", "{{json .}}"
            ])

            containers = self._parse_container_output(result.stdout, ancestor_pattern=pattern)
        except DockerException:
            pass  # Continue with other patterns

        return containers

    def _search_containers_by_name(self) -> List[ContainerInfo]:
        """Search containers by name pattern"""
        containers = []
        try:
            result = self.docker.execute_docker_command([
                "docker", "ps", "-a",
                "--filter", "name=libretranslate",
                "--format", "{{json .}}"
            ])

            containers = self._parse_container_output(result.stdout, found_by="name_filter")
        except DockerException:
            pass

        return containers

    def _parse_container_output(self, output: str, **kwargs) -> List[ContainerInfo]:
        """Parse Docker container JSON output"""
        containers = []

        if not output.strip():
            return containers

        for line in output.strip().split('\n'):
            try:
                data = json.loads(line)
                container = ContainerInfo(
                    id=data.get('ID', '')[:12],
                    name=data.get('Names', ''),
                    status=data.get('Status', ''),
                    ports=data.get('Ports', ''),
                    state=data.get('State', 'unknown'),
                    image=data.get('Image', ''),
                    **kwargs
                )
                containers.append(container)
            except (json.JSONDecodeError, KeyError) as e:
                log.warning(f"Failed to parse container data: {e}")
                continue

        return containers

    def _remove_duplicate_containers(self, containers: List[ContainerInfo]) -> List[ContainerInfo]:
        """Remove duplicate containers based on ID"""
        seen_ids = set()
        unique_containers = []

        for container in containers:
            if container.id not in seen_ids:
                seen_ids.add(container.id)
                unique_containers.append(container)

        return unique_containers

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive LibreTranslate status and recommended actions.

        Returns:
            Dict[str, Any]: Status information and recommendations
        """
        log.info("Getting LibreTranslate status")

        all_containers = self.find_all_containers()
        running_containers = [c for c in all_containers if c.is_running()]
        stopped_containers = [c for c in all_containers if c.is_stopped()]

        status_info = {
            'status': None,
            'action_needed': None,
            'containers_found': [asdict(c) for c in all_containers],
            'running_containers': [asdict(c) for c in running_containers],
            'stopped_containers': [asdict(c) for c in stopped_containers],
            'message': '',
            'can_start': False,
            'can_install': False
        }

        if running_containers:
            status_info.update({
                'status': ContainerStatus.RUNNING,
                'action_needed': None,
                'message': f'LibreTranslate is running. {len(running_containers)} active container(s)'
            })
        elif stopped_containers:
            status_info.update({
                'status': ContainerStatus.STOPPED,
                'action_needed': 'start_container',
                'message': f'LibreTranslate is installed but stopped. {len(stopped_containers)} available container(s)',
                'can_start': True
            })
        else:
            status_info.update({
                'status': ContainerStatus.NOT_FOUND,
                'action_needed': 'install_libretranslate',
                'message': 'No LibreTranslate containers found',
                'can_install': True
            })

        return status_info

    def start_container(self, container_id: Optional[str] = None) -> OperationResult:
        """
        Start a LibreTranslate container.

        Args:
            container_id: Specific container ID to start, or None for first available

        Returns:
            OperationResult: Operation result
        """
        log.info("Starting LibreTranslate container")

        if not container_id:
            status = self.get_status()
            if status['stopped_containers']:
                container_id = status['stopped_containers'][0]['id']
                log.info(f"Using first stopped container: {container_id}")
            else:
                return OperationResult(
                    success=False,
                    message="No stopped containers found to start"
                )

        try:
            self.docker.execute_docker_command(["docker", "start", container_id])
            return OperationResult(
                success=True,
                message=f"Container {container_id} started successfully",
                data={'container_id': container_id}
            )
        except DockerException as e:
            return OperationResult(
                success=False,
                message=f"Failed to start container {container_id}",
                error=str(e)
            )

    def find_existing_images(self) -> List[ImageInfo]:
        """
        Find all existing LibreTranslate images locally.

        Returns:
            List[ImageInfo]: List of found images
        """
        log.info("Searching for existing LibreTranslate images")
        images = []

        search_patterns = ["*libretranslate*", "libretranslate/*"]

        for pattern in search_patterns:
            try:
                result = self.docker.execute_docker_command([
                    "docker", "images",
                    "--filter", f"reference={pattern}",
                    "--format", "{{.ID}}\t{{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
                ])

                images.extend(self._parse_image_output(result.stdout))
            except DockerException:
                continue

        # Remove duplicates
        unique_images = self._remove_duplicate_images(images)
        log.info(f"Found {len(unique_images)} unique LibreTranslate images")

        return unique_images

    def _parse_image_output(self, output: str) -> List[ImageInfo]:
        """Parse Docker image output"""
        images = []

        if not output.strip():
            return images

        for line in output.strip().split('\n'):
            parts = line.split('\t')
            if len(parts) >= 4:
                image = ImageInfo(
                    id=parts[0][:12],
                    repository=parts[1],
                    tag=parts[2],
                    size=parts[3],
                    created=parts[4] if len(parts) > 4 else 'unknown'
                )
                images.append(image)

        return images

    def _remove_duplicate_images(self, images: List[ImageInfo]) -> List[ImageInfo]:
        """Remove duplicate images based on ID and full name"""
        seen = set()
        unique_images = []

        for image in images:
            key = (image.id, image.full_name)
            if key not in seen:
                seen.add(key)
                unique_images.append(image)

        return unique_images


class ServiceChecker:
    """Checks if LibreTranslate service is accessible"""

    def __init__(self, host: str = "localhost", port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}"

    def is_service_running(self, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """
        Check if LibreTranslate service is accessible with exponential backoff.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            bool: True if service is accessible, False otherwise
        """
        log.info(f"Checking if LibreTranslate service is running at {self.url}")

        wait_time = 1
        max_wait_time = timeout

        while True:
            try:
                response = requests.get(self.url, timeout=5)
                if response.status_code == 200:
                    log.info("LibreTranslate service is accessible")
                    return True
                return False
            except requests.RequestException as e:
                log.debug(f"Service check failed: {e}")

            # Exponential backoff with cap
            time.sleep(min(wait_time, max_wait_time))
            wait_time = min(wait_time * 2, max_wait_time)
            log.info(f"Waiting for {wait_time} seconds before retrying")


class LibreTranslateInstaller:
    """Handles LibreTranslate installation with multiple strategies"""

    def __init__(self, manager: LibreTranslateManager, docker: DockerManager):
        self.manager = manager
        self.docker = docker

    def install_smart(self) -> OperationResult:
        """
        Smart installation that tries multiple methods in order of preference.

        Returns:
            OperationResult: Installation result
        """
        log.info("Starting smart LibreTranslate installation")

        # Strategy 1: Use existing local image
        result = self._try_existing_image()
        if result.success:
            return result

        # Strategy 2: Build from a repository (last resort)
        result = self._try_build_from_repo()
        if result.success:
            return result

        # Strategy 3: Pull the official image from Docker Hub
        result = self._try_docker_hub_image()
        if result.success:
            return result

        return OperationResult(
            success=False,
            message="All installation methods failed",
            error="Could not install LibreTranslate using any available method"
        )

    def _try_existing_image(self) -> OperationResult:
        """Try to use existing local image"""
        log.info("Trying to use existing local image")

        existing_images = self.manager.find_existing_images()
        if not existing_images:
            return OperationResult(success=False, message="No existing images found")

        # Use the first available image
        best_image = existing_images[0]

        try:
            result = self._run_container_from_image(best_image)
            if result.success:
                return OperationResult(
                    success=True,
                    message=f"LibreTranslate started from existing image: {best_image.full_name}",
                    data={
                        'method': 'existing_image',
                        'image_used': best_image.full_name,
                        'container_info': result.data
                    }
                )
        except Exception as e:
            log.warning(f"Failed to use existing image: {e}")

        return OperationResult(success=False, message="Could not use existing image")

    def _try_docker_hub_image(self) -> OperationResult:
        """Try to pull and run official image from Docker Hub"""
        log.info("Trying to pull official image from Docker Hub")

        official_image = "libretranslate/libretranslate:latest"
        container_name = "libretranslate-official"

        try:
            # Pull image
            log.info("Pulling official LibreTranslate image")
            self.docker.execute_docker_command([
                "docker", "pull", official_image
            ], timeout=300)  # Longer timeout for image pull

            # Run container
            self.docker.execute_docker_command([
                "docker", "run", "-d",
                "--name", container_name,
                "-p", f"{DEFAULT_PORT}:{DEFAULT_PORT}",
                "--restart", "unless-stopped",
                official_image
            ])

            return OperationResult(
                success=True,
                message="LibreTranslate installed from Docker Hub",
                data={
                    'method': 'docker_hub_official',
                    'image_used': official_image,
                    'container_name': container_name
                }
            )

        except DockerException as e:
            log.warning(f"Failed to install from Docker Hub: {e}")
            return OperationResult(
                success=False,
                message="Failed to install from Docker Hub",
                error=str(e)
            )

    def _try_build_from_repo(self) -> OperationResult:
        """
        Try to build LibreTranslate from GitHub repository with CUDA support.

        Returns:
            OperationResult: Build and deployment result
        """
        log.info("Trying to build LibreTranslate from repository")

        temp_dir = None
        try:
            # Create temporary directory
            temp_dir = Path(tempfile.mkdtemp(prefix="libretranslate_build_"))
            log.info(f"Created temporary directory: {temp_dir}")

            # Clone repository
            clone_result = self._clone_repository(temp_dir)
            if not clone_result.success:
                return clone_result

            # Build image using docker-compose
            build_result = self._build_cuda_image(temp_dir)
            if not build_result.success:
                return build_result

            # Run container from built image
            run_result = self._deploy_built_container(build_result.data.get('image_name', 'libretranslate:latest'))
            if not run_result.success:
                return run_result

            return OperationResult(
                success=True,
                message="LibreTranslate successfully built and deployed from repository",
                data={
                    'method': 'repository_build',
                    'build_info': build_result.data,
                    'container_info': run_result.data,
                    'temp_dir': str(temp_dir)
                }
            )

        except Exception as e:
            log.error(f"Error building from repository: {e}")
            return OperationResult(
                success=False,
                message="Failed to build from repository",
                error=str(e)
            )
        finally:
            # Cleanup temporary directory
            if temp_dir and temp_dir.exists():
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                    log.debug(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    log.warning(f"Failed to cleanup temp directory {temp_dir}: {e}")

    def _clone_repository(self, temp_dir: Path) -> OperationResult:
        """
        Clone LibreTranslate repository to temporary directory.

        Args:
            temp_dir: Directory where to clone the repository

        Returns:
            OperationResult: Clone operation result
        """
        log.info(f"Cloning LibreTranslate repository to {temp_dir}")

        try:
            # Check if git is available
            subprocess.run(
                ["git", "--version"],
                check=True,
                capture_output=True,
                timeout=10
            )

            # Clone the repository
            log.info(f"Executing: git clone {LIBRETRANSLATE_REPO_URL} {temp_dir}")
            subprocess.run([
                "git", "clone", LIBRETRANSLATE_REPO_URL, str(temp_dir)
            ], check=True, capture_output=True, text=True, timeout=120)

            return OperationResult(
                success=True,
                message=f"Repository cloned successfully to {temp_dir}",
                data={'repo_path': str(temp_dir)}
            )

        except FileNotFoundError:
            return OperationResult(
                success=False,
                message="Git is not installed on the system",
                error="git command not found"
            )
        except subprocess.CalledProcessError as e:
            return OperationResult(
                success=False,
                message="Failed to clone repository",
                error=f"Git clone failed: {e.stderr}"
            )
        except subprocess.TimeoutExpired:
            return OperationResult(
                success=False,
                message="Repository clone timed out",
                error="Git clone operation exceeded timeout"
            )

    def _build_cuda_image(self, repo_path: Path) -> OperationResult:
        """
        Build LibreTranslate Docker image with CUDA support using docker-compose.

        Args:
            repo_path: Path to cloned repository

        Returns:
            OperationResult: Build an operation result
        """
        log.info("Building LibreTranslate CUDA image")

        # Change to repository directory
        original_cwd = os.getcwd()

        try:
            os.chdir(repo_path)
            log.info(f"Changed to directory: {repo_path}")

            # Check if docker-compose.cuda.yml exists
            dockerfile_path = Path(DOCKER_COMPOSE_FILE)
            if not dockerfile_path.exists():
                return OperationResult(
                    success=False,
                    message=f"Docker compose file not found: {DOCKER_COMPOSE_FILE}",
                    error=f"Required file {DOCKER_COMPOSE_FILE} missing in repository"
                )

            # Check for existing containers to avoid conflicts
            existing_containers = self.manager.find_all_containers()
            running_containers = [c for c in existing_containers if c.is_running()]

            if running_containers:
                return OperationResult(
                    success=True,
                    message=f"LibreTranslate already running: {running_containers[0].name}",
                    data={
                        'image_name': running_containers[0].image,
                        'container_reused': True,
                        'existing_container': asdict(running_containers[0])
                    }
                )

            # Build using docker-compose
            build_command = [
                "docker", "compose",
                "-f", str(dockerfile_path),
                "-p", PROJECT_NAME,
                "up", "-d", "--build"
            ]

            log.info(f"Executing build command: {' '.join(build_command)}")

            # Execute build with streaming output
            build_output = []
            build_success = True

            try:
                for line in self._stream_command_output(build_command, cwd=str(repo_path)):
                    log.debug(f"BUILD: {line}")
                    build_output.append(line)

                    # Check for critical errors
                    line_lower = line.lower()
                    if any(error_keyword in line_lower for error_keyword in ['error', 'failed']):
                        if 'error' in line_lower or 'failed' in line_lower:
                            log.error(f"BUILD ERROR: {line}")
                            build_success = False
                        else:
                            log.warning(f"BUILD WARNING: {line}")
                    elif any(success_keyword in line_lower for success_keyword in ['successfully', 'complete', 'done']):
                        log.info(f"BUILD SUCCESS: {line}")

                if not build_success:
                    return OperationResult(
                        success=False,
                        message="Build completed with errors",
                        error="Error detected in build output",
                        data={'build_output': build_output}
                    )

                # Rename image to custom name
                target_image_name = "libretranslate:latest"
                rename_result = self._rename_composed_image(PROJECT_NAME, target_image_name)

                final_image_name = target_image_name if rename_result.success else f"{PROJECT_NAME}_libretranslate"

                return OperationResult(
                    success=True,
                    message=f"Image built successfully: {final_image_name}",
                    data={
                        'image_name': final_image_name,
                        'build_output': build_output,
                        'lines_output': len(build_output),
                        'renamed': rename_result.success
                    }
                )

            except subprocess.CalledProcessError as e:
                return OperationResult(
                    success=False,
                    message="Docker compose build failed",
                    error=f"Build process failed: {e}",
                    data={'build_output': build_output}
                )

        except Exception as e:
            return OperationResult(
                success=False,
                message="Error during build process",
                error=str(e)
            )
        finally:
            # Restore the original working directory
            os.chdir(original_cwd)

    def _stream_command_output(self, command: List[str], cwd: Optional[str] = None) -> Iterator[str]:
        """
        Execute command and yield output line by line in real-time.

        Args:
            command: Command to execute as list of strings
            cwd: Working directory for command execution

        Yields:
            str: Lines of command output
        """
        try:
            # Configure environment for UTF-8
            env = os.environ.copy()
            env.update({
                'PYTHONIOENCODING': 'utf-8',
                'PYTHONUTF8': '1'
            })

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                text=True,
                bufsize=1,  # Line buffering
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',  # Replace problematic characters
                cwd=cwd,
                env=env
            )

            log.debug(f"Started command: {' '.join(command)}")

            # Read line by line
            for line in iter(process.stdout.readline, ''):
                clean_line = line.rstrip()
                if clean_line:  # Only yield non-empty lines
                    yield clean_line

            # Wait for process completion
            process.wait()

            # Check for errors
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command)

        except Exception as e:
            log.error(f"Command execution failed: {e}")
            yield f"ERROR: {str(e)}"
            raise

    def _rename_composed_image(self, project_name: str, target_name: str) -> OperationResult:
        """
        Rename image created by docker-compose to a custom name.

        Args:
            project_name: Project name used in docker-compose
            target_name: Desired final image name

        Returns:
            OperationResult: Rename operation result
        """
        try:
            # Find image built by docker-compose
            result = self.docker.execute_docker_command([
                "docker", "images",
                "--filter", f"reference={project_name}*",
                "--format", "{{.Repository}}:{{.Tag}}"
            ])

            if result.stdout.strip():
                source_image = result.stdout.strip().split('\n')[0]

                # Tag with a new name
                self.docker.execute_docker_command([
                    "docker", "tag", source_image, target_name
                ])

                log.info(f"Image renamed from {source_image} to {target_name}")

                return OperationResult(
                    success=True,
                    message=f"Image renamed successfully to {target_name}",
                    data={
                        'source_image': source_image,
                        'target_image': target_name
                    }
                )
            else:
                return OperationResult(
                    success=False,
                    message=f"No image found with prefix {project_name}",
                    error="Built image not found for renaming"
                )

        except DockerException as e:
            return OperationResult(
                success=False,
                message="Failed to rename image",
                error=str(e)
            )

    def _deploy_built_container(self, image_name: str,
                                container_name: str = "libretranslate-custom") -> OperationResult:
        """
        Deploy container from built image.

        Args:
            image_name: Name of the built Docker image
            container_name: Name for the new container

        Returns:
            OperationResult: Deployment result
        """
        log.info(f"Deploying container from built image: {image_name}")

        try:
            # Check if container with same name exists
            existing_check = self.docker.execute_docker_command([
                "docker", "ps", "-a",
                "--filter", f"name={container_name}",
                "--format", "{{.Names}}"
            ])

            if container_name in existing_check.stdout:
                log.info(f"Removing existing container: {container_name}")
                try:
                    self.docker.execute_docker_command([
                        "docker", "rm", "-f", container_name
                    ])
                except DockerException:
                    pass  # Continue if removal fails

            # Run new container
            run_command = [
                "docker", "run", "-d",
                "--name", container_name,
                "-p", f"{DEFAULT_PORT}:{DEFAULT_PORT}",
                "--restart", "unless-stopped",
                image_name
            ]

            log.info(f"Executing: {' '.join(run_command)}")

            result = self.docker.execute_docker_command(run_command)
            container_id = result.stdout.strip()

            return OperationResult(
                success=True,
                message=f"Container {container_name} deployed successfully",
                data={
                    'container_id': container_id[:12],
                    'container_name': container_name,
                    'image_used': image_name,
                    'port_mapping': f"{DEFAULT_PORT}:{DEFAULT_PORT}"
                }
            )

        except DockerException as e:
            return OperationResult(
                success=False,
                message=f"Failed to deploy container from image {image_name}",
                error=str(e)
            )

    def _run_container_from_image(self, image: ImageInfo,
                                  container_name: Optional[str] = None) -> OperationResult:
        """Run container from existing image"""
        if not container_name:
            repo_clean = image.repository.replace('/', '-').replace(':', '-')
            container_name = f"{repo_clean}-{image.tag}"

        try:
            # Check if container already exists
            existing_check = self.docker.execute_docker_command([
                "docker", "ps", "-a",
                "--filter", f"name={container_name}",
                "--format", "{{.Names}}"
            ])

            if container_name in existing_check.stdout:
                # Start existing container
                self.docker.execute_docker_command([
                    "docker", "start", container_name
                ])

                return OperationResult(
                    success=True,
                    message=f"Existing container {container_name} started",
                    data={'container_name': container_name, 'restarted': True}
                )
            else:
                # Create new container
                self.docker.execute_docker_command([
                    "docker", "run", "-d",
                    "--name", container_name,
                    "-p", f"{DEFAULT_PORT}:{DEFAULT_PORT}",
                    "--restart", "unless-stopped",
                    image.full_name
                ])

                return OperationResult(
                    success=True,
                    message=f"New container {container_name} created",
                    data={'container_name': container_name, 'created': True}
                )

        except DockerException as e:
            return OperationResult(
                success=False,
                message=f"Failed to run container from image {image.full_name}",
                error=str(e)
            )


def manage_libretranslate() -> Dict[str, Any]:
    """
    Main function to automatically manage LibreTranslate.

    This is the primary entry point that handles the complete lifecycle:
    - Checks current status
    - Takes appropriate action (start existing container or install)
    - Verifies service accessibility

    Returns:
        Dict[str, Any]: Complete management result with status and actions taken
    """
    log.info("Starting LibreTranslate management")

    try:
        # Initialize managers
        docker = DockerManager()
        manager = LibreTranslateManager(docker)
        checker = ServiceChecker()
        installer = LibreTranslateInstaller(manager, docker)

        # Check Docker availability
        if not docker.is_docker_installed():
            return {
                'success': False,
                'message': 'Docker is not installed',
                'action_taken': 'none',
                'status_connect': False
            }

        if not docker.is_docker_running():
            return {
                'success': False,
                'message': 'Docker daemon is not running',
                'action_taken': 'none',
                'status_connect': False
            }

        # Get current status
        status = manager.get_status()
        log.info(f"Current status: {status['status']}")

        result = status.copy()
        result['action_taken'] = None
        result['result'] = None

        # Handle based on current status
        if status['running_containers']:
            log.info("LibreTranslate is already running")
            result.update({
                'action_taken': 'no_action_needed',
                'result': OperationResult(
                    success=True,
                    message='LibreTranslate is already active'
                ).to_dict()
            })

        elif status['action_needed'] == 'start_container':
            log.info("Starting existing container")
            operation_result = manager.start_container()
            result.update({
                'action_taken': 'start_container',
                'result': operation_result.to_dict()
            })

        elif status['action_needed'] == 'install_libretranslate':
            log.info("Installing LibreTranslate")
            operation_result = installer.install_smart()
            result.update({
                'action_taken': 'install_libretranslate_smart',
                'result': operation_result.to_dict()
            })

        # Check service accessibility
        result['status_connect'] = checker.is_service_running()
        result['success'] = result.get('result', {}).get('success', False)

        log.info(f"Management completed. Success: {result['success']}, Service accessible: {result['status_connect']}")
        return result

    except Exception as e:
        log.error(f"Error in LibreTranslate management: {e}")
        return {
            'success': False,
            'message': f'Management error: {str(e)}',
            'action_taken': 'error',
            'status_connect': False,
            'error': str(e)
        }


# Utility functions for backward compatibility
def is_docker_running() -> bool:
    """Backward compatibility function"""
    return DockerManager.is_docker_running()


def is_docker_installed() -> bool:
    """Backward compatibility function"""
    return DockerManager.is_docker_installed()


def get_libretranslate_status() -> Dict[str, Any]:
    """Backward compatibility function"""
    manager = LibreTranslateManager()
    return manager.get_status()


# Example usage
if __name__ == "__main__":
    # Example of how to use the optimized code
    result = manage_libretranslate()
    print(f"Management result: {result}")
