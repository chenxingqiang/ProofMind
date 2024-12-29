# Models Module

The models module implements theorem proving capabilities using Large Language Models (LLMs) and provides training utilities for fine-tuning models on mathematical theorem proving tasks.

## Overview

The models module consists of two main components:
- `TheoremLLM`: Core model for generating mathematical proofs
- `TheoremProverTrainer`: Training utilities for fine-tuning models

## Components

### TheoremLLM

The `TheoremLLM` class provides methods for generating mathematical proofs using large language models.

#### Parameters

- `config` (dict): Configuration settings including:
  - `model_name`: Name of the base LLM to use
  - `model_path`: Path to model weights
  - `tokenizer_path`: Path to tokenizer
  - `generation_config`: Parameters for proof generation
  - `device`: Device to run model on (cuda/cpu)

#### Methods

```python
def generate_proof(theorem: dict, max_length: int = 512) -> str:
    """
    Generate a proof for the given theorem.
    
    Args:
        theorem (dict): Theorem metadata including statement and domain
        max_length (int): Maximum length of generated proof
        
    Returns:
        str: Generated proof text
    """

def verify_proof(proof: str, theorem: dict) -> bool:
    """
    Verify if a proof is valid for a theorem.
    
    Args:
        proof (str): The proof to verify
        theorem (dict): Theorem metadata
        
    Returns:
        bool: Whether the proof is valid
    """

def get_proof_confidence(proof: str, theorem: dict) -> float:
    """
    Get model's confidence in generated proof.
    
    Args:
        proof (str): The proof to evaluate
        theorem (dict): Theorem metadata
        
    Returns:
        float: Confidence score between 0 and 1
    """
```

### TheoremProverTrainer

The `TheoremProverTrainer` class provides utilities for training and fine-tuning theorem proving models.

#### Parameters

- `config` (dict): Training configuration including:
  - `model_config`: Model architecture settings
  - `training_config`: Training hyperparameters
  - `data_config`: Dataset configuration
  - `optimization_config`: Optimizer settings

#### Methods

```python
def train(
    train_dataset: TheoremDataset,
    val_dataset: TheoremDataset,
    num_epochs: int
) -> TrainingResults:
    """
    Train the model on theorem proving data.
    
    Args:
        train_dataset: Training dataset
        val_dataset: Validation dataset
        num_epochs: Number of training epochs
        
    Returns:
        TrainingResults: Training metrics and model state
    """

def evaluate(
    test_dataset: TheoremDataset,
    metrics: List[str] = ['accuracy', 'bleu', 'rouge']
) -> EvaluationResults:
    """
    Evaluate model performance on test dataset.
    
    Args:
        test_dataset: Test dataset
        metrics: List of metrics to compute
        
    Returns:
        EvaluationResults: Evaluation metrics
    """

def save_checkpoint(path: str) -> None:
    """
    Save model checkpoint.
    
    Args:
        path: Path to save checkpoint
    """

def load_checkpoint(path: str) -> None:
    """
    Load model checkpoint.
    
    Args:
        path: Path to checkpoint
    """
```

## Usage Examples

### Basic Proof Generation

```python
# Initialize model with configuration
config = {
    'model_name': 'theorem-llm-base',
    'model_path': 'models/theorem_prover',
    'generation_config': {
        'max_length': 512,
        'num_beams': 4,
        'temperature': 0.7
    }
}
model = TheoremLLM(config)

# Example theorem
theorem = {
    'statement': 'For all real numbers x and y, if x > 0 and y > 0, then xy > 0',
    'domain': 'algebra',
    'difficulty': 2,
    'prerequisites': ['real numbers', 'multiplication']
}

# Generate proof
proof = model.generate_proof(theorem)

# Print generated proof
print("\nGenerated Proof:")
print(proof)

# Get model confidence
confidence = model.get_proof_confidence(proof, theorem)
print(f"\nConfidence Score: {confidence:.4f}")

# Verify the proof
is_valid = model.verify_proof(proof, theorem)
print(f"Proof is Valid: {is_valid}")
```

