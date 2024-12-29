# Advanced Examples

This guide provides advanced examples of using ProofMind for complex theorem proving tasks.

## Advanced Proof Generation

### Multi-Step Proof Generation

```python
from proofmind.models import TheoremLLM
from proofmind.symbolic import SymbolicReasoner

# Initialize components with advanced configuration
model = TheoremLLM.from_pretrained(
    'models/theorem_prover',
    generation_config={
        'mode': 'step_by_step',
        'max_steps': 10,
        'step_temperature': 0.8
    }
)
reasoner = SymbolicReasoner(verification_mode='thorough')

# Define complex theorem
theorem = {
    'statement': 'If f is differentiable on [a,b] and f(a)=f(b), then there exists c in (a,b) such that f\'(c)=0',
    'domain': 'analysis',
    'difficulty': 4,
    'prerequisites': ['mean value theorem', 'differentiability', 'rolle theorem']
}

# Generate proof with step tracking
proof_result = model.generate_proof_with_steps(theorem)

# Print step-by-step generation
print("\nStep-by-Step Proof Generation:")
for i, step in enumerate(proof_result.steps, 1):
    print(f"\nStep {i}:")
    print(f"Statement: {step.statement}")
    print(f"Reasoning: {step.reasoning}")
    print(f"Confidence: {step.confidence:.4f}")
    print(f"Dependencies: {step.dependencies}")
```

### Multiple Proof Strategies

```python
# Generate multiple proof attempts with different strategies
proof_attempts = model.generate_proofs(
    theorem,
    num_attempts=3,
    strategies=['direct', 'contradiction', 'induction'],
    diversity_penalty=0.8
)

# Analyze different attempts
print("\nMultiple Proof Attempts:")
for i, attempt in enumerate(proof_attempts, 1):
    print(f"\nAttempt {i} ({attempt.strategy}):")
    print(f"Proof:\n{attempt.text}")
    print(f"Confidence: {attempt.confidence:.4f}")
    print(f"Valid: {attempt.is_valid}")
    print(f"Length: {len(attempt.steps)} steps")
```

## Advanced Verification

### Detailed Proof Analysis

```python
# Perform detailed verification
verification = reasoner.verify_proof(
    proof_result.text,
    theorem,
    {
        'check_completeness': True,
        'validate_references': True,
        'analyze_dependencies': True
    }
)

# Print detailed analysis
print("\nDetailed Verification Results:")
print(f"Valid: {verification.is_valid}")
print(f"Complete: {verification.is_complete}")
print(f"Referenced Theorems: {verification.references}")

print("\nStep Analysis:")
for step in verification.step_analysis:
    print(f"\nStep {step.number}:")
    print(f"Valid: {step.is_valid}")
    print(f"Rule Applied: {step.rule}")
    print(f"Dependencies: {step.dependencies}")
    if step.issues:
        print("Issues:", step.issues)
```

### Counterexample Generation

```python
# Find counterexamples for invalid proofs
def analyze_proof_validity(proof, theorem):
    counterexample = reasoner.get_counterexample(
        proof,
        theorem,
        search_mode='exhaustive'
    )
    
    if counterexample:
        print("\nCounterexample Found:")
        for var, value in counterexample.items():
            print(f"{var} = {value}")
        print("\nViolated Conditions:")
        for condition in counterexample.violated_conditions:
            print(f"- {condition}")
    else:
        print("\nNo counterexample found - proof may be valid")

# Test with intentionally invalid proof
invalid_proof = """
1. Let f be differentiable on [a,b]
2. Assume f(a)=f(b)
3. Therefore, f'(c)=0 for some c
"""
analyze_proof_validity(invalid_proof, theorem)
```

## Advanced Training

### Custom Training Loop

