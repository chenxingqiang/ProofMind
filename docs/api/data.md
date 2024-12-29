# Data Module

The data module handles data processing tasks for the ProofMind system, including loading, preprocessing, and managing theorem datasets.

## Overview

The data module consists of three main components:
- `TheoremDataLoader`: Handles loading and preprocessing of theorem data
- `TheoremFeatureExtractor`: Extracts features from theorems and proofs
- `TheoremDataset`: PyTorch dataset implementation for theorem proving

## Components

### TheoremDataLoader

The `TheoremDataLoader` class provides methods for loading and preprocessing theorem data.

#### Parameters

- `config` (dict): Configuration settings including:
  - `data_dir`: Directory containing theorem data
  - `file_pattern`: Pattern for data files
  - `preprocessing`: Preprocessing options
  - `cache_dir`: Directory for caching processed data

#### Methods

```python
def load_data(split: str = 'train') -> List[Dict]:
    """
    Load theorem data for specified split.
    
    Args:
        split (str): Data split to load (train/val/test)
        
    Returns:
        List[Dict]: List of theorem dictionaries
    """

def preprocess_theorem(theorem: Dict) -> Dict:
    """
    Preprocess a single theorem.
    
    Args:
        theorem (dict): Raw theorem data
        
    Returns:
        dict: Preprocessed theorem
    """

def save_processed_data(data: List[Dict], path: str) -> None:
    """
    Save processed data to disk.
    
    Args:
        data (List[Dict]): Processed theorems
        path (str): Save path
    """
```

### TheoremFeatureExtractor

The `TheoremFeatureExtractor` class handles feature extraction from theorems and proofs.

#### Parameters

- `config` (dict): Configuration including:
  - `feature_types`: Types of features to extract
  - `embedding_model`: Model for text embeddings
  - `max_length`: Maximum sequence length
  - `device`: Device for computation

#### Methods

```python
def extract_features(theorem: Dict) -> Dict[str, torch.Tensor]:
    """
    Extract features from a theorem.
    
    Args:
        theorem (dict): Theorem data
        
    Returns:
        Dict[str, torch.Tensor]: Extracted features
    """

def encode_proof(proof: str) -> torch.Tensor:
    """
    Encode a proof into tensor representation.
    
    Args:
        proof (str): Proof text
        
    Returns:
        torch.Tensor: Encoded proof
    """

def get_embeddings(text: str) -> torch.Tensor:
    """
    Get embeddings for text.
    
    Args:
        text (str): Input text
        
    Returns:
        torch.Tensor: Text embeddings
    """
```

### TheoremDataset

The `TheoremDataset` class implements a PyTorch dataset for theorem proving.

#### Parameters

- `config` (dict): Dataset configuration including:
  - `data_path`: Path to data directory
  - `split`: Dataset split (train/val/test)
  - `transform`: Data transformations
  - `cache`: Caching options

#### Methods

```python
def __len__() -> int:
    """
    Get dataset size.
    
    Returns:
        int: Number of theorems
    """

def __getitem__(idx: int) -> Dict[str, torch.Tensor]:
    """
    Get a single theorem example.
    
    Args:
        idx (int): Index of theorem
        
    Returns:
        Dict[str, torch.Tensor]: Theorem data
    """

def get_batch(indices: List[int]) -> Dict[str, torch.Tensor]:
    """
    Get a batch of theorems.
    
    Args:
        indices (List[int]): Indices to include
        
    Returns:
        Dict[str, torch.Tensor]: Batch of theorem data
    """
```

## Usage Examples

### Basic Data Loading

```python
# Initialize data loader with configuration
config = {
    'data_dir': 'data/theorems',
    'preprocessing': {
        'normalize_text': True,
        'remove_comments': True,
        'standardize_notation': True
    },
    'cache_dir': 'cache/processed_data'
}
loader = TheoremDataLoader(config)

# Load training data
train_data = loader.load_data('train')

# Print example theorem
print("\nExample Theorem:")
theorem = train_data[0]
print(f"Statement: {theorem['statement']}")
print(f"Domain: {theorem['domain']}")
print(f"Difficulty: {theorem['difficulty']}")
print("\nProof:")
print(theorem['proof'])

# Preprocess specific theorem
processed = loader.preprocess_theorem(theorem)
print("\nPreprocessed Theorem:")
print(f"Normalized Statement: {processed['normalized_statement']}")
print(f"Tokenized Proof: {processed['tokenized_proof'][:50]}...")
```

