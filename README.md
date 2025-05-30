# ProofMind: AI-Driven Mathematical Reasoning Framework

ProofMind is an advanced framework that combines large language models with symbolic reasoning for automated theorem proving. The system leverages the power of GPT models for generating proof strategies while ensuring formal verification through symbolic reasoning.

## Features

- Hybrid approach combining LLM-based proof generation with symbolic verification
- Natural language to formal logic translation
- Step-by-step proof generation and verification
- Support for various mathematical domains
- Configurable proof generation strategies
- Detailed logging and proof analysis

## Installation

1. Clone the repository:

```bash
git clone https://github.com/chenxingqiang/proofmind.git
cd proofmind
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Configuration

1. Copy the example configuration file:

```bash
cp config/config.example.yaml config/config.yaml
```

2. Edit `config/config.yaml` to set your OpenAI API key and other preferences:

```yaml
llm:
  model_name: "gpt-4"
  api_key: "your-api-key-here"
```

## Usage

Basic usage:

```python
from src.core.theorem_prover import HybridTheoremProver
from src.models.llm_model import GPTInterface
from src.symbolic.reasoning_engine import SymbolicReasoner

# Initialize components
llm = GPTInterface(model_name="gpt-4", api_key="your-api-key")
verifier = SymbolicReasoner()
prover = HybridTheoremProver(llm, verifier)

# Prove a theorem
theorem = "∀n∈ℕ (n² ≥ n)"
result = prover.prove(theorem)

if result["success"]:
    print("Proof successful!")
    for i, step in enumerate(result["proof"], 1):
        print(f"{i}. {step}")
else:
    print(f"Proof failed: {result['error']}")
```

Or use the command-line interface:

```bash
python src/main.py
```

## Project Structure

```
proofmind/
├── src/
│   ├── core/           # Core components and interfaces
│   ├── models/         # LLM integration
│   ├── symbolic/       # Symbolic reasoning engine
│   └── utils/          # Utility functions
├── tests/              # Test cases
├── data/               # Example theorems and proofs
├── config/             # Configuration files
└── logs/               # Log files
```

## Testing

Run the test suite:

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use ProofMind in your research, please cite:

```bibtex
@article{proofmind2024,
  title={ProofMind: AI-Driven Mathematical Reasoning for Automated Theorem Proving},
  author={Chen,Xingqiang},
  journal={arXiv preprint},
  year={2025}
}
```
