"""
DroidForge Execution Context
============================
Context object passed to command handlers during execution.
Provides access to configuration, logging, and execution state.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from utils.logger import get_logger


@dataclass
class ExecutionContext:
    """
    Execution context for command handlers.
    
    Provides:
    - Access to command parameters
    - Configuration values
    - Logging
    - State management
    - Progress reporting
    """
    
    execution_id: str
    command: str
    params: Dict[str, Any]
    config: Any  # ConfigManager
    
    # Execution state
    started_at: datetime = field(default_factory=datetime.now)
    progress: float = 0.0
    status: str = "running"
    
    # Output collection
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.logger = get_logger(f"Exec-{self.execution_id[:8]}")
    
    def log(self, message: str, level: str = "info"):
        """Log a message within this execution context."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level.upper()}] {message}"
        self.logs.append(log_entry)
        
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(message)
    
    def set_progress(self, progress: float, message: str = None):
        """Update execution progress (0.0 to 1.0)."""
        self.progress = max(0.0, min(1.0, progress))
        if message:
            self.log(f"Progress {self.progress:.0%}: {message}")
    
    def add_output(self, output_type: str, data: Any, name: str = None):
        """Add an output artifact."""
        self.outputs.append({
            "type": output_type,
            "name": name or f"output_{len(self.outputs)}",
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_param(self, key: str, default: Any = None) -> Any:
        """Get a command parameter."""
        return self.params.get(key, default)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        if self.config:
            return self.config.get(key, default)
        return default
    
    def set_metadata(self, key: str, value: Any):
        """Set execution metadata."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get execution metadata."""
        return self.metadata.get(key, default)
    
    def fail(self, error: str):
        """Mark execution as failed."""
        self.status = "failed"
        self.log(error, "error")
        raise ExecutionError(error)
    
    def complete(self, result: Any = None):
        """Mark execution as complete."""
        self.status = "completed"
        self.progress = 1.0
        if result:
            self.add_output("result", result)
    
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        return (datetime.now() - self.started_at).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "execution_id": self.execution_id,
            "command": self.command,
            "params": self.params,
            "started_at": self.started_at.isoformat(),
            "progress": self.progress,
            "status": self.status,
            "outputs": self.outputs,
            "logs": self.logs,
            "metadata": self.metadata,
            "elapsed_seconds": self.elapsed_seconds()
        }


class ExecutionError(Exception):
    """Exception raised when command execution fails."""
    pass


class ExecutionContextManager:
    """
    Manages multiple execution contexts.
    
    Tracks active and completed executions for monitoring and debugging.
    """
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self._active: Dict[str, ExecutionContext] = {}
        self._completed: List[ExecutionContext] = []
        self.logger = get_logger("ContextManager")
    
    def create(self, command: str, params: Dict[str, Any], 
               config: Any) -> ExecutionContext:
        """Create a new execution context."""
        ctx = ExecutionContext(
            execution_id=str(uuid.uuid4()),
            command=command,
            params=params,
            config=config
        )
        self._active[ctx.execution_id] = ctx
        self.logger.debug(f"Created context: {ctx.execution_id[:8]}")
        return ctx
    
    def complete(self, execution_id: str):
        """Move context from active to completed."""
        if execution_id in self._active:
            ctx = self._active.pop(execution_id)
            self._completed.append(ctx)
            
            # Trim history
            if len(self._completed) > self.max_history:
                self._completed = self._completed[-self.max_history:]
            
            self.logger.debug(f"Completed context: {execution_id[:8]}")
    
    def get_active(self, execution_id: str) -> Optional[ExecutionContext]:
        """Get an active execution context."""
        return self._active.get(execution_id)
    
    def get_all_active(self) -> List[ExecutionContext]:
        """Get all active execution contexts."""
        return list(self._active.values())
    
    def get_history(self, limit: int = 50) -> List[ExecutionContext]:
        """Get completed execution history."""
        return self._completed[-limit:]
    
    def cancel(self, execution_id: str) -> bool:
        """Cancel an active execution."""
        if execution_id in self._active:
            ctx = self._active[execution_id]
            ctx.status = "cancelled"
            self.complete(execution_id)
            return True
        return False