```python
from proofmind.models import TheoremProverTrainer
from proofmind.data import TheoremDataset
import torch.optim as optim

# Custom training configuration
class CustomTrainingConfig:
    def __init__(self):
        self.learning_rate = 2e-5
        self.warmup_steps = 1000
        self.gradient_accumulation = 4
        self.max_grad_norm = 1.0

# Initialize trainer with custom configuration
config = CustomTrainingConfig()
trainer = TheoremProverTrainer(
    model,
    optimizer_class=optim.AdamW,
    optimizer_params={'lr': config.learning_rate}
)

# Custom training loop
def train_with_monitoring():
    # Load datasets
    train_dataset = TheoremDataset('data/train')
    val_dataset = TheoremDataset('data/val')
    
    # Training loop with monitoring
    for epoch in range(3):
        print(f"\nEpoch {epoch + 1}:")
        
        # Training phase
        train_metrics = trainer.train_epoch(
            train_dataset,
            gradient_accumulation=config.gradient_accumulation,
            max_grad_norm=config.max_grad_norm
        )
        print("\nTraining Metrics:")
        for metric, value in train_metrics.items():
            print(f"{metric}: {value:.4f}")
        
        # Validation phase
        val_metrics = trainer.evaluate(val_dataset)
        print("\nValidation Metrics:")
        for metric, value in val_metrics.items():
            print(f"{metric}: {value:.4f}")
        
        # Save checkpoint
        trainer.save_checkpoint(
            f'checkpoints/epoch_{epoch + 1}.pt',
            epoch=epoch,
            metrics=val_metrics
        )

# Run training
train_with_monitoring()
```

## Advanced Evaluation

### Custom Evaluation Metrics

```python
from proofmind.evaluation import ProofEvaluator
import numpy as np

# Define custom metrics
class ComplexityMetric:
    def __init__(self):
        self.weights = {
            'length': 0.3,
            'steps': 0.3,
            'concepts': 0.4
        }
    
    def __call__(self, proof: str) -> float:
        # Calculate weighted complexity score
        scores = {
            'length': len(proof) / 1000,  # Normalize by 1000 chars
            'steps': len(proof.split('\n')),
            'concepts': len(set(proof.split()))  # Unique words
        }
        return sum(self.weights[k] * scores[k] for k in self.weights)

# Initialize evaluator with custom metrics
evaluator = ProofEvaluator(
    custom_metrics={
        'complexity': ComplexityMetric()
    }
)

# Evaluate with custom metrics
results = evaluator.evaluate_proof(
    proof_result.text,
    theorem,
    metrics=['accuracy', 'bleu', 'complexity']
)

print("\nEvaluation Results:")
for metric, value in results.items():
    print(f"{metric}: {value:.4f}")
```

### Comparative Analysis

```python
# Compare multiple models
def compare_models(models, test_dataset):
    results = {}
    for model_name, model in models.items():
        print(f"\nEvaluating {model_name}...")
        
        # Generate proofs
        proofs = model.generate_proofs(test_dataset)
        
        # Evaluate proofs
        metrics = evaluator.evaluate_proofs(
            proofs,
            test_dataset,
            metrics=['accuracy', 'bleu', 'complexity']
        )
        
        # Store results
        results[model_name] = {
            'metrics': metrics,
            'sample_proofs': proofs[:3]  # Store some examples
        }
    
    return results

# Compare different model variants
models = {
    'base': TheoremLLM.from_pretrained('models/base'),
    'large': TheoremLLM.from_pretrained('models/large'),
    'specialized': TheoremLLM.from_pretrained('models/math')
}

comparison = compare_models(models, test_dataset)

# Print comparison
print("\nModel Comparison:")
for model_name, result in comparison.items():
    print(f"\n{model_name}:")
    for metric, value in result['metrics'].items():
        print(f"{metric}: {value:.4f}")
```

## Next Steps

- Review [Configuration Options](../user-guide/configuration.md)
- Explore [Domain-Specific Examples](domain-specific.md)
- Check [API Documentation](../api/models.md) 