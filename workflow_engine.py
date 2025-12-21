"""
DroidForge Workflow Engine
==========================
Declarative workflow definition and execution system.
Enables complex multi-step automation with dependency resolution.
"""

import json
import yaml
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import threading
import queue

from utils.logger import get_logger


class StepStatus(Enum):
    """Workflow step status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    id: str
    name: str
    command: str
    params: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    timeout: int = 300
    retry_count: int = 0
    
    # Runtime state
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class WorkflowDefinition:
    """Definition of a complete workflow."""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    variables: Dict[str, Any] = field(default_factory=dict)
    triggers: List[Dict] = field(default_factory=list)
    on_success: Optional[str] = None
    on_failure: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorkflowDefinition':
        """Create workflow from dictionary."""
        steps = []
        for step_data in data.get('steps', []):
            steps.append(WorkflowStep(
                id=step_data['id'],
                name=step_data.get('name', step_data['id']),
                command=step_data['command'],
                params=step_data.get('params', {}),
                depends_on=step_data.get('depends_on', []),
                condition=step_data.get('condition'),
                timeout=step_data.get('timeout', 300),
                retry_count=step_data.get('retry_count', 0)
            ))
        
        return cls(
            id=data['id'],
            name=data.get('name', data['id']),
            description=data.get('description', ''),
            steps=steps,
            variables=data.get('variables', {}),
            triggers=data.get('triggers', []),
            on_success=data.get('on_success'),
            on_failure=data.get('on_failure')
        )
    
    @classmethod
    def from_yaml(cls, yaml_content: str) -> 'WorkflowDefinition':
        """Create workflow from YAML string."""
        data = yaml.safe_load(yaml_content)
        return cls.from_dict(data)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'steps': [
                {
                    'id': s.id,
                    'name': s.name,
                    'command': s.command,
                    'params': s.params,
                    'depends_on': s.depends_on,
                    'condition': s.condition,
                    'timeout': s.timeout,
                    'retry_count': s.retry_count
                }
                for s in self.steps
            ],
            'variables': self.variables,
            'triggers': self.triggers,
            'on_success': self.on_success,
            'on_failure': self.on_failure
        }


class WorkflowRun:
    """A single execution of a workflow."""
    
    def __init__(self, workflow: WorkflowDefinition, run_id: str):
        self.workflow = workflow
        self.run_id = run_id
        self.status = "pending"
        self.started_at = None
        self.completed_at = None
        self.variables = dict(workflow.variables)
        self.step_results: Dict[str, Any] = {}
        
        # Reset step states
        for step in self.workflow.steps:
            step.status = StepStatus.PENDING
            step.result = None
            step.error = None
    
    def get_ready_steps(self) -> List[WorkflowStep]:
        """Get steps that are ready to execute."""
        ready = []
        
        for step in self.workflow.steps:
            if step.status != StepStatus.PENDING:
                continue
            
            # Check dependencies
            deps_satisfied = True
            for dep_id in step.depends_on:
                dep_step = self._get_step(dep_id)
                if dep_step and dep_step.status != StepStatus.SUCCESS:
                    deps_satisfied = False
                    break
            
            if deps_satisfied:
                ready.append(step)
        
        return ready
    
    def _get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by ID."""
        for step in self.workflow.steps:
            if step.id == step_id:
                return step
        return None
    
    def is_complete(self) -> bool:
        """Check if all steps are complete."""
        for step in self.workflow.steps:
            if step.status in (StepStatus.PENDING, StepStatus.RUNNING):
                return False
        return True
    
    def is_success(self) -> bool:
        """Check if workflow completed successfully."""
        for step in self.workflow.steps:
            if step.status == StepStatus.FAILED:
                return False
        return self.is_complete()


