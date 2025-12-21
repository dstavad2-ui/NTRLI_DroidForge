"""
DroidForge AI Runtime
=====================
Standalone AI execution environment for code synthesis and automation.
Implements a modular, local-first AI system.
"""

import re
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from utils.logger import get_logger
from .code_generator import CodeGenerator, Language


class TaskType(Enum):
    """Types of AI tasks."""
    GENERATE = "generate"
    REFACTOR = "refactor"
    EXPLAIN = "explain"
    ANALYZE = "analyze"
    COMPLETE = "complete"
    FIX = "fix"


@dataclass
class AITask:
    """Represents an AI task."""
    task_type: TaskType
    prompt: str
    context: Dict[str, Any] = None
    language: Language = Language.PYTHON
    
    def to_dict(self) -> Dict:
        return {
            "task_type": self.task_type.value,
            "prompt": self.prompt,
            "context": self.context,
            "language": self.language.value
        }


@dataclass
class AIResponse:
    """Response from AI processing."""
    success: bool
    result: Any
    task_type: TaskType
    processing_time_ms: int
    metadata: Dict[str, Any] = None


class AIRuntime:
    """
    AI Runtime for DroidForge.
    
    This is a standalone AI system that provides:
    - Code generation based on prompts
    - Code analysis and explanation
    - Refactoring suggestions
    - Pattern-based code completion
    
    Note: This is an independent implementation, not using
    any third-party AI services or proprietary APIs.
    """
    
    def __init__(self, config_manager, event_bus):
        self.config = config_manager
        self.event_bus = event_bus
        self.logger = get_logger("AIRuntime")
        
        # Initialize components
        self.code_generator = CodeGenerator(config_manager)
        
        # Task handlers
        self._handlers: Dict[TaskType, Callable] = {
            TaskType.GENERATE: self._handle_generate,
            TaskType.REFACTOR: self._handle_refactor,
            TaskType.EXPLAIN: self._handle_explain,
            TaskType.ANALYZE: self._handle_analyze,
            TaskType.COMPLETE: self._handle_complete,
            TaskType.FIX: self._handle_fix,
        }
        
        # Pattern matchers for intent detection
        self._patterns = self._compile_patterns()
        
        self.logger.info("AI Runtime initialized")
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for intent detection."""
        return {
            "create_class": re.compile(
                r"(?:create|generate|make)\s+(?:a\s+)?(?:new\s+)?class\s+(?:called\s+)?(\w+)",
                re.IGNORECASE
            ),
            "create_function": re.compile(
                r"(?:create|generate|make)\s+(?:a\s+)?(?:new\s+)?function\s+(?:called\s+)?(\w+)",
                re.IGNORECASE
            ),
            "create_screen": re.compile(
                r"(?:create|generate|make)\s+(?:a\s+)?(?:new\s+)?screen\s+(?:called\s+|for\s+)?(\w+)",
                re.IGNORECASE
            ),
            "explain": re.compile(
                r"(?:explain|describe|what\s+(?:is|does))\s+(.+)",
                re.IGNORECASE
            ),
            "refactor": re.compile(
                r"(?:refactor|improve|optimize|clean\s+up)\s+(.+)",
                re.IGNORECASE
            ),
            "fix": re.compile(
                r"(?:fix|debug|solve|repair)\s+(.+)",
                re.IGNORECASE
            ),
        }
    
    def process(self, task: AITask) -> AIResponse:
        """
        Process an AI task.
        
        Args:
            task: AITask to process
            
        Returns:
            AIResponse with results
        """
        start_time = datetime.now()
        
        self.logger.info(f"Processing AI task: {task.task_type.value}")
        self.event_bus.emit("ai_task_started", task.task_type.value)
        
        handler = self._handlers.get(task.task_type)
        if not handler:
            return AIResponse(
                success=False,
                result={"error": f"Unknown task type: {task.task_type}"},
                task_type=task.task_type,
                processing_time_ms=0
            )
        
        try:
            result = handler(task)
            success = True
        except Exception as e:
            self.logger.error(f"AI task failed: {e}")
            result = {"error": str(e)}
            success = False
        
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        response = AIResponse(
            success=success,
            result=result,
            task_type=task.task_type,
            processing_time_ms=elapsed_ms
        )
        
        self.event_bus.emit("ai_task_completed", task.task_type.value, success)
        
        return response
    
    def process_prompt(self, prompt: str, context: Dict = None) -> AIResponse:
        """
        Process a natural language prompt.
        
        Args:
            prompt: Natural language instruction
            context: Additional context
            
        Returns:
            AIResponse with results
        """
        # Detect intent from prompt
        task_type, extracted_data = self._detect_intent(prompt)
        
        task = AITask(
            task_type=task_type,
            prompt=prompt,
            context={**(context or {}), **extracted_data}
        )
        
        return self.process(task)
    
    def _detect_intent(self, prompt: str) -> tuple[TaskType, Dict]:
        """Detect intent from natural language prompt."""
        extracted = {}
        
        # Check patterns
        for pattern_name, pattern in self._patterns.items():
            match = pattern.search(prompt)
            if match:
                extracted["match"] = match.group(1) if match.groups() else None
                
                if pattern_name.startswith("create_"):
                    return TaskType.GENERATE, {
                        "generate_type": pattern_name.replace("create_", ""),
                        "name": extracted.get("match")
                    }
                elif pattern_name == "explain":
                    return TaskType.EXPLAIN, {"target": extracted.get("match")}
                elif pattern_name == "refactor":
                    return TaskType.REFACTOR, {"target": extracted.get("match")}
                elif pattern_name == "fix":
                    return TaskType.FIX, {"target": extracted.get("match")}
        
        # Default to generate
        return TaskType.GENERATE, {}
    
    def _handle_generate(self, task: AITask) -> Dict:
        """Handle code generation tasks."""
        context = task.context or {}
        generate_type = context.get("generate_type", "generic")
        name = context.get("name", "Generated")
        
        if generate_type == "class":
            result = self.code_generator.generate_class(
                class_name=name,
                description=task.prompt
            )
        elif generate_type == "function":
            result = self.code_generator.generate(
                "python_function",
                function_name=name,
                params="",
                return_type="None",
                docstring=task.prompt,
                args_doc="",
                return_doc="None",
                body="pass"
            )
        elif generate_type == "screen":
            result = self.code_generator.generate_kivy_screen(
                screen_name=name,
                description=task.prompt
            )
        else:
            # Generic generation based on prompt analysis
            result = self._generate_from_prompt(task.prompt)
        
        return {
            "type": "generated_code",
            "language": result.language.value,
            "code": result.code,
            "description": result.description
        }
    
    def _generate_from_prompt(self, prompt: str):
        """Generate code from a free-form prompt."""
        # Analyze prompt for keywords
        prompt_lower = prompt.lower()
        
        if "api" in prompt_lower or "endpoint" in prompt_lower:
            return self._generate_api_handler(prompt)
        elif "test" in prompt_lower:
            return self._generate_test(prompt)
        elif "config" in prompt_lower:
            return self._generate_config(prompt)
        else:
            # Default: generate a utility function
            return self.code_generator.generate(
                "python_function",
                function_name="generated_function",
                params="*args, **kwargs",
                return_type="Any",
                docstring=prompt,
                args_doc="args: Variable arguments\n        kwargs: Keyword arguments",
                return_doc="Result based on implementation",
                body=f"# TODO: Implement based on: {prompt}\n    raise NotImplementedError()"
            )
    
    def _generate_api_handler(self, prompt: str):
        """Generate an API handler."""
        code = '''"""
