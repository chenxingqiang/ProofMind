# ProofMind Documentation

Welcome to the ProofMind documentation! ProofMind is an AI-driven mathematical theorem proving system that combines Large Language Models (LLMs) with symbolic reasoning.

## Table of Contents

### API Reference

- [Data Module](api/data.md) - Data processing and management
- [Models Module](api/models.md) - LLM-based theorem proving
- [Symbolic Module](api/symbolic.md) - Symbolic reasoning and verification
- [Evaluation Module](api/evaluation.md) - Performance evaluation

### Getting Started

1. **Installation**
   ```bash
   git clone https://github.com/chenxingqiang/ProofMind.git
   cd ProofMind
   pip install -r requirements.txt
   ```

2. **Download Models**
   ```bash
   python scripts/download_models.py
   ```

3. **Download Data**
   ```bash
   python scripts/download_data.py
   ```

### Basic Usage

1. **Training**
   ```bash
   python src/train.py --config configs/train.yaml
   ```

2. **Evaluation**
   ```bash
   python src/evaluate.py --config configs/eval.yaml
   ```

3. **Proof Generation**
   ```python
   from src.models import TheoremLLM
   
   model = TheoremLLM(config)
   model.from_pretrained('models/checkpoints/best_model')
   
   theorem = {
       'statement': 'For all real numbers x and y, if x > 0 and y > 0, then xy > 0',
       'domain': 'algebra'
   }
   
   proof = model.generate_proof(theorem)
   ```

### Configuration

The system uses YAML configuration files:

```yaml
model:
  model_name: google/flan-t5-large
  max_tokens: 512
  save_dir: models/checkpoints

training:
  num_epochs: 10
  batch_size: 8
  learning_rate: 2.0e-5
  weight_decay: 0.01
  warmup_steps: 500
  max_grad_norm: 1.0
  clip_gradients: true

evaluation:
  metrics: ['bleu', 'rouge', 'correctness']
  batch_size: 16
  save_results: true
```

### Project Structure

```
ProofMind/
├── configs/
│   ├── train.yaml
│   └── eval.yaml
├── data/
│   ├── train/
│   ├── val/
│   └── test/
├── docs/
│   ├── api/
│   └── index.md
├── models/
│   └── checkpoints/
├── scripts/
│   ├── download_data.py
│   └── download_models.py
├── src/
│   ├── data/
│   ├── models/
│   ├── symbolic/
│   └── evaluation/
├── tests/
├── README.md
└── requirements.txt
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### License

This project is licensed under the MIT License - see the LICENSE file for details.

### Support

For questions and support:
- Open an issue on GitHub
- Join our Discord community
- Contact the maintainers

### Roadmap

- [ ] Support for more mathematical domains
- [ ] Advanced proof generation strategies
- [ ] Interactive theorem proving
- [ ] Performance optimizations
- [ ] Extended documentation 