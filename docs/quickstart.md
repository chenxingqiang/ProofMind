# Quick Start Guide

This guide provides a quick introduction to using ProofMind for theorem proving.

## Basic Usage

### 1. Import Required Modules

```python
from proofmind.models import TheoremLLM
from proofmind.symbolic import SymbolicReasoner
from proofmind.evaluation import ProofEvaluator
```

### 2. Initialize Components

```python
# Initialize model
model = TheoremLLM.from_pretrained('models/theorem_prover')

# Initialize reasoner
reasoner = SymbolicReasoner()

# Initialize evaluator
evaluator = ProofEvaluator()
```

### 3. Generate and Verify Proof

```python
# Define theorem
theorem = {
    'statement': 'For all real numbers x and y, if x > 0 and y > 0, then xy > 0',
    'domain': 'algebra',
    'difficulty': 2
}

# Generate proof
proof = model.generate_proof(theorem)
print("\nGenerated Proof:")
print(proof)

# Verify proof
result = reasoner.verify_proof(proof, theorem)
print("\nVerification Result:")
print(f"Valid: {result.is_valid}")
print(f"Confidence: {result.confidence:.4f}")
```

## Example Workflows

### Training a Model

```python
from proofmind.models import TheoremProverTrainer
from proofmind.data import TheoremDataset

# Load datasets
train_dataset = TheoremDataset('data/train')
val_dataset = TheoremDataset('data/val')

# Initialize trainer
trainer = TheoremProverTrainer(model)

# Train model
trainer.train(
    train_dataset=train_dataset,
    val_dataset=val_dataset,
    num_epochs=3
)
```

### Evaluating Performance

```python
# Load test dataset
test_dataset = TheoremDataset('data/test')

# Evaluate model
metrics = evaluator.evaluate_model(
    model,
    test_dataset,
    metrics=['accuracy', 'bleu', 'rouge']
)

# Print results
print("\nEvaluation Results:")
for metric, value in metrics.items():
    print(f"{metric}: {value:.4f}")
```

## Common Operations

### Loading Custom Data

```python
# Load theorems from file
from proofmind.data import TheoremDataLoader

loader = TheoremDataLoader()
theorems = loader.load_data('path/to/theorems.json')
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

### Batch Processing

```python
# Process multiple theorems
theorems = [theorem1, theorem2, theorem3]
proofs = model.generate_proofs(theorems)

# Batch verification
results = reasoner.verify_proofs(proofs, theorems)
```

## Next Steps

For more detailed information:

1. Review [Basic Usage](user-guide/basic-usage.md)
2. Explore [Advanced Features](user-guide/advanced-features.md)
3. Check [Examples](examples/basic.md)
4. Read [API Documentation](api/models.md) 