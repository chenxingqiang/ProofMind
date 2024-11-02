# src/data/generate_sample_data.py

import json
from pathlib import Path
import numpy as np


def generate_sample_theorems(domain: str, n_samples: int = 100):
    """生成示例定理数据"""
    templates = {
        "algebra": [
            "For any {x} in ring R, {x}^2 = 0 implies {x} = 0",
            "The sum of the squares of {x} and {y} equals ({x} + {y})({x} - {y})",
            "The determinant of a {n}x{n} matrix is invariant under transpose"
        ],
        "topology": [
            "Every compact subset of a Hausdorff space is closed",
            "The product of two compact spaces is compact",
            "Every continuous function on a compact space is uniformly continuous"
        ],
        "number_theory": [
            "Every positive integer greater than {n} can be written as a sum of {k} squares",
            "If p is prime and a is not divisible by p, then a^(p-1) ≡ 1 (mod p)",
            "The sum of two consecutive perfect squares is never a perfect square"
        ]
    }

    theorems = []
    for i in range(n_samples):
        template = np.random.choice(templates[domain])
        theorem = {
            "id": f"{domain}_{i}",
            "statement": template.format(
                x=np.random.choice(['x', 'y', 'z']),
                y=np.random.choice(['x', 'y', 'z']),
                n=np.random.randint(2, 10),
                k=np.random.randint(2, 5)
            ),
            "domain": domain,
            "difficulty": np.random.choice(['easy', 'medium', 'hard']),
            "proof": f"This is a sample proof for theorem {i} in {domain}..."
        }
        theorems.append(theorem)

    return {"theorems": theorems}


def main():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    domains = ["algebra", "topology", "number_theory"]

    for domain in domains:
        domain_dir = data_dir / domain
        domain_dir.mkdir(exist_ok=True)

        data = generate_sample_theorems(domain)

        with open(domain_dir / f"{domain}_theorems.json", 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Generated sample data for {domain}")


if __name__ == "__main__":
    main()
