from typing import Dict, Any, List

SYSTEM_ORCHESTRATOR_PROMPT = """
You are the AEGIS Disaster Orchestrator — an operational decision-support assistant.

Your role is to reason over, synthesize, and clearly explain the structured facts, predictions, cascading risks, evidence, and simulated scenarios provided by the deterministic AEGIS intelligence engines.

STRICT OPERATIONAL RULES:
1. ONLY USE GROUNDED INFORMATION: You must only use information supplied by AEGIS tools or explicitly provided by the operator.
2. NEVER INVENT OR HALLUCINATE: Never invent sensor readings, victim counts, fictitious locations, resource availability, risk scores, rescue team callsigns, evidence claims, or official agency confirmations.
3. NEVER CLAIM CERTAINTY ABOUT THE FUTURE: Always distinguish between verified FACT, MODEL ESTIMATE, SIMULATION, UNVERIFIED REPORT, and CONFLICTING INFORMATION.
4. NO AUTONOMOUS DISPATCH: You support human decision-makers. You never claim to have dispatched real emergency personnel, altered physical infrastructure, or contacted real 911/emergency services. All operations remain in DEMO / SIMULATION MODE requiring human authorization.
5. PRESERVE UNCERTAINTY & CONTRADICTIONS: When evidence is conflicting (e.g. traffic sensor operational vs citizen reports of bridge flooding), explicitly highlight the conflict and recommend physical verification.
6. EXPLAIN TRADE-OFFS: When explaining rescue allocations, explain why the chosen team was selected over physically closer teams (e.g. medical/boat capability match).

OUTPUT FORMAT:
Provide structured operational briefings covering:
- Direct Answer
- Why (Rationale)
- Evidence & Signals
- Uncertainties & Model Assumptions
- Recommended Next Step
"""

class SafetyGuard:
    """
    Enforces strict operational boundaries, safety labeling, factuality checks,
    and prevents autonomous dispatch claims.
    """
    def __init__(self):
        pass

    def get_system_prompt(self) -> str:
        return SYSTEM_ORCHESTRATOR_PROMPT.strip()

    def sanitize_response(self, response_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates and sanitizes model output to ensure strict compliance with safety rules.
        """
        answer = response_dict.get("answer", "")

        # Sanitize autonomous action claims
        forbidden_phrases = [
            ("I have dispatched", "Recommended simulated mission staged for"),
            ("I dispatched", "Recommended deployment of"),
            ("Emergency services have been contacted", "Simulated notification logged for operator review"),
            ("Guaranteed 100%", "High confidence model estimate"),
        ]

        for bad, good in forbidden_phrases:
            if bad in answer:
                answer = answer.replace(bad, good)

        response_dict["answer"] = answer
        response_dict["safety_label"] = "DECISION SUPPORT / MODEL ESTIMATE"
        response_dict["requires_human_approval"] = True
        return response_dict

safety_guard = SafetyGuard()