API Handler - Generated
"""

from typing import Dict, Any
import json


class APIHandler:
    """Handle API requests."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
    
    async def request(self, method: str, endpoint: str, 
                      data: Dict = None) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
        """
        # TODO: Implement actual HTTP request
        url = f"{self.base_url}/{endpoint}"
        
        return {
            "status": "success",
            "url": url,
            "method": method
        }
    
    async def get(self, endpoint: str) -> Dict[str, Any]:
        """GET request."""
        return await self.request("GET", endpoint)
    
    async def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """POST request."""
        return await self.request("POST", endpoint, data)
'''
        from .code_generator import GeneratedCode
        return GeneratedCode(
            language=Language.PYTHON,
            code=code,
            description="API Handler class"
        )
    
    def _generate_test(self, prompt: str):
        """Generate test code."""
        code = '''"""
Unit Tests - Generated
"""

import unittest


class TestGenerated(unittest.TestCase):
    """Generated test cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def tearDown(self):
        """Tear down test fixtures."""
        pass
    
    def test_example(self):
        """Example test case."""
        # TODO: Implement test based on requirements
        self.assertTrue(True)
    
    def test_edge_case(self):
        """Test edge cases."""
        # TODO: Add edge case tests
        pass


if __name__ == '__main__':
    unittest.main()