class WorkflowEngine:
    """
    Workflow execution engine.
    
    Features:
    - Declarative workflow definitions
    - Dependency resolution
    - Parallel step execution
    - Variable interpolation
    - Conditional execution
    - Retry logic
    """
    
    def __init__(self, engine, config_manager, event_bus):
        self.engine = engine  # DroidForge engine for command execution
        self.config = config_manager
        self.event_bus = event_bus
        self.logger = get_logger("WorkflowEngine")
        
        # Workflow storage
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._runs: Dict[str, WorkflowRun] = {}
        
        # Load built-in workflows
        self._load_builtin_workflows()
    
    def _load_builtin_workflows(self):
        """Load built-in workflow definitions."""
        
        # Build and Deploy workflow
        self.register_workflow(WorkflowDefinition(
            id="build-deploy",
            name="Build and Deploy",
            description="Build APK and deploy to release",
            steps=[
                WorkflowStep(
                    id="lint",
                    name="Run Linter",
                    command="test.lint",
                    params={}
                ),
                WorkflowStep(
                    id="test",
                    name="Run Tests",
                    command="test.run",
                    params={"coverage": True},
                    depends_on=["lint"]
                ),
                WorkflowStep(
                    id="build",
                    name="Build APK",
                    command="build.trigger",
                    params={"target": "android_release"},
                    depends_on=["test"]
                ),
                WorkflowStep(
                    id="deploy",
                    name="Deploy Release",
                    command="deploy.trigger",
                    params={"target": "github_release"},
                    depends_on=["build"]
                )
            ],
            variables={"version": "1.0.0"}
        ))
        
        # Quick Build workflow
        self.register_workflow(WorkflowDefinition(
            id="quick-build",
            name="Quick Build",
            description="Fast debug build without tests",
            steps=[
                WorkflowStep(
                    id="build",
                    name="Build Debug APK",
                    command="build.trigger",
                    params={"target": "android_debug"}
                )
            ]
        ))
        
        # Full CI workflow
        self.register_workflow(WorkflowDefinition(
            id="full-ci",
            name="Full CI Pipeline",
            description="Complete CI/CD pipeline",
            steps=[
                WorkflowStep(
                    id="checkout",
                    name="Checkout Code",
                    command="git.checkout",
                    params={"branch": "main"}
                ),
                WorkflowStep(
                    id="deps",
                    name="Install Dependencies",
                    command="system.install_deps",
                    depends_on=["checkout"]
                ),
                WorkflowStep(
                    id="lint",
                    name="Lint Check",
                    command="test.lint",
                    depends_on=["deps"]
                ),
                WorkflowStep(
                    id="unit-tests",
                    name="Unit Tests",
                    command="test.run",
                    params={"suite": "unit"},
                    depends_on=["deps"]
                ),
                WorkflowStep(
                    id="integration-tests",
                    name="Integration Tests",
                    command="test.run",
                    params={"suite": "integration"},
                    depends_on=["unit-tests"]
                ),
                WorkflowStep(
                    id="build-debug",
                    name="Build Debug",
                    command="build.trigger",
                    params={"target": "android_debug"},
                    depends_on=["lint", "unit-tests"]
                ),
                WorkflowStep(
                    id="build-release",
                    name="Build Release",
                    command="build.trigger",
                    params={"target": "android_release"},
                    depends_on=["integration-tests"]
                )
            ]
        ))
    
    def register_workflow(self, workflow: WorkflowDefinition):
        """Register a workflow definition."""
        self._workflows[workflow.id] = workflow
        self.logger.info(f"Registered workflow: {workflow.id}")
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get a workflow by ID."""
        return self._workflows.get(workflow_id)
    
    def list_workflows(self) -> List[WorkflowDefinition]:
        """List all registered workflows."""
        return list(self._workflows.values())
    
    def run_workflow(self, workflow_id: str, variables: Dict = None) -> WorkflowRun:
        """
        Execute a workflow.
        
        Args:
            workflow_id: ID of workflow to run
            variables: Override workflow variables
            
        Returns:
            WorkflowRun instance
        """
        import uuid
        
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Unknown workflow: {workflow_id}")
        
        run_id = str(uuid.uuid4())[:8]
        run = WorkflowRun(workflow, run_id)
        
        # Apply variable overrides
        if variables:
            run.variables.update(variables)
        
        self._runs[run_id] = run
        
        self.logger.info(f"Starting workflow run: {workflow_id} ({run_id})")
        self.event_bus.emit("workflow_started", workflow_id, run_id)
        
        run.status = "running"
        run.started_at = datetime.now()
        
        # Execute workflow
        self._execute_run(run)
        
        return run
    
    def _execute_run(self, run: WorkflowRun):
        """Execute a workflow run."""
        while not run.is_complete():
            ready_steps = run.get_ready_steps()
            
            if not ready_steps:
                # Deadlock or all remaining steps have failed dependencies
                for step in run.workflow.steps:
                    if step.status == StepStatus.PENDING:
                        step.status = StepStatus.SKIPPED
                break
            
            # Execute ready steps (could be parallelized)
            for step in ready_steps:
                self._execute_step(run, step)
        
        run.status = "success" if run.is_success() else "failed"
        run.completed_at = datetime.now()
        
        self.logger.info(f"Workflow completed: {run.workflow.id} ({run.run_id}) - {run.status}")
        self.event_bus.emit("workflow_completed", run.workflow.id, run.run_id, run.status)
        
        # Execute hooks
        if run.status == "success" and run.workflow.on_success:
            self.engine.execute(run.workflow.on_success, {})
        elif run.status == "failed" and run.workflow.on_failure:
            self.engine.execute(run.workflow.on_failure, {})
    
    def _execute_step(self, run: WorkflowRun, step: WorkflowStep):
        """Execute a single workflow step."""
        self.logger.info(f"Executing step: {step.id} ({step.name})")
        
        step.status = StepStatus.RUNNING
        step.started_at = datetime.now()
        
        self.event_bus.emit("workflow_step_started", run.run_id, step.id)
        
        # Check condition
        if step.condition:
            if not self._evaluate_condition(step.condition, run):
                step.status = StepStatus.SKIPPED
                step.completed_at = datetime.now()
                return
        
        # Interpolate parameters
        params = self._interpolate_params(step.params, run)
        
        # Execute with retry
        attempts = 0
        max_attempts = step.retry_count + 1
        
        while attempts < max_attempts:
            try:
                result = self.engine.execute(step.command, params, async_exec=False)
                
                if result.get('status') == 'completed':
                    step.status = StepStatus.SUCCESS
                    step.result = result.get('result')
                    run.step_results[step.id] = step.result
                    break
                else:
                    step.error = result.get('error', 'Unknown error')
                    attempts += 1
                    
            except Exception as e:
                step.error = str(e)
                attempts += 1
        
        if step.status != StepStatus.SUCCESS:
            step.status = StepStatus.FAILED
        
        step.completed_at = datetime.now()
        
        self.event_bus.emit(
            "workflow_step_completed",
            run.run_id,
            step.id,
            step.status.value
        )
    
    def _interpolate_params(self, params: Dict, run: WorkflowRun) -> Dict:
        """Interpolate variables in parameters."""
        result = {}
        
        for key, value in params.items():
            if isinstance(value, str):
                # Replace ${var} with variable values
                for var_name, var_value in run.variables.items():
                    value = value.replace(f"${{{var_name}}}", str(var_value))
                
                # Replace ${steps.step_id.result} with step results
                for step_id, step_result in run.step_results.items():
                    value = value.replace(
                        f"${{steps.{step_id}.result}}",
                        str(step_result)
                    )
            
            result[key] = value
        
        return result
    
    def _evaluate_condition(self, condition: str, run: WorkflowRun) -> bool:
        """Evaluate a step condition."""
        # Simple condition evaluation
        # Supports: ${var} == "value", ${steps.id.status} == "success"
        
        try:
            # Replace variables
            for var_name, var_value in run.variables.items():
                condition = condition.replace(f"${{{var_name}}}", f'"{var_value}"')
            
            # This is a simplified evaluator - in production, use a proper expression parser
            return eval(condition)
        except Exception as e:
            self.logger.warning(f"Condition evaluation failed: {e}")
            return True  # Default to executing
    
    def get_run(self, run_id: str) -> Optional[WorkflowRun]:
        """Get a workflow run by ID."""
        return self._runs.get(run_id)
    
    def get_run_history(self, workflow_id: str = None, limit: int = 20) -> List[WorkflowRun]:
        """Get workflow run history."""
        runs = list(self._runs.values())
        
        if workflow_id:
            runs = [r for r in runs if r.workflow.id == workflow_id]
        
        return sorted(runs, key=lambda r: r.started_at or datetime.min, reverse=True)[:limit]
