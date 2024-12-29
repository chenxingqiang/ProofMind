# Configuration Guide

This guide covers the configuration options available in ProofMind.

## Configuration Files

ProofMind uses YAML configuration files for various components:

### Model Configuration

```yaml
model:
  # Base model settings
  model_name: google/flan-t5-large
  model_path: models/theorem_prover
  max_length: 512
  device: cuda
  
  # Generation settings
  generation:
    num_beams: 4
    temperature: 0.7
    top_p: 0.9
    repetition_penalty: 1.2
    
  # Special tokens
  special_tokens:
    - "<PROOF_START>"
    - "<PROOF_END>"
    - "<STEP>"
    - "<THEREFORE>"
```

### Data Configuration

```yaml
data:
  # Data paths
  train_dir: data/train
  val_dir: data/val
  test_dir: data/test
  cache_dir: cache/data
  
  # Data splitting
  train_ratio: 0.8
  val_ratio: 0.1
  test_ratio: 0.1
  
  # Preprocessing
  preprocessing:
    clean_text: true
    normalize_math: true
    remove_comments: true
    
  # Augmentation
  augmentation:
    enabled: true
    techniques:
      - synonym_replacement
      - back_translation
```

### Symbolic Reasoning Configuration

```yaml
symbolic:
  # Verification settings
  verification_mode: strict
  timeout: 30
  max_steps: 100
  
  # Domain rules
  domains:
    algebra:
      enabled: true
      rules: rules/algebra.yaml
    analysis:
      enabled: true
      rules: rules/analysis.yaml
    geometry:
      enabled: true
      rules: rules/geometry.yaml
```

### Evaluation Configuration

```yaml
evaluation:
  # Metrics
  metrics:
    - accuracy
    - bleu
    - rouge
    - proof_length
    
  # Thresholds
  thresholds:
    min_confidence: 0.8
    max_steps: 20
    timeout: 60
    
  # Logging
  logging:
    save_results: true
    output_dir: results/evaluation
    log_level: INFO
```

## Environment Variables

Set environment variables in `.env`:

```bash
# Model settings
CUDA_VISIBLE_DEVICES=0,1
MAX_MEMORY=16GB
NUM_WORKERS=4

# API keys
WANDB_API_KEY=your_key_here
HF_TOKEN=your_token_here

# Logging
LOG_LEVEL=INFO
LOG_DIR=logs/
```

## Runtime Configuration

### Model Configuration

```python
# Configure model at runtime
model.configure(
    max_length=512,
    num_beams=4,
    temperature=0.7
)

# Set device configuration
model.to(device='cuda:0')
```

### Data Configuration

```python
# Configure data loading
loader = TheoremDataLoader(
    batch_size=32,
    num_workers=4,
    pin_memory=True
)

# Set preprocessing options
loader.set_preprocessing(
    clean_text=True,
    normalize_math=True
)
```

### Verification Configuration

```python
# Configure reasoner
reasoner.configure(
    verification_mode='strict',
    timeout=30,
    check_completeness=True
)

# Set domain rules
reasoner.load_rules('rules/custom_rules.yaml')
```

## Advanced Configuration

### Custom Configuration

```python
# Define custom configuration
class ProofConfig:
    def __init__(self):
        self.model_params = {
            'temperature': 0.7,
            'num_beams': 4
        }
        self.verification_params = {
            'mode': 'strict',
            'timeout': 30
        }

# Use custom configuration
config = ProofConfig()
model.configure(**config.model_params)
```

### Dynamic Configuration

```python
# Configure based on input
def get_config(theorem_difficulty):
    return {
        'temperature': 0.7 if theorem_difficulty > 3 else 0.5,
        'num_beams': min(4 + theorem_difficulty, 8),
        'max_length': 512 * (1 + theorem_difficulty // 3)
    }

# Apply dynamic configuration
config = get_config(theorem['difficulty'])
model.configure(**config)
```

## Configuration Best Practices

1. **Version Control**
   - Keep configuration files in version control
   - Document configuration changes
   - Use environment-specific configs

2. **Security**
   - Never commit sensitive data
   - Use environment variables for secrets
   - Validate configuration values

3. **Optimization**
   - Profile different configurations
   - Monitor resource usage
   - Cache expensive operations

4. **Maintenance**
   - Regular configuration review
   - Remove unused options
   - Update documentation

## Next Steps

- Review [Advanced Features](advanced-features.md)
- Check [Examples](../examples/basic.md)
- Read [API Documentation](../api/models.md) 