### Model Training

```python
# Initialize trainer with configuration
trainer_config = {
    'model_config': {
        'architecture': 'transformer',
        'hidden_size': 768,
        'num_layers': 12,
        'num_heads': 12
    },
    'training_config': {
        'learning_rate': 2e-5,
        'batch_size': 16,
        'gradient_accumulation_steps': 2,
        'warmup_steps': 1000
    },
    'optimization_config': {
        'optimizer': 'adamw',
        'weight_decay': 0.01,
        'max_grad_norm': 1.0
    }
}
trainer = TheoremProverTrainer(trainer_config)

# Load datasets
train_dataset = TheoremDataset('data/train')
val_dataset = TheoremDataset('data/val')
test_dataset = TheoremDataset('data/test')

# Train model
print("\nStarting Training...")
results = trainer.train(
    train_dataset=train_dataset,
    val_dataset=val_dataset,
    num_epochs=3
)

# Print training results
print("\nTraining Results:")
print(f"Final Loss: {results.final_loss:.4f}")
print(f"Best Validation Accuracy: {results.best_val_accuracy:.4f}")
print("\nLearning Curves:")
print(f"Training Loss: {results.train_losses}")
print(f"Validation Loss: {results.val_losses}")

# Evaluate on test set
print("\nEvaluating on Test Set...")
eval_results = trainer.evaluate(
    test_dataset=test_dataset,
    metrics=['accuracy', 'bleu', 'rouge']
)

# Print evaluation results
print("\nTest Set Results:")
print(f"Accuracy: {eval_results.accuracy:.4f}")
print(f"BLEU Score: {eval_results.bleu:.4f}")
print(f"ROUGE-L Score: {eval_results.rouge_l:.4f}")

# Save trained model
trainer.save_checkpoint('models/theorem_prover_trained')
```

### Advanced Generation Features

```python
# Generate proof with step-by-step reasoning
proof_with_steps = model.generate_proof(
    theorem,
    generation_mode='step_by_step',
    max_steps=10,
    step_temperature=0.8
)

# Print proof steps
print("\nStep-by-Step Proof:")
for i, step in enumerate(proof_with_steps.steps, 1):
    print(f"\nStep {i}:")
    print(f"Statement: {step.statement}")
    print(f"Reasoning: {step.reasoning}")
    print(f"Confidence: {step.confidence:.4f}")

# Generate multiple proof attempts
proofs = model.generate_proofs(
    theorem,
    num_attempts=3,
    diversity_penalty=0.8
)

# Print multiple attempts
print("\nMultiple Proof Attempts:")
for i, proof in enumerate(proofs, 1):
    print(f"\nAttempt {i}:")
    print(proof.text)
    print(f"Confidence: {proof.confidence:.4f}")
    print(f"Valid: {proof.is_valid}")
```

## Error Handling

The module includes comprehensive error handling:

```python
try:
    proof = model.generate_proof(invalid_theorem)
except InvalidTheoremError as e:
    print(f"Invalid theorem: {e}")
except GenerationError as e:
    print(f"Proof generation failed: {e}")
except ModelNotFoundError as e:
    print(f"Model loading failed: {e}")
```

## Best Practices

1. Always validate theorem format before generation
2. Use appropriate generation parameters based on theorem complexity
3. Implement proper error handling
4. Monitor model confidence scores
5. Validate generated proofs

## Contributing

Guidelines for contributing to the models module:

1. Follow the established code style
2. Add tests for new features
3. Document model architectures
4. Maintain backwards compatibility
5. Update model cards

## Future Improvements

Planned enhancements for the module:

1. Support for more model architectures
2. Advanced proof generation strategies
3. Multi-modal theorem proving
4. Performance optimizations
5. Integration with external models 