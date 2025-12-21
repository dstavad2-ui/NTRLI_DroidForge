"""
DroidForge Build Manager
========================
Manages build processes for APK generation via local or remote execution.
"""

import os
import subprocess
import json
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from utils.logger import get_logger


class BuildTarget(Enum):
    """Supported build targets."""
    ANDROID_DEBUG = "android_debug"
    ANDROID_RELEASE = "android_release"
    ANDROID_AAB = "android_aab"


class BuildStatus(Enum):
    """Build status states."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BuildResult:
    """Result of a build operation."""
    build_id: str
    target: BuildTarget
    status: BuildStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    artifact_path: Optional[str] = None
    logs: List[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "build_id": self.build_id,
            "target": self.target.value,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "artifact_path": self.artifact_path,
            "error": self.error
        }


class BuildManager:
    """
    Manages build operations for DroidForge.
    
    Supports:
    - Local buildozer builds
    - Remote GitHub Actions builds
    - Build status tracking
    - Artifact management
    """
    
    def __init__(self, config_manager, event_bus):
        self.config = config_manager
        self.event_bus = event_bus
        self.logger = get_logger("BuildManager")
        
        # Build tracking
        self._builds: Dict[str, BuildResult] = {}
        self._current_build: Optional[str] = None
        
        # Callbacks
        self._progress_callbacks: List[Callable] = []
    
    def build_local(self, target: BuildTarget = BuildTarget.ANDROID_DEBUG,
                    project_path: str = None) -> BuildResult:
        """
        Execute a local build using buildozer.
        
        Args:
            target: Build target type
            project_path: Path to project (default: current directory)
            
        Returns:
            BuildResult object
        """
        import uuid
        build_id = str(uuid.uuid4())[:8]
        
        result = BuildResult(
            build_id=build_id,
            target=target,
            status=BuildStatus.RUNNING,
            started_at=datetime.now(),
            logs=[]
        )
        self._builds[build_id] = result
        self._current_build = build_id
        
        self.logger.info(f"Starting local build: {build_id} ({target.value})")
        self.event_bus.emit("build_started", build_id, target.value)
        
        try:
            # Determine buildozer command
            if target == BuildTarget.ANDROID_DEBUG:
                cmd = ["buildozer", "android", "debug"]
            elif target == BuildTarget.ANDROID_RELEASE:
                cmd = ["buildozer", "android", "release"]
            elif target == BuildTarget.ANDROID_AAB:
                cmd = ["buildozer", "android", "release", "aab"]
            else:
                raise ValueError(f"Unknown target: {target}")
            
            # Execute buildozer
            project_path = project_path or os.getcwd()
            
            process = subprocess.Popen(
                cmd,
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Stream output
            for line in process.stdout:
                result.logs.append(line.strip())
                self._notify_progress(build_id, line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                result.status = BuildStatus.SUCCESS
                # Find artifact
                bin_dir = os.path.join(project_path, "bin")
                if os.path.exists(bin_dir):
                    apks = [f for f in os.listdir(bin_dir) if f.endswith('.apk')]
                    if apks:
                        result.artifact_path = os.path.join(bin_dir, apks[0])
            else:
                result.status = BuildStatus.FAILED
                result.error = f"Build failed with exit code {process.returncode}"
            
        except FileNotFoundError:
            result.status = BuildStatus.FAILED
            result.error = "buildozer not found. Install with: pip install buildozer"
        except Exception as e:
            result.status = BuildStatus.FAILED
            result.error = str(e)
            self.logger.error(f"Build error: {e}")
        
        result.completed_at = datetime.now()
        self._current_build = None
        
        self.event_bus.emit("build_completed", build_id, result.status.value)
        self.logger.info(f"Build {build_id} completed: {result.status.value}")
        
        return result
    
    def build_remote(self, target: BuildTarget = BuildTarget.ANDROID_DEBUG,
                     branch: str = "main") -> Dict:
        """
        Trigger a remote build via GitHub Actions.
        
        Args:
            target: Build target type
            branch: Git branch to build
            
        Returns:
            Dictionary with workflow dispatch result
        """
        from .github_integration import GitHubIntegration
        
        github = GitHubIntegration(self.config, self.event_bus)
        
        # Trigger workflow dispatch
        result = github.trigger_workflow(
            workflow_file=self.config.get("github.workflow", "build.yml"),
            ref=branch,
            inputs={
                "build_type": target.value,
                "triggered_by": "droidforge"
            }
        )
        
        return result
    
    def get_build(self, build_id: str) -> Optional[BuildResult]:
        """Get a build by ID."""
        return self._builds.get(build_id)
    
    def get_current_build(self) -> Optional[BuildResult]:
        """Get the currently running build."""
        if self._current_build:
            return self._builds.get(self._current_build)
        return None
    
    def get_build_history(self, limit: int = 20) -> List[BuildResult]:
        """Get build history."""
        builds = list(self._builds.values())
        return sorted(builds, key=lambda b: b.started_at, reverse=True)[:limit]
    
    def cancel_build(self, build_id: str) -> bool:
        """Cancel a running build."""
        if build_id in self._builds:
            build = self._builds[build_id]
            if build.status == BuildStatus.RUNNING:
                build.status = BuildStatus.CANCELLED
                build.completed_at = datetime.now()
                self.event_bus.emit("build_cancelled", build_id)
                return True
        return False
    
    def on_progress(self, callback: Callable):
        """Register a progress callback."""
        self._progress_callbacks.append(callback)
    
    def _notify_progress(self, build_id: str, message: str):
        """Notify progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(build_id, message)
            except Exception as e:
                self.logger.error(f"Progress callback error: {e}")
    
    def generate_buildozer_spec(self, project_name: str, 
                                 package_name: str,
                                 version: str = "1.0.0") -> str:
        """
        Generate a buildozer.spec file content.
        
        Args:
            project_name: Application name
            package_name: Package identifier (e.g., com.example.app)
            version: Version string
            
        Returns:
            buildozer.spec content
        """
        spec = f"""[app]
# Application name
title = {project_name}

# Package name
package.name = {project_name.lower().replace(' ', '_')}

# Package domain
package.domain = {'.'.join(reversed(package_name.split('.')[:-1]))}

# Source directory
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# Application version
version = {version}

# Requirements
requirements = python3,kivy,kivymd,pillow,requests

# Supported orientations
orientation = portrait

# Android permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android API levels
android.minapi = {self.config.get('build.min_sdk', 21)}
android.api = {self.config.get('build.target_sdk', 33)}
android.ndk_api = 21

# Fullscreen mode
fullscreen = 0

# Icon
#icon.filename = %(source.dir)s/assets/icon.png

# Presplash
#presplash.filename = %(source.dir)s/assets/presplash.png

# Android specific settings
android.archs = arm64-v8a,armeabi-v7a

# Copy python source to APK
android.copy_libs = 1

# Enable AndroidX
android.enable_androidx = True

# Gradle dependencies
android.gradle_dependencies = 

# Java files to add
#android.add_jars = 

# AAR files to add
#android.add_aars = 

# Python-for-Android branch
p4a.branch = master

# Bootstrap
p4a.bootstrap = sdl2

[buildozer]
# Log level (debug, info, warning, error, critical)
log_level = 2

# Warn on root
warn_on_root = 1

# Build directory
# build_dir = ./.buildozer

# Bin directory
# bin_dir = ./bin
"""
        return spec
