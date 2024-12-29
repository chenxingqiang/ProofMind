# Basic Examples

This guide provides basic examples of using ProofMind for theorem proving tasks.

## Simple Proof Generation

### Basic Algebra Theorem

```python
from proofmind.models import TheoremLLM
from proofmind.symbolic import SymbolicReasoner

# Initialize components
model = TheoremLLM.from_pretrained('models/theorem_prover')
reasoner = SymbolicReasoner()

# Define theorem
theorem = {
    'statement': 'For all real numbers x and y, if x > 0 and y > 0, then xy > 0',
    'domain': 'algebra',
    'difficulty': 2,
    'prerequisites': ['real numbers', 'multiplication']
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

### Basic Analysis Theorem

```python
# Define analysis theorem
theorem = {
    'statement': 'If f is continuous at a and f(a) > 0, then there exists δ > 0 such that f(x) > 0 for all x in (a-δ, a+δ)',
    'domain': 'analysis',
    'difficulty': 3,
    'prerequisites': ['continuity', 'epsilon-delta']
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

## Working with Datasets

### Loading Training Data

```python
from proofmind.data import TheoremDataset

# Load training dataset
train_dataset = TheoremDataset('data/train')

# Print dataset information
print(f"Dataset Size: {len(train_dataset)}")
print("\nExample Theorem:")
theorem = train_dataset[0]
for key, value in theorem.items():
    print(f"{key}: {value}")
```

### Basic Data Processing

```python
from proofmind.data import TheoremDataLoader

# Initialize loader
loader = TheoremDataLoader()

# Load and process theorems
theorems = loader.load_data('data/theorems.json')
processed = loader.preprocess_theorem(theorems[0])

print("\nProcessed Theorem:")
print(f"Statement: {processed['normalized_statement']}")
print(f"Domain: {processed['domain']}")
```

## Simple Evaluation

### Basic Metrics

```python
from proofmind.evaluation import ProofEvaluator

# Initialize evaluator
evaluator = ProofEvaluator()

# Evaluate proof
metrics = evaluator.evaluate_proof(proof, theorem)

print("\nEvaluation Metrics:")
for metric, value in metrics.items():
    print(f"{metric}: {value:.4f}")
```

### Batch Evaluation

```python
# Evaluate multiple proofs
theorems = [theorem1, theorem2, theorem3]
proofs = model.generate_proofs(theorems)

# Batch evaluation
results = evaluator.evaluate_proofs(proofs, theorems)

print("\nBatch Evaluation Results:")
for i, result in enumerate(results, 1):
    print(f"\nTheorem {i}:")
    for metric, value in result.items():
        print(f"{metric}: {value:.4f}")
```

## Error Handling

### Basic Error Handling

```python
try:
    # Try to generate proof
    proof = model.generate_proof(invalid_theorem)
except InvalidTheoremError as e:
    print(f"Invalid theorem: {e}")
except GenerationError as e:
    print(f"Generation failed: {e}")
```

### Validation Checks

```python
# Validate theorem format
def validate_theorem(theorem):
    required_fields = ['statement', 'domain']
    return all(field in theorem for field in required_fields)

# Check theorem before processing
if validate_theorem(theorem):
    proof = model.generate_proof(theorem)
else:
    print("Invalid theorem format")
```

## Saving Results

### Basic Result Saving

```python
import json

# Save results to file
results = {
    'theorem': theorem,
    'proof': proof,
    'verification': result.__dict__,
    'metrics': metrics
}

with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

### Loading Previous Results

```python
# Load previous results
with open('results.json', 'r') as f:
    saved_results = json.load(f)

print("\nLoaded Results:")
print(f"Theorem: {saved_results['theorem']['statement']}")
print(f"Proof: {saved_results['proof']}")
```

## Next Steps

- Explore [Advanced Examples](advanced.md)
- Review [Advanced Features](../user-guide/advanced-features.md)
- Check [Configuration Options](../user-guide/configuration.md) 