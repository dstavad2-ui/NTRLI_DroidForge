"""
DroidForge Core Engine
======================
The central orchestration engine that manages command execution,
workflow automation, and system coordination.

This engine implements a deterministic, command-driven architecture where
all actions are reproducible, auditable, and traceable.
"""

import threading
import queue
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any

from utils.logger import get_logger
from .command_processor import CommandProcessor
from .execution_context import ExecutionContext


class DroidForgeEngine:
    """
    Core Engine for DroidForge Console.
    
    Responsibilities:
    - Command queue management and execution
    - Workflow orchestration
    - Proof-of-work logging
    - Remote execution coordination
    - State management
    
    Architecture:
    - All actions flow through deterministic commands
    - Execution is logged for auditability
    - Configuration changes propagate without rebuilds
    """
    
    def __init__(self, config_manager, event_bus):
        self.config_manager = config_manager
        self.event_bus = event_bus
        self.logger = get_logger("Engine")
        
        # Command processing
        self.command_processor = CommandProcessor(self)
        self.command_queue = queue.Queue()
        self.execution_history: List[Dict] = []
        
        # State management
        self.is_running = False
        self.current_context: Optional[ExecutionContext] = None
        self._worker_thread: Optional[threading.Thread] = None
        
        # Registered handlers
        self._command_handlers: Dict[str, Callable] = {}
        self._workflow_definitions: Dict[str, Dict] = {}
        
        # Initialize built-in commands
        self._register_builtin_commands()
        
        self.logger.info("DroidForge Engine initialized")
    
    def _register_builtin_commands(self):
        """Register built-in command handlers."""
        self.register_command("echo", self._cmd_echo)
        self.register_command("config.get", self._cmd_config_get)
        self.register_command("config.set", self._cmd_config_set)
        self.register_command("workflow.run", self._cmd_workflow_run)
        self.register_command("system.status", self._cmd_system_status)
        self.register_command("build.trigger", self._cmd_build_trigger)
        self.register_command("git.status", self._cmd_git_status)
        self.register_command("ai.generate", self._cmd_ai_generate)
        
        self.logger.info(f"Registered {len(self._command_handlers)} built-in commands")
    
    def register_command(self, name: str, handler: Callable):
        """Register a command handler."""
        self._command_handlers[name] = handler
        self.logger.debug(f"Registered command: {name}")
    
    def register_workflow(self, name: str, definition: Dict):
        """Register a workflow definition."""
        self._workflow_definitions[name] = definition
        self.logger.debug(f"Registered workflow: {name}")
    
    def start(self):
        """Start the engine worker thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            daemon=True,
            name="DroidForge-Worker"
        )
        self._worker_thread.start()
        self.logger.info("Engine started")
        self.event_bus.emit("engine_started")
    
    def shutdown(self):
        """Shutdown the engine gracefully."""
        self.logger.info("Shutting down engine...")
        self.is_running = False
        
        # Signal worker to stop
        self.command_queue.put(None)
        
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)
        
        self.logger.info("Engine shutdown complete")
        self.event_bus.emit("engine_stopped")
    
    def execute(self, command: str, params: Dict = None, 
                async_exec: bool = True) -> Optional[Dict]:
        """
        Execute a command.
        
        Args:
            command: Command name (e.g., "build.trigger")
            params: Command parameters
            async_exec: If True, queue for async execution
            
        Returns:
            Execution result (immediate) or execution_id (async)
        """
        params = params or {}
        execution_id = str(uuid.uuid4())[:8]
        
        execution_record = {
            "id": execution_id,
            "command": command,
            "params": params,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        self.logger.info(f"[{execution_id}] Executing: {command}")
        
        if async_exec:
            self.command_queue.put(execution_record)
            return {"execution_id": execution_id, "status": "queued"}
        else:
            return self._execute_sync(execution_record)
    
    def _execute_sync(self, record: Dict) -> Dict:
        """Execute a command synchronously."""
        command = record["command"]
        params = record["params"]
        exec_id = record["id"]
        
        try:
            handler = self._command_handlers.get(command)
            if not handler:
                raise ValueError(f"Unknown command: {command}")
            
            # Create execution context
            self.current_context = ExecutionContext(
                execution_id=exec_id,
                command=command,
                params=params,
                config=self.config_manager
            )
            
            # Execute
            start_time = time.time()
            result = handler(self.current_context)
            elapsed = time.time() - start_time
            
            # Record success
            record["status"] = "completed"
            record["result"] = result
            record["elapsed_ms"] = int(elapsed * 1000)
            
            self.logger.info(f"[{exec_id}] Completed in {elapsed:.2f}s")
            self.event_bus.emit("command_completed", exec_id, result)
            
        except Exception as e:
            record["status"] = "failed"
            record["error"] = str(e)
            self.logger.error(f"[{exec_id}] Failed: {e}")
            self.event_bus.emit("command_failed", exec_id, str(e))
        
        finally:
            self.current_context = None
            self.execution_history.append(record)
        
        return record
    
    def _worker_loop(self):
        """Background worker for async command execution."""
        self.logger.info("Worker loop started")
        
        while self.is_running:
            try:
                record = self.command_queue.get(timeout=1.0)
                
                if record is None:  # Shutdown signal
                    break
                
                self._execute_sync(record)
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Worker error: {e}")
        
        self.logger.info("Worker loop stopped")
    
    # ==================== Built-in Command Handlers ====================
    
    def _cmd_echo(self, ctx: ExecutionContext) -> Dict:
        """Echo command for testing."""
        message = ctx.params.get("message", "Hello from DroidForge!")
        return {"message": message}
    
    def _cmd_config_get(self, ctx: ExecutionContext) -> Dict:
        """Get configuration value."""
        key = ctx.params.get("key")
        if not key:
            return {"error": "Key required"}
        value = self.config_manager.get(key)
        return {"key": key, "value": value}
    
    def _cmd_config_set(self, ctx: ExecutionContext) -> Dict:
        """Set configuration value (live reconfiguration)."""
        key = ctx.params.get("key")
        value = ctx.params.get("value")
        if not key:
            return {"error": "Key required"}
        self.config_manager.set(key, value)
        return {"key": key, "value": value, "status": "updated"}
    
    def _cmd_workflow_run(self, ctx: ExecutionContext) -> Dict:
        """Run a registered workflow."""
        workflow_name = ctx.params.get("workflow")
        if not workflow_name:
            return {"error": "Workflow name required"}
        
        workflow = self._workflow_definitions.get(workflow_name)
        if not workflow:
            return {"error": f"Unknown workflow: {workflow_name}"}
        
        # Execute workflow steps
        results = []
        for step in workflow.get("steps", []):
            step_result = self.execute(
                step["command"],
                step.get("params", {}),
                async_exec=False
            )
            results.append(step_result)
            
            if step_result.get("status") == "failed":
                return {"workflow": workflow_name, "status": "failed", "results": results}
        
        return {"workflow": workflow_name, "status": "completed", "results": results}
    
    def _cmd_system_status(self, ctx: ExecutionContext) -> Dict:
        """Get system status."""
        return {
            "engine_running": self.is_running,
            "queue_size": self.command_queue.qsize(),
            "history_count": len(self.execution_history),
            "registered_commands": list(self._command_handlers.keys()),
            "registered_workflows": list(self._workflow_definitions.keys())
        }
    
    def _cmd_build_trigger(self, ctx: ExecutionContext) -> Dict:
        """Trigger a build via GitHub Actions or local buildozer."""
        target = ctx.params.get("target", "github")
        branch = ctx.params.get("branch", "main")
        
        if target == "github":
            # This would integrate with GitHub API
            return {
                "status": "triggered",
                "target": "github_actions",
                "branch": branch,
                "message": "Build workflow dispatched"
            }
        elif target == "local":
            return {
                "status": "triggered", 
                "target": "local_buildozer",
                "message": "Local build started"
            }
        else:
            return {"error": f"Unknown build target: {target}"}
    
    def _cmd_git_status(self, ctx: ExecutionContext) -> Dict:
        """Get git repository status."""
        # Placeholder - would integrate with git
        return {
            "branch": "main",
            "clean": True,
            "ahead": 0,
            "behind": 0
        }
    
    def _cmd_ai_generate(self, ctx: ExecutionContext) -> Dict:
        """Generate code using AI runtime."""
        prompt = ctx.params.get("prompt", "")
        language = ctx.params.get("language", "python")
        
        # This would integrate with AI module
        return {
            "status": "generated",
            "language": language,
            "prompt": prompt,
            "code": f"# Generated code for: {prompt}\n# TODO: AI integration"
        }
    
    # ==================== Public API ====================
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get execution history."""
        return self.execution_history[-limit:]
    
    def get_status(self) -> Dict:
        """Get engine status."""
        return self._cmd_system_status(None)
    
    def clear_history(self):
        """Clear execution history."""
        self.execution_history.clear()
        self.logger.info("Execution history cleared")