'''
        from .code_generator import GeneratedCode
        return GeneratedCode(
            language=Language.PYTHON,
            code=code,
            description="Unit test template"
        )
    
    def _generate_config(self, prompt: str):
        """Generate configuration code."""
        code = '''"""
Configuration Module - Generated
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Application configuration manager."""
    
    DEFAULTS = {
        "app_name": "Application",
        "debug": False,
        "log_level": "INFO",
    }
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else None
        self._config: Dict[str, Any] = dict(self.DEFAULTS)
        
        if self.config_path and self.config_path.exists():
            self.load()
    
    def load(self):
        """Load configuration from file."""
        if self.config_path:
            with open(self.config_path) as f:
                self._config.update(json.load(f))
    
    def save(self):
        """Save configuration to file."""
        if self.config_path:
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self._config[key] = value
'''
        from .code_generator import GeneratedCode
        return GeneratedCode(
            language=Language.PYTHON,
            code=code,
            description="Configuration manager"
        )
    
    def _handle_refactor(self, task: AITask) -> Dict:
        """Handle refactoring tasks."""
        code = task.context.get("code", "")
        operation = task.context.get("operation", "format")
        
        refactored, changes = self.code_generator.refactor_code(
            code, operation, **task.context
        )
        
        return {
            "type": "refactored_code",
            "code": refactored,
            "changes": changes
        }
    
    def _handle_explain(self, task: AITask) -> Dict:
        """Handle code explanation tasks."""
        code = task.context.get("code", "")
        
        if code:
            analysis = self.code_generator.analyze_code(code)
            
            explanation = f"""Code Analysis:
- Lines of code: {analysis.get('lines', 0)}
- Classes: {', '.join(analysis.get('classes', [])) or 'None'}
- Functions: {', '.join(analysis.get('functions', [])) or 'None'}
- Imports: {len(analysis.get('imports', []))} modules
- Complexity: {analysis.get('complexity', 'unknown')}
"""
            return {
                "type": "explanation",
                "text": explanation,
                "analysis": analysis
            }
        
        return {
            "type": "explanation",
            "text": f"Explanation for: {task.prompt}",
            "note": "Provide code in context for detailed analysis"
        }
    
    def _handle_analyze(self, task: AITask) -> Dict:
        """Handle code analysis tasks."""
        code = task.context.get("code", "")
        language = task.language
        
        analysis = self.code_generator.analyze_code(code, language)
        
        return {
            "type": "analysis",
            "results": analysis
        }
    
    def _handle_complete(self, task: AITask) -> Dict:
        """Handle code completion tasks."""
        code = task.context.get("code", "")
        cursor_position = task.context.get("cursor", len(code))
        
        # Simple completion based on context
        completions = self._generate_completions(code, cursor_position)
        
        return {
            "type": "completions",
            "suggestions": completions
        }
    
    def _generate_completions(self, code: str, cursor: int) -> List[str]:
        """Generate code completions."""
        completions = []
        
        # Get line at cursor
        lines = code[:cursor].split('\n')
        current_line = lines[-1] if lines else ""
        
        # Basic keyword completions
        if current_line.strip().startswith("def"):
            completions.extend(["__init__(self):", "__str__(self):"])
        elif current_line.strip().startswith("class"):
            completions.extend([":", "(object):"])
        elif "import" in current_line:
            completions.extend(["os", "sys", "json", "typing"])
        
        return completions[:10]
    
    def _handle_fix(self, task: AITask) -> Dict:
        """Handle bug fixing tasks."""
        code = task.context.get("code", "")
        error = task.context.get("error", "")
        
        # Simple fixes based on common errors
        fixes = []
        fixed_code = code
        
        if "IndentationError" in error:
            # Fix indentation
            fixed_code = self._fix_indentation(code)
            fixes.append("Fixed indentation")
        
        if "NameError" in error:
            fixes.append("Check for undefined variables or missing imports")
        
        if "SyntaxError" in error:
            fixes.append("Check for missing colons, brackets, or quotes")
        
        return {
            "type": "fix",
            "original_error": error,
            "fixed_code": fixed_code,
            "fixes_applied": fixes,
            "suggestions": [
                "Review the error message carefully",
                "Check line numbers mentioned in the error",
                "Ensure all imports are present"
            ]
        }
    
    def _fix_indentation(self, code: str) -> str:
        """Fix common indentation issues."""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Convert tabs to spaces
            line = line.replace('\t', '    ')
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
