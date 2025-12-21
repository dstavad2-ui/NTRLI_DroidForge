"""
DroidForge Command Processor
============================
Handles command parsing, validation, and routing.
Implements the deterministic command layer for reproducible execution.
"""

import re
import shlex
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from utils.logger import get_logger


class CommandType(Enum):
    """Types of commands supported."""
    BUILTIN = "builtin"
    WORKFLOW = "workflow"
    SHELL = "shell"
    REMOTE = "remote"
    AI = "ai"


@dataclass
class ParsedCommand:
    """Represents a parsed command."""
    raw: str
    command: str
    command_type: CommandType
    params: Dict[str, Any] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
    is_valid: bool = True
    error: Optional[str] = None


class CommandProcessor:
    """
    Command Processor for parsing and validating commands.
    
    Supports multiple command syntaxes:
    - Dot notation: build.trigger --target=github
    - Shell style: @shell ls -la
    - Workflow: @workflow deploy-production
    - AI generation: @ai generate authentication module
    """
    
    # Command patterns
    PATTERNS = {
        'dot_notation': re.compile(r'^([a-z][a-z0-9_.]+)(.*)$', re.IGNORECASE),
        'shell': re.compile(r'^@shell\s+(.+)$', re.IGNORECASE),
        'workflow': re.compile(r'^@workflow\s+(\S+)(.*)$', re.IGNORECASE),
        'ai': re.compile(r'^@ai\s+(\S+)\s*(.*)$', re.IGNORECASE),
        'remote': re.compile(r'^@remote\s+(\S+)\s+(.+)$', re.IGNORECASE),
    }
    
    # Built-in commands
    BUILTIN_COMMANDS = {
        'echo', 'help', 'version', 'status', 'clear', 'history',
        'config.get', 'config.set', 'config.list', 'config.reset',
        'build.trigger', 'build.status', 'build.logs',
        'git.status', 'git.pull', 'git.push', 'git.commit',
        'workflow.run', 'workflow.list', 'workflow.create',
        'ai.generate', 'ai.refactor', 'ai.explain',
        'system.status', 'system.info', 'system.restart',
        'test.run', 'test.list',
        'deploy.trigger', 'deploy.status',
    }
    
    def __init__(self, engine):
        self.engine = engine
        self.logger = get_logger("CommandProcessor")
        
        # Command history for completion
        self._command_history: List[str] = []
        self._history_limit = 1000
        
        # Aliases
        self._aliases: Dict[str, str] = {
            'b': 'build.trigger',
            's': 'system.status',
            'c': 'config.get',
            'h': 'help',
            'g': 'ai.generate',
        }
    
    def parse(self, input_str: str) -> ParsedCommand:
        """
        Parse a command string into structured format.
        
        Args:
            input_str: Raw command string
            
        Returns:
            ParsedCommand object
        """
        input_str = input_str.strip()
        
        if not input_str:
            return ParsedCommand(
                raw=input_str,
                command="",
                command_type=CommandType.BUILTIN,
                is_valid=False,
                error="Empty command"
            )
        
        # Add to history
        self._add_to_history(input_str)
        
        # Expand aliases
        input_str = self._expand_alias(input_str)
        
        # Try each pattern
        if input_str.startswith('@shell'):
            return self._parse_shell(input_str)
        elif input_str.startswith('@workflow'):
            return self._parse_workflow(input_str)
        elif input_str.startswith('@ai'):
            return self._parse_ai(input_str)
        elif input_str.startswith('@remote'):
            return self._parse_remote(input_str)
        else:
            return self._parse_dot_notation(input_str)
    
    def _parse_dot_notation(self, input_str: str) -> ParsedCommand:
        """Parse dot-notation commands like 'build.trigger --target=github'."""
        match = self.PATTERNS['dot_notation'].match(input_str)
        
        if not match:
            return ParsedCommand(
                raw=input_str,
                command=input_str,
                command_type=CommandType.BUILTIN,
                is_valid=False,
                error="Invalid command format"
            )
        
        command = match.group(1).lower()
        args_str = match.group(2).strip()
        
        # Parse arguments
        params, flags = self._parse_args(args_str)
        
        return ParsedCommand(
            raw=input_str,
            command=command,
            command_type=CommandType.BUILTIN,
            params=params,
            flags=flags,
            is_valid=True
        )
    
    def _parse_shell(self, input_str: str) -> ParsedCommand:
        """Parse shell commands like '@shell ls -la'."""
        match = self.PATTERNS['shell'].match(input_str)
        
        if not match:
            return ParsedCommand(
                raw=input_str,
                command="shell",
                command_type=CommandType.SHELL,
                is_valid=False,
                error="Invalid shell command"
            )
        
        shell_cmd = match.group(1)
        
        return ParsedCommand(
            raw=input_str,
            command="shell",
            command_type=CommandType.SHELL,
            params={"cmd": shell_cmd},
            is_valid=True
        )
    
    def _parse_workflow(self, input_str: str) -> ParsedCommand:
        """Parse workflow commands like '@workflow deploy-prod --env=staging'."""
        match = self.PATTERNS['workflow'].match(input_str)
        
        if not match:
            return ParsedCommand(
                raw=input_str,
                command="workflow",
                command_type=CommandType.WORKFLOW,
                is_valid=False,
                error="Invalid workflow command"
            )
        
        workflow_name = match.group(1)
        args_str = match.group(2).strip()
        params, flags = self._parse_args(args_str)
        params["workflow"] = workflow_name
        
        return ParsedCommand(
            raw=input_str,
            command="workflow.run",
            command_type=CommandType.WORKFLOW,
            params=params,
            flags=flags,
            is_valid=True
        )
    
    def _parse_ai(self, input_str: str) -> ParsedCommand:
        """Parse AI commands like '@ai generate user authentication'."""
        match = self.PATTERNS['ai'].match(input_str)
        
        if not match:
            return ParsedCommand(
                raw=input_str,
                command="ai",
                command_type=CommandType.AI,
                is_valid=False,
                error="Invalid AI command"
            )
        
        action = match.group(1).lower()
        prompt = match.group(2).strip()
        
        return ParsedCommand(
            raw=input_str,
            command=f"ai.{action}",
            command_type=CommandType.AI,
            params={"action": action, "prompt": prompt},
            is_valid=True
        )
    
    def _parse_remote(self, input_str: str) -> ParsedCommand:
        """Parse remote execution commands like '@remote worker-1 run-tests'."""
        match = self.PATTERNS['remote'].match(input_str)
        
        if not match:
            return ParsedCommand(
                raw=input_str,
                command="remote",
                command_type=CommandType.REMOTE,
                is_valid=False,
                error="Invalid remote command"
            )
        
        target = match.group(1)
        remote_cmd = match.group(2)
        
        return ParsedCommand(
            raw=input_str,
            command="remote.execute",
            command_type=CommandType.REMOTE,
            params={"target": target, "command": remote_cmd},
            is_valid=True
        )
    
    def _parse_args(self, args_str: str) -> Tuple[Dict[str, Any], List[str]]:
        """
        Parse command arguments.
        
        Supports:
        - --key=value
        - --key value
        - --flag (boolean)
        - -f (short flag)
        - positional args
        """
        params = {}
        flags = []
        positional = []
        
        if not args_str:
            return params, flags
        
        try:
            tokens = shlex.split(args_str)
        except ValueError:
            tokens = args_str.split()
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.startswith('--'):
                if '=' in token:
                    # --key=value
                    key, value = token[2:].split('=', 1)
                    params[key] = self._parse_value(value)
                elif i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                    # --key value
                    key = token[2:]
                    params[key] = self._parse_value(tokens[i + 1])
                    i += 1
                else:
                    # --flag
                    flags.append(token[2:])
            elif token.startswith('-') and len(token) == 2:
                # -f (short flag)
                flags.append(token[1:])
            else:
                # Positional argument
                positional.append(token)
            
            i += 1
        
        # Add positional args
        if positional:
            params['_positional'] = positional
        
        return params, flags
    
    def _parse_value(self, value: str) -> Any:
        """Parse a value string into appropriate type."""
        # Boolean
        if value.lower() in ('true', 'yes', 'on', '1'):
            return True
        if value.lower() in ('false', 'no', 'off', '0'):
            return False
        
        # Number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        
        # String
        return value
    
    def _expand_alias(self, input_str: str) -> str:
        """Expand command aliases."""
        parts = input_str.split(None, 1)
        if parts and parts[0] in self._aliases:
            expanded = self._aliases[parts[0]]
            if len(parts) > 1:
                return f"{expanded} {parts[1]}"
            return expanded
        return input_str
    
    def _add_to_history(self, command: str):
        """Add command to history."""
        self._command_history.append(command)
        if len(self._command_history) > self._history_limit:
            self._command_history = self._command_history[-self._history_limit:]
    
    def get_history(self, limit: int = 50) -> List[str]:
        """Get command history."""
        return self._command_history[-limit:]
    
    def add_alias(self, alias: str, command: str):
        """Add a command alias."""
        self._aliases[alias] = command
    
    def get_completions(self, partial: str) -> List[str]:
        """
        Get command completions for partial input.
        
        Args:
            partial: Partial command string
            
        Returns:
            List of possible completions
        """
        completions = []
        partial_lower = partial.lower()
        
        # Match built-in commands
        for cmd in self.BUILTIN_COMMANDS:
            if cmd.startswith(partial_lower):
                completions.append(cmd)
        
        # Match aliases
        for alias in self._aliases:
            if alias.startswith(partial_lower):
                completions.append(alias)
        
        # Match history
        for hist_cmd in reversed(self._command_history):
            if hist_cmd.lower().startswith(partial_lower):
                if hist_cmd not in completions:
                    completions.append(hist_cmd)
        
        return completions[:20]  # Limit completions
    
    def validate(self, parsed: ParsedCommand) -> ParsedCommand:
        """
        Validate a parsed command.
        
        Args:
            parsed: ParsedCommand to validate
            
        Returns:
            ParsedCommand with validation results
        """
        if not parsed.is_valid:
            return parsed
        
        # Check if command exists
        if parsed.command_type == CommandType.BUILTIN:
            if parsed.command not in self.BUILTIN_COMMANDS:
                # Check if it's a registered command in engine
                if not hasattr(self.engine, '_command_handlers'):
                    parsed.is_valid = False
                    parsed.error = f"Unknown command: {parsed.command}"
        
        return parsed
