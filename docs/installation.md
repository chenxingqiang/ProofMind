# Installation Guide

This guide will help you install and set up ProofMind on your system.

## Prerequisites

- Python 3.8 or higher
- CUDA-compatible GPU (recommended)
- Git

## Installation Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/chenxingqiang/proofmind.git
   cd proofmind
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download Models and Data**

   ```bash
   python scripts/download_models.py
   python scripts/download_data.py
   ```

## Configuration

1. **Environment Setup**
   - Copy `.env.example` to `.env`
   - Update configuration values

2. **Model Configuration**
   - Review `config/model_config.yaml`
   - Adjust settings as needed

3. **Data Configuration**
   - Check `config/data_config.yaml`
   - Set data paths and preferences

## Verification

1. **Run Tests**

   ```bash
   python -m pytest tests/
   ```

2. **Quick Verification**

   ```bash
   python scripts/verify_installation.py
   ```

## Common Issues

### CUDA Setup

- Ensure CUDA toolkit is installed
- Check GPU compatibility
- Verify PyTorch installation

### Memory Requirements

- Minimum 16GB RAM recommended
- GPU with 8GB+ VRAM for large models
- SSD storage recommended

### Python Dependencies

- Check Python version compatibility
- Resolve package conflicts
- Update pip if needed

## Next Steps

After installation:

1. Follow the [Quick Start Guide](quickstart.md)
2. Review [Basic Usage](user-guide/basic-usage.md)
3. Explore [Configuration](user-guide/configuration.md)

## Getting Help

If you encounter issues:

1. Check [Troubleshooting](resources/troubleshooting.md)
2. Review [FAQ](resources/faq.md)
3. Open an issue on GitHub
