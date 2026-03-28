"""
arifosmcp.intelligence/tools/logic/consensus_arbitrator.py — Tri-Witness Reality Arbitration

Provides specialized logic for combining evidence from multiple sources
into a single constitutional truth claim (F2, F3).
"""

import logging
from typing import Any

from arifosmcp.core.shared.physics import geometric_mean, std_dev

logger = logging.getLogger(__name__)


class ConsensusArbitrator:
    """
    Arbitrates search results from multiple engines.

    Constitutional Goals:
    - F2 Truth: Weight ASEAN sources and trusted domains
    - F3 Consensus: Apply Tri-Witness geometric mean to uncertainty
    - F7 Humility: Propagate uncertainty from sources
    """

    def __init__(self, asean_sites: list[str]):
        self.asean_sites = asean_sites

    def arbitrate(self, query: str, engines_results: dict[str, list[Any]]) -> dict[str, Any]:
        """
        Synthesize results into a single view.

        Args:
            query: Original search query
            engines_results: Map of engine_name -> list of SearchResult-like dicts

        Returns:
            Dictionary with aggregated results and uncertainty.
        """
        all_flattened = []
        for engine, results in engines_results.items():
            for r in results:
                # Ensure it's a dict
                if not isinstance(r, dict):
                    r_dict = r.to_dict() if hasattr(r, "to_dict") else vars(r)
                else:
                    r_dict = r

                # Apply ASEAN Weight (F2 Truth)
                r_dict["asean_bonus"] = self._calculate_asean_bonus(r_dict.get("url", ""))
                r_dict["final_score"] = self._calculate_rank_score(r_dict)
                all_flattened.append(r_dict)

        # Sort by final score (descending)
        all_flattened.sort(key=lambda x: x["final_score"], reverse=True)

        # Calculate Aggregate Uncertainty (F3 Consensus)
        # We treat different engines as 'witnesses'
        uncertainties = [r.get("uncertainty_omega", 0.5) for r in all_flattened]

        # If we have multiple successful engines, we can compute a more robust mean
        if uncertainties:
            # We use geometric mean to ensure one low-quality engine doesn't poison the score
            # and that we have 'consensus' across high-quality ones.
            agg_uncertainty = geometric_mean(uncertainties)
        else:
            agg_uncertainty = 1.0

        return {
            "results": all_flattened,
            "uncertainty_aggregate": round(agg_uncertainty, 4),
            "consensus_variance": std_dev(uncertainties) if len(uncertainties) > 1 else 0.0,
            "witness_count": len(engines_results.keys()),
        }

    def _calculate_asean_bonus(self, url: str) -> float:
        """F2: Give weight to ASEAN regional sources."""
        if any(url.endswith(s) or f"{s}/" in url for s in self.asean_sites):
            return 0.15
        return 0.0

    def _calculate_rank_score(self, result: dict[str, Any]) -> float:
        """
        Heuristic for result ranking.
        Lower rank (1, 2, 3) + low uncertainty + ASEAN bonus = high score.
        """
        base_rank_score = 1.0 / (result.get("rank", 10) + 1)
        uncertainty = result.get("uncertainty_omega", 0.1)

        # High uncertainty reduces score
        score = base_rank_score * (1.0 - uncertainty)

        # Add ASEAN bonus
        score += result.get("asean_bonus", 0.0)

        return score
