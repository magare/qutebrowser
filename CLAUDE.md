# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

qutebrowser is a keyboard-driven, vim-like browser based on Python and Qt. It uses QtWebEngine (Chromium-based) as its primary backend.

### Design Philosophy

qutebrowser's design is minimalist, keyboard-focused, and highly customizable. Its core principle is being a browser that "gets out of the user's way". The browser follows these key principles:

- **Keyboard-driven interface**: Inspired by Vim's keybindings and command-line approach
- **Minimalist design**: Focus on content, not chrome
- **Highly customizable**: Extensive configuration options through Python scripting
- **Extensible**: Userscripts provide flexibility without traditional extensions

## Development Commands

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/path/to/test_file.py

# Run with coverage
pytest --cov --cov-report html tests/

# Run tests with tox (includes linting)
tox

# Run only unit tests
pytest tests/unit/

# Run end-to-end tests
pytest tests/end2end/
```

### Linting and Type Checking
```bash
# Run all misc checks (includes various code quality checks)
python scripts/dev/misc_checks.py all

# Type checking with mypy
mypy qutebrowser

# Flake8 linting
flake8 qutebrowser tests

# PyLint
pylint qutebrowser

# Run vulture (dead code detection)
vulture qutebrowser
```

### Running qutebrowser
```bash
# Run directly from source
python -m qutebrowser

# Or using the launcher script
./qutebrowser.py

# Run with debug logging
python -m qutebrowser --debug

# Run with temporary basedir (for testing)
python -m qutebrowser --temp-basedir
```

### Development Setup
```bash
# Create virtual environment
python scripts/mkvenv.py

# Install in development mode
pip install -e .

# Link PyQt for development
python scripts/link_pyqt.py
```

## Code Architecture

### Core Components

**qutebrowser/** - Main application package
- **app.py** - Application initialization and main entry point
- **qutebrowser.py** - Core browser application logic

**qutebrowser/browser/** - Browser functionality
- **webengine/** - QtWebEngine (Chromium) backend implementation
- **webkit/** - Legacy QtWebKit backend (deprecated)
- **downloads.py** - Download manager
- **hints.py** - Link hinting system (vim-like navigation)
- **browsertab.py** - Tab abstraction layer

**qutebrowser/config/** - Configuration system
- **config.py** - Main configuration handling
- **configdata.py** - Configuration option definitions
- **configfiles.py** - Config file parsing

**qutebrowser/keyinput/** - Keyboard input handling
- **modeman.py** - Mode management (normal, insert, command, etc.)
- **keyparser.py** - Key sequence parsing
- **bindings.py** - Key binding definitions

**qutebrowser/mainwindow/** - Main window and UI
- **mainwindow.py** - Main browser window
- **tabbedbrowser.py** - Tab management
- **statusbar/** - Status bar widgets
- **prompt.py** - Command/prompt interface

**qutebrowser/commands/** - Command system
- **command.py** - Command decorator and registration
- **cmdutils.py** - Command utilities
- **runners.py** - Command execution

**qutebrowser/completion/** - Completion system
- **completionwidget.py** - Completion UI
- **models/** - Various completion models (commands, URLs, settings)

**qutebrowser/utils/** - Utility modules
- **objreg.py** - Global object registry (dependency injection)
- **message.py** - User messaging system
- **log.py** - Logging utilities
- **qtutils.py** - Qt-specific utilities

### Key Design Patterns

1. **Object Registry**: Global objects are registered in `objreg` for dependency injection
2. **Command System**: Commands are decorated with `@cmdutils.register()` and automatically exposed to users
3. **Configuration**: Declarative configuration in `configdata.py` with automatic UI generation
4. **Mode-based Input**: Vim-like modes (normal, insert, command, hint, etc.) handled by `modeman`
5. **Qt Signal/Slot**: Heavy use of Qt's signal/slot mechanism for event handling

### Backend Support

The browser supports two backends (though WebKit is deprecated):
- **QtWebEngine** (default): Modern Chromium-based backend
- **QtWebKit** (legacy): Older WebKit backend with known security issues

Backend abstraction is handled through `browsertab.AbstractTab` and related interfaces.

## Testing Strategy

- **Unit tests**: Fast, isolated tests in `tests/unit/`
- **End-to-end tests**: Full browser tests using pytest-qt and pytest-bdd in `tests/end2end/`
- **Hypothesis**: Property-based testing for complex logic
- **Coverage**: Aim for high coverage, checked with `scripts/dev/check_coverage.py`

## Customization and Configuration

### Configuration System

The primary way to customize qutebrowser is through the `config.py` Python script in the configuration directory. This provides programmatic control over all aspects of the browser.

**Accessing Configuration:**
- `:config-edit` - Opens config.py in your editor
- `:set` - Change settings from command-line interface
- `:help` - Access documentation directly from the browser

**Key Configuration Areas:**

1. **UI Elements**
   - Tab bar appearance and behavior
   - Status bar customization
   - Color palettes and themes
   - Font settings
   - Window and interface layout

2. **Webpage Appearance**
   - Custom CSS stylesheets applicable to all websites
   - Dark mode implementations
   - Content blocking and filtering

3. **Keybindings**
   - Fully customizable keybindings
   - Ability to rebind existing commands
   - Creation of new command shortcuts
   - Mode-specific bindings (normal, insert, command, etc.)

### Extensibility

**Userscripts:**
- Written in any language that can read environment variables and write to FIFO
- Called from command mode or assigned to keybindings
- Provide functionality that traditionally requires browser extensions
- Located in `~/.config/qutebrowser/userscripts/` (Linux) or equivalent

**Theming:**
- Themes are distributed as Python files sourced in config.py
- Community themes available on GitHub and other platforms
- Themes can completely transform the browser's appearance while maintaining its keyboard-driven nature

### Configuration Best Practices

When making changes to qutebrowser:
1. Always respect the minimalist, keyboard-first philosophy
2. Ensure customizations don't interfere with core keyboard navigation
3. Test configuration changes with `:config-source` before making permanent
4. Keep config.py modular and well-commented for maintainability
5. Use the built-in configuration options before resorting to userscripts

## Important Notes

- Python 3.9+ required
- Qt 6.2+ or Qt 5.15+ required
- Uses PyQt6 (preferred) or PyQt5 for Python-Qt bindings
- Follow PEP 8 with some exceptions (see `.flake8` and `.pylintrc`)
- Type hints are encouraged and checked with mypy
- Docstrings should follow Google style