### Feature Extraction

```python
# Initialize feature extractor
extractor_config = {
    'feature_types': ['text', 'domain', 'difficulty'],
    'embedding_model': 'sentence-transformers/mathematical-bert',
    'max_length': 512
}
extractor = TheoremFeatureExtractor(extractor_config)

# Extract features from theorem
features = extractor.extract_features(theorem)

# Print feature information
print("\nExtracted Features:")
print(f"Text Embeddings Shape: {features['text_embeddings'].shape}")
print(f"Domain Features: {features['domain_features']}")
print(f"Difficulty Score: {features['difficulty_score']}")

# Get proof embeddings
proof_encoding = extractor.encode_proof(theorem['proof'])
print(f"\nProof Encoding Shape: {proof_encoding.shape}")

# Get statement embeddings
statement_embeddings = extractor.get_embeddings(theorem['statement'])
print(f"Statement Embeddings Shape: {statement_embeddings.shape}")
```

### Dataset Creation

```python
# Initialize dataset
dataset_config = {
    'data_path': 'data/theorems',
    'split': 'train',
    'transform': {
        'augment_proofs': True,
        'shuffle_steps': True
    }
}
dataset = TheoremDataset(dataset_config)

# Get dataset information
print(f"\nDataset Size: {len(dataset)}")

# Get single example
example = dataset[0]
print("\nExample Data:")
for key, value in example.items():
    if isinstance(value, torch.Tensor):
        print(f"{key} Shape: {value.shape}")
    else:
        print(f"{key}: {value}")

# Create data loader
from torch.utils.data import DataLoader
loader = DataLoader(
    dataset,
    batch_size=16,
    shuffle=True,
    num_workers=4
)

# Iterate through batches
for batch_idx, batch in enumerate(loader):
    print(f"\nBatch {batch_idx + 1}:")
    print(f"Input IDs Shape: {batch['input_ids'].shape}")
    print(f"Attention Mask Shape: {batch['attention_mask'].shape}")
    if batch_idx >= 2:
        break
```

## Error Handling

The module includes comprehensive error handling:

```python
try:
    data = loader.load_data('invalid_split')
except ValueError as e:
    print(f"Invalid split name: {e}")
except FileNotFoundError as e:
    print(f"Data directory not found: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. Always validate data format before processing
2. Use appropriate preprocessing for theorem text
3. Implement caching for processed data
4. Handle missing or invalid data gracefully
5. Monitor memory usage with large datasets

## Contributing

Guidelines for contributing to the data module:

1. Follow the established data format
2. Add tests for new features
3. Document preprocessing steps
4. Maintain backwards compatibility
5. Update data validation

## Future Improvements

Planned enhancements for the module:

1. Support for more data formats
2. Advanced data augmentation
3. Distributed data loading
4. Memory-efficient processing
5. Real-time data validation

## Data Format

Theorems should be stored in JSON format with the following structure:

```json
{
    "id": "thm123",
    "statement": "For all real numbers x and y, if x > 0 and y > 0, then xy > 0",
    "domain": "algebra",
    "difficulty": 2,
    "prerequisites": ["real numbers", "multiplication"],
    "proof": "1. Let x and y be positive real numbers\n2. By definition, x > 0 and y > 0\n3. By properties of positive numbers, their product is positive\n4. Therefore, xy > 0",
    "metadata": {
        "source": "textbook",
        "chapter": "3",
        "tags": ["basic", "multiplication", "positivity"]
    }
}
```

## Directory Structure

```
data/
├── train/
│   ├── algebra/
│   ├── analysis/
│   ├── geometry/
│   └── number_theory/
├── val/
│   ├── algebra/
│   ├── analysis/
│   ├── geometry/
│   └── number_theory/
└── test/
    ├── algebra/
    ├── analysis/
    ├── geometry/
    └── number_theory/
``` 