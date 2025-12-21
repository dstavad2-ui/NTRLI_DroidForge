# DroidForge Console

<div align="center">

![DroidForge Logo](assets/icon.png)

**A self-contained Android-native development, automation, and orchestration tool**

[![Build Status](https://github.com/yourusername/droidforge/workflows/Build%20DroidForge%20APK/badge.svg)](https://github.com/yourusername/droidforge/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Android 5.0+](https://img.shields.io/badge/Android-5.0%2B-brightgreen.svg)](https://www.android.com/)

</div>

---

## Overview

DroidForge Console is a mobile-first autonomous development console designed for end-to-end software creation, deployment, marketing enablement, and sustainability management—all operated entirely from a mobile device.

The system is architected as an **independent execution environment**, not a wrapper, clone, or redistributed service. All functionality is either natively implemented or accessed through lawful, user-initiated programmatic interfaces.

## Key Features

### 🎛️ Command-Orchestrated Automation
All actions—code generation, repository operations, builds, tests, deployments—execute through deterministic commands. Human input is limited to intent definition; execution is fully automated.

### ⚡ Live-Configurable Environment
Real-time system reconfiguration without rebuilds or redeployments. Configuration changes propagate instantly through a declarative command layer.

### 🤖 Native AI Runtime
Standalone AI engine for code synthesis, refactoring, dependency reasoning, and workflow generation—operating fully within the app's boundary.

### 🔄 GitHub Integration
Direct repository automation and remote execution control via GitHub Actions. Issue authenticated commands, trigger builds, run tests, and retrieve outputs.

### 📱 Mobile-First Design
Built with Kivy/KivyMD for a responsive, native-feeling Android experience.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DroidForge Console                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   UI Layer  │  │  Event Bus  │  │  Config Manager     │  │
│  │  (KivyMD)   │◄─┤  (Pub/Sub)  ├─►│  (Live Updates)     │  │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────┘  │
│         │                │                                   │
│  ┌──────▼────────────────▼──────────────────────────────┐   │
│  │              Core Engine (Command Processor)          │   │
│  │  • Deterministic execution    • Proof-of-work logs   │   │
│  │  • Workflow orchestration     • State management     │   │
│  └──────┬──────────────┬─────────────────┬──────────────┘   │
│         │              │                 │                   │
│  ┌──────▼──────┐ ┌─────▼─────┐  ┌───────▼───────┐          │
│  │  Automation │ │ AI Runtime │  │ GitHub        │          │
│  │  • Builds   │ │ • Generate │  │ Integration   │          │
│  │  • Tests    │ │ • Refactor │  │ • CI/CD       │          │
│  │  • Deploy   │ │ • Analyze  │  │ • Workflows   │          │
│  └─────────────┘ └───────────┘  └───────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Option 1: Download Pre-built APK
Download the latest release from the [Releases](https://github.com/yourusername/droidforge/releases) page.

### Option 2: Build from Source

#### Prerequisites
- Python 3.11+
- Android SDK/NDK (auto-downloaded by buildozer)
- Linux/macOS (or WSL on Windows)

#### Steps

```bash
# Clone the repository
git clone https://github.com/yourusername/droidforge.git
cd droidforge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Build debug APK
buildozer android debug

# Or build release APK
buildozer android release
```

The APK will be in the `bin/` directory.

### Option 3: GitHub Actions (Recommended)

1. Fork this repository
2. Go to Actions tab
3. Run the "Build DroidForge APK" workflow
4. Download the artifact

## Usage

### Console Commands

```bash
# System commands
system.status              # Get system status
echo --message="Hello"     # Echo test

# Configuration
config.get --key=app.name  # Get config value
config.set --key=app.debug --value=true  # Set config

# Build commands
build.trigger --target=github  # Trigger GitHub build
build.trigger --target=local   # Local buildozer build

# AI commands
@ai generate login screen     # Generate code
@ai refactor authentication   # Refactor suggestions
@ai explain current_module    # Explain code

# Workflow commands
@workflow build-deploy        # Run full pipeline
workflow.list                 # List workflows

# Git commands
git.status                    # Repository status
```

### Creating Custom Workflows

```yaml
# workflows/my-workflow.yml
id: my-custom-workflow
name: My Custom Workflow
description: Custom automation workflow

steps:
  - id: lint
    name: Run Linter
    command: test.lint
    
  - id: build
    name: Build App
    command: build.trigger
    params:
      target: android_debug
    depends_on: [lint]
```

## Project Structure

```
droidforge/
├── main.py                 # Application entry point
├── buildozer.spec          # Buildozer configuration
├── requirements.txt        # Python dependencies
│
├── core/                   # Core engine components
│   ├── engine.py           # Main orchestration engine
│   ├── config_manager.py   # Live configuration
│   ├── event_bus.py        # Event system
│   ├── command_processor.py# Command parsing
│   └── execution_context.py# Execution contexts
│
├── ui/                     # User interface
│   ├── main_screen.py      # Main application screen
│   ├── screens/            # Additional screens
│   └── widgets/            # Custom widgets
│
├── automation/             # Automation systems
│   ├── build_manager.py    # Build orchestration
│   ├── github_integration.py# GitHub API integration
│   └── workflow_engine.py  # Workflow execution
│
├── ai/                     # AI runtime
│   ├── code_generator.py   # Code generation
│   └── runtime.py          # AI processing engine
│
├── commands/               # Command definitions
├── utils/                  # Utilities
│   └── logger.py           # Logging system
│
├── assets/                 # App assets
└── .github/
    └── workflows/
        └── build.yml       # GitHub Actions workflow
```

## Configuration

Configuration is managed through `ConfigManager` with live propagation:

```python
# Default configuration sections
app.*           # Application settings
theme.*         # UI theme settings
engine.*        # Engine configuration
build.*         # Build settings
github.*        # GitHub integration
ai.*            # AI runtime settings
automation.*    # Automation settings
logging.*       # Logging configuration
network.*       # Network settings
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Legal Notice

This application is explicitly designed as:
- A **non-derivative** system
- A **non-redistribution** platform
- A **first-party** automation and development environment

All third-party inspirations are functional references only. No branding, protected interfaces, proprietary logic, or licensed assets are used.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Kivy](https://kivy.org/) - Cross-platform Python framework
- [KivyMD](https://kivymd.readthedocs.io/) - Material Design components
- [Buildozer](https://buildozer.readthedocs.io/) - Python-to-APK packaging
- [Python-for-Android](https://python-for-android.readthedocs.io/) - Android packaging

---

<div align="center">
<strong>Built with ❤️ for mobile-first development</strong>
</div>
