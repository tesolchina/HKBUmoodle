# 📁 Project Organization

This document describes the organized file structure of the Moodle AI Processor project.

## 🏗️ Directory Structure

```
moodle-ai-processor/
├── 📄 main.py                       # Main entry point - unified CLI
├── 📄 README.md                     # Project overview and quick start
├── 📄 requirements.txt              # Python dependencies
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 config/                       # Configuration files
│   ├── config.json                 # Main configuration
│   ├── config.template.json        # Configuration template
│   └── APIkey.txt                  # API keys storage
│
├── 📁 src/                         # Core source code modules
│   ├── moodle_client.py           # Moodle API client
│   ├── ai_client.py               # OpenRouter AI client
│   └── processor.py               # Main processing logic
│
├── 📁 stage1_manual/              # Manual file processing (Stage 1)
│   ├── stage1.py                  # Stage 1 CLI interface
│   ├── file_processor.py          # File processing engine
│   ├── uploads/                   # Input files directory
│   ├── processed/                 # Results and outputs
│   └── docs/                      # Stage 1 specific documentation
│       ├── STAGE1_DEVELOPMENT_LOG.md
│       └── FEEDBACK_DELIVERY_OPTIONS.md
│
├── 📁 stage2_automated/           # API automation (Stage 2)
│   ├── automated_processor.py     # Stage 2 CLI interface
│   ├── stage2.py                 # Stage 2 commands
│   └── docs/                     # Stage 2 specific documentation
│       └── STAGE2_DEVELOPMENT_LOG.md
│
├── 📁 docs/                       # General documentation
│   ├── DEVELOPMENT_LOG.md         # Main development log
│   └── USAGE.md                   # Usage instructions
│
├── 📁 scripts/                    # Utility scripts
│   ├── setup.py                  # Setup utilities
│   └── example.py                 # Example scripts
│
└── 📁 tests/                      # Test files
    └── test_moodle_client.py      # Unit tests
```

## 📋 File Organization Principles

### Root Level (Minimal)
- **Essential files only**: main entry point, README, requirements
- **Configuration**: Keep config folder at root for easy access
- **Core source**: src/ contains shared modules used by both stages

### Stage-Specific Organization
- **stage1_manual/**: Everything related to manual file processing
- **stage2_automated/**: Everything related to API automation
- **Dedicated docs/**: Each stage has its own documentation folder

### Documentation Structure
- **docs/**: General project documentation and main development log
- **stage1_manual/docs/**: Stage 1 specific documentation and delivery options
- **stage2_automated/docs/**: Stage 2 specific documentation and API guides

### Support Files
- **scripts/**: Utility scripts and setup tools
- **tests/**: All test files and testing utilities

## 🎯 Benefits of This Organization

### 1. **Clear Separation of Concerns**
- Each stage has its own dedicated space
- Easy to find stage-specific documentation and code
- Minimal root directory clutter

### 2. **Logical Documentation Structure**
- Stage-specific docs are co-located with relevant code
- General project docs remain accessible at the project level
- Easy navigation and maintenance

### 3. **Scalable Architecture**
- Easy to add new stages or features
- Clear places for new documentation
- Maintainable codebase structure

### 4. **Developer-Friendly**
- Quick access to relevant files
- Logical file locations
- Clear project navigation

## 🚀 Quick Navigation

### For Stage 1 (Manual Processing):
```bash
cd stage1_manual/
# Code: stage1.py, file_processor.py
# Docs: docs/STAGE1_DEVELOPMENT_LOG.md, docs/FEEDBACK_DELIVERY_OPTIONS.md
# Data: uploads/, processed/
```

### For Stage 2 (API Processing):
```bash
cd stage2_automated/  
# Code: automated_processor.py, stage2.py
# Docs: docs/STAGE2_DEVELOPMENT_LOG.md
```

### For General Project Info:
```bash
# Main CLI: main.py
# Documentation: docs/DEVELOPMENT_LOG.md, docs/USAGE.md
# Configuration: config/
```

## 📝 File Access Patterns

### Development
- Start with `main.py` for unified commands
- Use stage-specific CLIs for detailed operations
- Reference stage docs for implementation details

### Documentation
- **Project overview**: `README.md`
- **Usage instructions**: `docs/USAGE.md` 
- **Development history**: `docs/DEVELOPMENT_LOG.md`
- **Stage 1 details**: `stage1_manual/docs/`
- **Stage 2 details**: `stage2_automated/docs/`

### Configuration
- **Main config**: `config/config.json`
- **API keys**: `config/APIkey.txt`
- **Templates**: `config/config.template.json`

This organization provides a clean, scalable, and maintainable project structure that grows naturally with the project's needs.
