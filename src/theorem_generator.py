# src/theorem_generator.py

import json
import logging
from pathlib import Path
from typing import List, Dict
import numpy as np

logger = logging.getLogger(__name__)


class TheoremGenerator:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.domains = ["algebra", "topology", "number_theory"]

        # 加载各个领域的定理
        self.theorems = self._load_all_theorems()

    def _load_all_theorems(self) -> Dict[str, List[Dict]]:
        """加载所有领域的定理"""
        theorems = {}
        for domain in self.domains:
            domain_path = self.data_dir / domain / "theorems.json"
            try:
                with open(domain_path) as f:
                    data = json.load(f)
                    theorems[domain] = data["theorems"]
                logger.info(
                    f"Loaded {len(theorems[domain])} theorems for {domain}")
            except Exception as e:
                logger.error(f"Error loading theorems for {domain}: {str(e)}")
                theorems[domain] = []
        return theorems

    def generate_new_theorem(self, domain: str = None) -> Dict:
        """生成新定理"""
        if domain is None:
            domain = np.random.choice(self.domains)

        # 定理模板
        templates = {
            "algebra": [
                "For any {x} in ring R, {x}^n = 0 implies {x} = 0",
                "If {x} and {y} are elements of field F, then ({x} + {y})^2 = {x}^2 + 2{x}{y} + {y}^2",
                "For matrices A and B, (AB)^T = B^T A^T"
            ],
            "topology": [
                "Every {property} subset of a {space_type} space is {conclusion}",
                "The {map_type} image of a {property} set is {conclusion}",
                "Every {space_type} space is {conclusion}"
            ],
            "number_theory": [
                "For all prime numbers p > {n}, p ≡ {a} (mod {m}) or p ≡ {b} (mod {m})",
                "If p is prime and {condition}, then {conclusion}",
                "Every positive integer greater than {n} can be written as {representation}"
            ]
        }

        # 变量替换
        variables = {
            "x": ["a", "b", "c", "x", "y", "z"],
            "n": range(2, 10),
            "property": ["compact", "closed", "open", "connected"],
            "space_type": ["metric", "Hausdorff", "topological"],
            "conclusion": ["closed", "compact", "connected", "bounded"],
            "map_type": ["continuous", "homeomorphic", "linear"],
            "a": range(1, 5),
            "b": range(1, 5),
            "m": range(2, 10),
            "condition": ["a is coprime to p", "p divides n", "p is regular"],
            "representation": ["sum of squares", "product of primes", "sum of three cubes"]
        }

        # 随机选择模板
        template = np.random.choice(templates[domain])

        # 替换变量
        for var in variables:
            if "{" + var + "}" in template:
                value = str(np.random.choice(variables[var]))
                template = template.replace("{" + var + "}", value)

        # 创建新定理
        theorem = {
            "id": f"{domain}_{len(self.theorems[domain])}",
            "statement": template,
            "domain": domain,
            "difficulty": np.random.choice(["easy", "medium", "hard"]),
            "complexity_score": np.random.uniform(0, 1),
            "proof": f"This is a generated proof for theorem {template}...",
            "symbols": self._extract_symbols(template),
            "prerequisites": []
        }

        return theorem

    def _extract_symbols(self, statement: str) -> List[str]:
        """从定理陈述中提取数学符号"""
        symbols = []
        all_symbols = {
            "∀": "forall",
            "∃": "exists",
            "∈": "in",
            "⊆": "subset",
            "∪": "union",
            "∩": "intersection",
            "→": "implies",
            "≡": "equivalent",
            "≠": "not equal",
            "≤": "less or equal",
            "≥": "greater or equal"
        }

        for symbol in all_symbols:
            if symbol in statement:
                symbols.append(symbol)

        return symbols

    def generate(self, n_theorems: int = 10) -> List[Dict]:
        """生成多个定理"""
        theorems = []
        for _ in range(n_theorems):
            domain = np.random.choice(self.domains)
            theorem = self.generate_new_theorem(domain)
            theorems.append(theorem)
        return theorems

    def get_theorems_by_domain(self, domain: str) -> List[Dict]:
        """获取指定领域的所有定理"""
        return self.theorems.get(domain, [])

    def get_all_theorems(self) -> List[Dict]:
        """获取所有定理"""
        all_theorems = []
        for domain_theorems in self.theorems.values():
            all_theorems.extend(domain_theorems)
        return all_theorems

    def save_generated_theorems(self, theorems: List[Dict], output_path: Path):
        """保存生成的定理"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump({"theorems": theorems}, f, indent=2)
        logger.info(
            f"Saved {len(theorems)} generated theorems to {output_path}")


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试定理生成器
    generator = TheoremGenerator()
    generated_theorems = generator.generate(n_theorems=5)

    # 保存生成的定理
    output_path = Path("data/generated_theorems.json")
    generator.save_generated_theorems(generated_theorems, output_path)
