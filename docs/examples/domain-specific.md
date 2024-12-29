# Domain-Specific Examples

This guide provides examples of using ProofMind for specific mathematical domains.

## Algebra Examples

### Group Theory

```python
from proofmind.models import TheoremLLM
from proofmind.symbolic import SymbolicReasoner

# Initialize components
model = TheoremLLM.from_pretrained('models/theorem_prover')
reasoner = SymbolicReasoner(domain='algebra')

# Define group theory theorem
theorem = {
    'statement': 'In a group G, if a² = e for all a in G, then G is abelian',
    'domain': 'algebra',
    'subdomain': 'group_theory',
    'difficulty': 4,
    'prerequisites': ['group axioms', 'abelian groups']
}

# Generate proof
proof = model.generate_proof(theorem)
print("\nGroup Theory Proof:")
print(proof)

# Verify with domain-specific rules
result = reasoner.verify_proof(proof, theorem)
print("\nVerification Result:")
print(f"Valid: {result.is_valid}")
print(f"Confidence: {result.confidence:.4f}")
```

### Ring Theory

```python
# Define ring theory theorem
theorem = {
    'statement': 'In a ring R, if x² = x for all x in R, then R is commutative',
    'domain': 'algebra',
    'subdomain': 'ring_theory',
    'difficulty': 3,
    'prerequisites': ['ring axioms', 'commutativity']
}

# Generate and verify proof
proof = model.generate_proof(theorem)
result = reasoner.verify_proof(proof, theorem)

print("\nRing Theory Verification:")
print(f"Valid: {result.is_valid}")
for step in result.step_analysis:
    print(f"\nStep {step.number}:")
    print(f"Rule Applied: {step.rule}")
```

## Analysis Examples

### Real Analysis

```python
# Initialize analysis-specific components
reasoner = SymbolicReasoner(domain='analysis')

# Define analysis theorem
theorem = {
    'statement': 'If f is continuous on [a,b] and differentiable on (a,b), and f(a)=f(b), then there exists c in (a,b) such that f\'(c)=0',
    'domain': 'analysis',
    'subdomain': 'real_analysis',
    'difficulty': 4,
    'prerequisites': ['continuity', 'differentiability', 'rolle theorem']
}

# Generate proof with step-by-step reasoning
proof = model.generate_proof(
    theorem,
    generation_mode='step_by_step',
    max_steps=8
)

print("\nReal Analysis Proof:")
print(proof)
```

### Complex Analysis

```python
# Define complex analysis theorem
theorem = {
    'statement': 'If f is entire and bounded, then f is constant',
    'domain': 'analysis',
    'subdomain': 'complex_analysis',
    'difficulty': 5,
    'prerequisites': ['holomorphic functions', 'liouville theorem']
}

# Generate proof with domain-specific knowledge
proof = model.generate_proof(
    theorem,
    domain_context=['complex_plane', 'holomorphicity']
)

print("\nComplex Analysis Proof:")
print(proof)
```

## Geometry Examples

### Euclidean Geometry

```python
# Initialize geometry-specific components
reasoner = SymbolicReasoner(domain='geometry')

# Define geometry theorem
theorem = {
    'statement': 'The sum of the angles in a triangle is 180 degrees',
    'domain': 'geometry',
    'subdomain': 'euclidean',
    'difficulty': 2,
    'prerequisites': ['parallel lines', 'angles']
}

# Generate proof with visual reasoning
proof = model.generate_proof(
    theorem,
    reasoning_mode='visual'
)

print("\nEuclidean Geometry Proof:")
print(proof)
```

### Non-Euclidean Geometry

```python
# Define non-Euclidean theorem
theorem = {
    'statement': 'In hyperbolic geometry, the sum of the angles in a triangle is less than 180 degrees',
    'domain': 'geometry',
    'subdomain': 'hyperbolic',
    'difficulty': 5,
    'prerequisites': ['hyperbolic space', 'parallel postulate']
}

# Generate proof with specialized context
proof = model.generate_proof(
    theorem,
    domain_context=['hyperbolic_model', 'curvature']
)

print("\nHyperbolic Geometry Proof:")
print(proof)
```

## Number Theory Examples

### Elementary Number Theory

```python
# Initialize number theory components
reasoner = SymbolicReasoner(domain='number_theory')

# Define number theory theorem
theorem = {
    'statement': 'The sum of two consecutive perfect squares is never a perfect square',
    'domain': 'number_theory',
    'subdomain': 'elementary',
    'difficulty': 3,
    'prerequisites': ['perfect squares', 'consecutive integers']
}

# Generate proof with induction
proof = model.generate_proof(
    theorem,
    proof_technique='induction'
)

print("\nNumber Theory Proof:")
print(proof)
```

### Modular Arithmetic

```python
# Define modular arithmetic theorem
theorem = {
    'statement': 'If p is prime and a is not divisible by p, then a^(p-1) ≡ 1 (mod p)',
    'domain': 'number_theory',
    'subdomain': 'modular_arithmetic',
    'difficulty': 4,
    'prerequisites': ['fermat little theorem', 'modular exponentiation']
}

# Generate proof with specialized notation
proof = model.generate_proof(
    theorem,
    notation='modular'
)

print("\nModular Arithmetic Proof:")
print(proof)
```

## Domain-Specific Verification

### Custom Domain Rules

```python
# Define domain-specific verification rules
geometry_rules = {
    'triangle_inequality': lambda a, b, c: a + b > c,
    'angle_sum': lambda angles: sum(angles) == 180,
    'parallel_lines': lambda angle1, angle2: angle1 == angle2
}

# Initialize domain-specific reasoner
geometry_reasoner = SymbolicReasoner(
    domain='geometry',
    custom_rules=geometry_rules
)

# Verify with custom rules
result = geometry_reasoner.verify_proof(proof, theorem)
```

### Domain-Specific Evaluation

```python
from proofmind.evaluation import ProofEvaluator

# Initialize domain-specific evaluator
evaluator = ProofEvaluator(domain='analysis')

# Define domain-specific metrics
def continuity_check(proof: str) -> float:
    # Check if proof properly handles continuity
    return score

# Evaluate with domain-specific metrics
metrics = evaluator.evaluate_proof(
    proof,
    theorem,
    custom_metrics={'continuity': continuity_check}
)

print("\nDomain-Specific Evaluation:")
for metric, value in metrics.items():
    print(f"{metric}: {value:.4f}")
```

## Next Steps

- Review [Advanced Features](../user-guide/advanced-features.md)
- Check [Configuration Options](../user-guide/configuration.md)
- Explore [API Documentation](../api/models.md) 