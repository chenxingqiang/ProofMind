# Basic Usage Guide

This guide covers the fundamental operations and concepts for using ProofMind.

## Core Concepts

### Theorems

Theorems are represented as dictionaries with the following structure:

```python
theorem = {
    'id': 'thm123',
    'statement': 'For all real numbers x and y, if x > 0 and y > 0, then xy > 0',
    'domain': 'algebra',
    'difficulty': 2,
    'prerequisites': ['real numbers', 'multiplication']
}
```

### Proofs

Proofs are structured text containing logical steps:

```python
proof = """
1. Let x and y be positive real numbers
2. By definition, x > 0 and y > 0
3. By properties of positive numbers, their product is positive
4. Therefore, xy > 0
"""
```

### Verification Results

Verification results provide detailed analysis:

```python
verification_result = {
    'is_valid': True,
    'confidence': 0.95,
    'step_analysis': [
        {'step': 1, 'valid': True, 'rule': 'assumption'},
        {'step': 2, 'valid': True, 'rule': 'definition'},
        {'step': 3, 'valid': True, 'rule': 'property'},
        {'step': 4, 'valid': True, 'rule': 'conclusion'}
    ]
}
```

## Basic Operations

### 1. Generating Proofs

```python
from proofmind.models import TheoremLLM

# Initialize model
model = TheoremLLM.from_pretrained('models/theorem_prover')

# Generate proof
proof = model.generate_proof(theorem)
```

### 2. Verifying Proofs

```python
from proofmind.symbolic import SymbolicReasoner

# Initialize reasoner
reasoner = SymbolicReasoner()

# Verify proof
result = reasoner.verify_proof(proof, theorem)
```

### 3. Evaluating Results

```python
from proofmind.evaluation import ProofEvaluator

# Initialize evaluator
evaluator = ProofEvaluator()

# Evaluate proof
metrics = evaluator.evaluate_proof(proof, theorem)
```

## Working with Data

### Loading Datasets

```python
from proofmind.data import TheoremDataset

# Load training data
train_dataset = TheoremDataset('data/train')

# Access theorems
theorem = train_dataset[0]
```

### Processing Theorems

```python
from proofmind.data import TheoremDataLoader

# Initialize loader
loader = TheoremDataLoader()

# Load and preprocess theorems
theorems = loader.load_data('data/theorems.json')
processed = loader.preprocess_theorem(theorems[0])
```

## Common Tasks

### Batch Processing

```python
# Generate multiple proofs
theorems = [theorem1, theorem2, theorem3]
proofs = model.generate_proofs(theorems)

# Batch verification
results = reasoner.verify_proofs(proofs, theorems)
```

### Customizing Generation

```python
# Configure generation parameters
proof = model.generate_proof(
    theorem,
    max_length=512,
    num_beams=4,
    temperature=0.7
)
```

### Saving Results

```python
# Save verification results
import json

with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

## Best Practices

1. **Input Validation**
   - Verify theorem format
   - Check domain support
   - Validate prerequisites

2. **Error Handling**
   ```python
   try:
       proof = model.generate_proof(theorem)
   except InvalidTheoremError as e:
       print(f"Invalid theorem: {e}")
   except GenerationError as e:
       print(f"Generation failed: {e}")
   ```

3. **Resource Management**
   - Monitor memory usage
   - Use batch processing
   - Implement timeouts

## Next Steps

- Explore [Advanced Features](advanced-features.md)
- Review [Configuration Options](configuration.md)
- Check [Examples](../examples/basic.md) 