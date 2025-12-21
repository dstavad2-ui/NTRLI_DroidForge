"""
DroidForge Code Generator
=========================
AI-powered code generation and transformation engine.
Operates as a standalone module without third-party dependencies.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from utils.logger import get_logger


class Language(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    KOTLIN = "kotlin"
    JAVA = "java"
    XML = "xml"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"


@dataclass
class GeneratedCode:
    """Result of code generation."""
    language: Language
    code: str
    filename: Optional[str] = None
    description: Optional[str] = None
    imports: List[str] = None
    dependencies: List[str] = None


class CodeTemplate:
    """Base code template for generation."""
    
    def __init__(self, name: str, language: Language, template: str):
        self.name = name
        self.language = language
        self.template = template
    
    def render(self, **kwargs) -> str:
        """Render template with variables."""
        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f"{{{{ {key} }}}}", str(value))
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result


class CodeGenerator:
    """
    Code generation engine for DroidForge.
    
    Capabilities:
    - Template-based code generation
    - Code pattern recognition
    - Boilerplate generation
    - Code transformation
    - Documentation generation
    """
    
    def __init__(self, config_manager=None):
        self.config = config_manager
        self.logger = get_logger("CodeGenerator")
        
        # Initialize templates
        self._templates: Dict[str, CodeTemplate] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load built-in code templates."""
        
        # Python class template
        self._templates["python_class"] = CodeTemplate(
            name="Python Class",
            language=Language.PYTHON,
            template='''"""
{{ description }}
"""

from typing import Dict, List, Optional, Any


class {{ class_name }}:
    """{{ class_doc }}"""
    
    def __init__(self{{ init_params }}):
        """Initialize {{ class_name }}."""
        {{ init_body }}
    
    {{ methods }}
'''
        )
        
        # Python function template
        self._templates["python_function"] = CodeTemplate(
            name="Python Function",
            language=Language.PYTHON,
            template='''def {{ function_name }}({{ params }}) -> {{ return_type }}:
    """
    {{ docstring }}
    
    Args:
        {{ args_doc }}
    
    Returns:
        {{ return_doc }}
    """
    {{ body }}
'''
        )
        
        # Kivy screen template
        self._templates["kivy_screen"] = CodeTemplate(
            name="Kivy Screen",
            language=Language.PYTHON,
            template='''"""
{{ screen_name }} Screen
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.screen import MDScreen


class {{ screen_class }}(MDScreen):
    """{{ screen_doc }}"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "{{ screen_name_lower }}"
    
    def on_enter(self):
        """Called when screen is displayed."""
        {{ on_enter_body }}
    
    def on_leave(self):
        """Called when leaving screen."""
        pass
'''
        )
        
        # Command handler template
        self._templates["command_handler"] = CodeTemplate(
            name="Command Handler",
            language=Language.PYTHON,
            template='''def _cmd_{{ command_name }}(self, ctx: ExecutionContext) -> Dict:
    """
    {{ command_doc }}
    
    Args:
        ctx: Execution context with parameters
        
    Returns:
        Command result dictionary
    """
    {{ param_extraction }}
    
    {{ command_body }}
    
    return {
        "status": "completed",
        {{ result_fields }}
    }
'''
        )
        
        # GitHub Actions workflow template
        self._templates["github_workflow"] = CodeTemplate(
            name="GitHub Actions Workflow",
            language=Language.YAML,
            template='''name: {{ workflow_name }}

on:
  {{ triggers }}

jobs:
  {{ job_name }}:
    runs-on: {{ runs_on }}
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      {{ steps }}
'''
        )
        
        # Buildozer spec template
        self._templates["buildozer_spec"] = CodeTemplate(
            name="Buildozer Spec",
            language=Language.PYTHON,  # Actually INI but close enough
            template='''[app]
title = {{ app_title }}
package.name = {{ package_name }}
package.domain = {{ package_domain }}
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
version = {{ version }}
requirements = {{ requirements }}
orientation = {{ orientation }}
fullscreen = 0
android.permissions = {{ permissions }}
android.api = {{ android_api }}
android.minapi = {{ android_minapi }}
android.archs = {{ archs }}
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
'''
        )
    
    def generate(self, template_name: str, **kwargs) -> GeneratedCode:
        """
        Generate code from a template.
        
        Args:
            template_name: Name of template to use
            **kwargs: Template variables
            
        Returns:
            GeneratedCode object
        """
        if template_name not in self._templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self._templates[template_name]
        code = template.render(**kwargs)
        
        return GeneratedCode(
            language=template.language,
            code=code,
            description=f"Generated from {template_name} template"
        )
    
    def generate_class(self, class_name: str, 
                      description: str = "",
                      methods: List[Dict] = None,
                      parent_class: str = None) -> GeneratedCode:
        """
        Generate a Python class.
        
        Args:
            class_name: Name of the class
            description: Class description
            methods: List of method definitions
            parent_class: Optional parent class
            
        Returns:
            GeneratedCode object
        """
        methods_code = ""
        if methods:
            for method in methods:
                method_code = self._generate_method(method)
                methods_code += method_code + "\n\n    "
        
        init_body = "pass"
        init_params = ""
        
        return self.generate(
            "python_class",
            class_name=class_name,
            description=description,
            class_doc=description,
            init_params=init_params,
            init_body=init_body,
            methods=methods_code.strip()
        )
    
    def _generate_method(self, method_def: Dict) -> str:
        """Generate a method from definition."""
        name = method_def.get('name', 'method')
        params = method_def.get('params', [])
        return_type = method_def.get('return_type', 'None')
        body = method_def.get('body', 'pass')
        docstring = method_def.get('docstring', '')
        
        param_str = ', '.join(params) if params else ''
        
        return f'''def {name}(self, {param_str}) -> {return_type}:
        """{docstring}"""
        {body}'''
    
    def generate_kivy_screen(self, screen_name: str,
                            description: str = "") -> GeneratedCode:
        """
        Generate a Kivy/KivyMD screen class.
        
        Args:
            screen_name: Name of the screen
            description: Screen description
            
        Returns:
            GeneratedCode object
        """
        class_name = ''.join(word.title() for word in screen_name.split('_'))
        if not class_name.endswith('Screen'):
            class_name += 'Screen'
        
        return self.generate(
            "kivy_screen",
            screen_name=screen_name.replace('_', ' ').title(),
            screen_class=class_name,
            screen_name_lower=screen_name.lower(),
            screen_doc=description or f"{screen_name} screen",
            on_enter_body="pass"
        )
    
    def generate_command_handler(self, command_name: str,
                                 params: List[str] = None,
                                 description: str = "") -> GeneratedCode:
        """
        Generate a command handler method.
        
        Args:
            command_name: Name of the command
            params: Expected parameters
            description: Command description
            
        Returns:
            GeneratedCode object
        """
        param_extraction = ""
        if params:
            for param in params:
                param_extraction += f'{param} = ctx.params.get("{param}")\n        '
        else:
            param_extraction = "# No parameters expected"
        
        return self.generate(
            "command_handler",
            command_name=command_name.replace('.', '_').replace('-', '_'),
            command_doc=description or f"Handle {command_name} command",
            param_extraction=param_extraction.strip(),
            command_body="# TODO: Implement command logic",
            result_fields='"message": "Command executed"'
        )
    
    def generate_workflow(self, name: str,
                         triggers: List[str] = None,
                         steps: List[Dict] = None) -> GeneratedCode:
        """
        Generate a GitHub Actions workflow.
        
        Args:
            name: Workflow name
            triggers: Trigger events
            steps: Workflow steps
            
        Returns:
            GeneratedCode object
        """
        triggers_yaml = ""
        if triggers:
            for trigger in triggers:
                triggers_yaml += f"{trigger}:\n  "
        else:
            triggers_yaml = "push:\n    branches: [main]"
        
        steps_yaml = ""
        if steps:
            for step in steps:
                step_name = step.get('name', 'Step')
                step_run = step.get('run', 'echo "Hello"')
                steps_yaml += f'- name: {step_name}\n        run: {step_run}\n      '
        
        return self.generate(
            "github_workflow",
            workflow_name=name,
            triggers=triggers_yaml,
            job_name="build",
            runs_on="ubuntu-latest",
            steps=steps_yaml.strip()
        )
    
    def analyze_code(self, code: str, language: Language = Language.PYTHON) -> Dict:
        """
        Analyze code structure.
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            Analysis results
        """
        if language == Language.PYTHON:
            return self._analyze_python(code)
        
        return {"error": f"Analysis not supported for {language.value}"}
    
    def _analyze_python(self, code: str) -> Dict:
        """Analyze Python code."""
        results = {
            "classes": [],
            "functions": [],
            "imports": [],
            "lines": len(code.split('\n')),
            "complexity": "low"
        }
        
        # Find imports
        import_pattern = r'^(?:from\s+\S+\s+)?import\s+.+$'
        results["imports"] = re.findall(import_pattern, code, re.MULTILINE)
        
        # Find classes
        class_pattern = r'^class\s+(\w+)'
        results["classes"] = re.findall(class_pattern, code, re.MULTILINE)
        
        # Find functions
        func_pattern = r'^def\s+(\w+)'
        results["functions"] = re.findall(func_pattern, code, re.MULTILINE)
        
        # Estimate complexity
        if len(results["classes"]) > 5 or len(results["functions"]) > 20:
            results["complexity"] = "high"
        elif len(results["classes"]) > 2 or len(results["functions"]) > 10:
            results["complexity"] = "medium"
        
        return results
    
    def refactor_code(self, code: str, operation: str, 
                     **kwargs) -> Tuple[str, List[str]]:
        """
        Refactor code with specified operation.
        
        Args:
            code: Source code
            operation: Refactoring operation
            **kwargs: Operation-specific arguments
            
        Returns:
            Tuple of (refactored code, list of changes)
        """
        changes = []
        
        if operation == "rename":
            old_name = kwargs.get("old_name")
            new_name = kwargs.get("new_name")
            if old_name and new_name:
                count = code.count(old_name)
                code = code.replace(old_name, new_name)
                changes.append(f"Renamed '{old_name}' to '{new_name}' ({count} occurrences)")
        
        elif operation == "add_docstrings":
            # Simple docstring addition for functions
            pattern = r'(def\s+\w+\([^)]*\):)\n(\s+)([^"\'])'
            replacement = r'\1\n\2"""TODO: Add docstring."""\n\2\3'
            code, count = re.subn(pattern, replacement, code)
            changes.append(f"Added {count} docstrings")
        
        elif operation == "format":
            # Basic formatting (in practice, would use black/autopep8)
            code = re.sub(r'\n{3,}', '\n\n', code)
            changes.append("Normalized whitespace")
        
        return code, changes
    
    def get_template_names(self) -> List[str]:
        """Get list of available templates."""
        return list(self._templates.keys())
