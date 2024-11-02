# src/proof_verifier.py

from symbolic_reasoning.symbolic_engine import SymbolicEngine
from symbolic_reasoning.coq_integration import CoqVerifier
from symbolic_reasoning.lean_integration import LeanVerifier
import logging

logger = logging.getLogger(__name__)


class ProofVerifier:
    def __init__(self):
        self.symbolic_engine = SymbolicEngine()
        self.coq_verifier = CoqVerifier()
        self.lean_verifier = LeanVerifier()

    def verify_proofs(self, proof_results):
        """验证证明结果"""
        verification_results = []

        for result in proof_results:
            try:
                # 符号推理验证
                symbolic_valid = self.symbolic_engine.verify(
                    result['theorem'],
                    result['proof']
                )

                # Coq验证
                coq_valid = self.coq_verifier.verify(
                    result['theorem'],
                    result['proof']
                )

                # Lean验证
                lean_valid = self.lean_verifier.verify(
                    result['theorem'],
                    result['proof']
                )

                verification_results.append({
                    'theorem': result['theorem'],
                    'proof': result['proof'],
                    'symbolic_valid': symbolic_valid,
                    'coq_valid': coq_valid,
                    'lean_valid': lean_valid
                })

            except Exception as e:
                logger.error(f"Error verifying proof: {str(e)}")
                verification_results.append({
                    'theorem': result['theorem'],
                    'proof': result['proof'],
                    'error': str(e)
                })

        return verification_results

    def analyze_results(self, verification_results):
        """分析验证结果"""
        total = len(verification_results)
        symbolic_valid = sum(
            1 for r in verification_results if r.get('symbolic_valid', False))
        coq_valid = sum(
            1 for r in verification_results if r.get('coq_valid', False))
        lean_valid = sum(
            1 for r in verification_results if r.get('lean_valid', False))

        return {
            'total': total,
            'symbolic_validity_rate': symbolic_valid / total if total > 0 else 0,
            'coq_validity_rate': coq_valid / total if total > 0 else 0,
            'lean_validity_rate': lean_valid / total if total > 0 else 0
        }
