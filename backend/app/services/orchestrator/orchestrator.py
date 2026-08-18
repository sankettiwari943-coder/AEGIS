from typing import Dict, Any, List, Optional
from app.models.schemas import (
    AIChatRequest, AIChatResponse, OrchestratorQueryRequest, OrchestratorStructuredResponse,
    CommandBriefingResponse
)
from app.services.orchestrator.tool_registry import tool_registry, ToolRegistry
from app.services.orchestrator.intent_router import intent_router, IntentRouter
from app.services.orchestrator.context_builder import context_builder, ContextBuilder
from app.services.orchestrator.safety_guard import safety_guard, SafetyGuard
from app.services.orchestrator.response_generator import response_generator, ResponseGenerator
from app.ai import get_ai_provider

class DisasterOrchestrator:
    """
    AEGIS Central AI Disaster Orchestrator.
    Serves as the decision-support reasoning and communication layer above all deterministic intelligence engines.
    """
    def __init__(
        self,
        tools: Optional[ToolRegistry] = None,
        router: Optional[IntentRouter] = None,
        context: Optional[ContextBuilder] = None,
        safety: Optional[SafetyGuard] = None,
        generator: Optional[ResponseGenerator] = None
    ):
        self.tools = tools or tool_registry
        self.router = router or intent_router
        self.context = context or context_builder
        self.safety = safety or safety_guard
        self.generator = generator or response_generator

    def process_query(
        self,
        query: str,
        session_id: str = "demo-session",
        context_zone_id: Optional[str] = None,
        context_mode: Optional[str] = "LIVE"
    ) -> OrchestratorStructuredResponse:
        """
        Main query processing pipeline:
        1. Resolve follow-up entities / pronouns (e.g. 'it' -> 'Zone 7')
        2. Classify intent & select required tools
        3. Execute internal engine tools & build compact prompt context
        4. Invoke AI Provider (Gemini / Mock) with strict system instructions
        5. Apply Safety Guard & generate structured response with deep-links
        """
        # Step 1: Follow-up resolution
        resolved_zone = self.context.resolve_followup_context(query, session_id, context_zone_id)

        # Step 2: Intent routing & tool selection
        intent, tool_names, target_zone = self.router.route_intent(query, resolved_zone)

        # Step 3: Tool execution & context assembly
        tool_outputs, prompt_context, tool_records = self.context.execute_tools_and_build_context(
            tool_names, target_zone, query, session_id
        )

        # Step 4: AI Model synthesis
        ai_provider = get_ai_provider()
        system_prompt = self.safety.get_system_prompt()
        ai_result = ai_provider.generate_structured(prompt_context, system_prompt)

        # Step 5: Safety Guard & Structured Response Formulation
        sanitized_result = self.safety.sanitize_response(ai_result)
        structured_resp = self.generator.build_structured_response(
            sanitized_result, tool_records, intent, target_zone, tool_outputs
        )

        return structured_resp

    def generate_briefing(self, session_id: str = "demo-session") -> CommandBriefingResponse:
        """
        Synthesizes a comprehensive multi-engine situation briefing.
        """
        tool_names = [
            "get_current_situation",
            "get_prediction",
            "get_cascading_risks",
            "get_mission_recommendations",
            "get_silent_risk_zones",
            "run_simulation"
        ]
        tool_outputs, _, _ = self.context.execute_tools_and_build_context(
            tool_names, "zone-7", "Generate executive command situation briefing", session_id
        )
        return self.generator.build_command_briefing(tool_outputs)

    def route_query(self, req: AIChatRequest) -> AIChatResponse:
        """
        Backward compatibility entry point for existing API endpoints.
        """
        query_text = req.query or req.message or "What is the current situation?"
        session_id = req.session_id or "demo-session"
        res = self.process_query(
            query=query_text,
            session_id=session_id,
            context_zone_id=req.context_zone_id,
            context_mode=req.context_mode
        )

        return AIChatResponse(
            answer=res.answer,
            direct_answer=res.direct_answer,
            why_rationale=res.why_rationale,
            referenced_zones=res.referenced_zones,
            supporting_evidence=res.supporting_evidence,
            uncertainties=res.uncertainties,
            recommendations=res.recommendations,
            tools_used=res.tools_used,
            deep_links=res.deep_links,
            confidence_score=res.confidence_score,
            orchestrator_agent=res.orchestrator_agent,
            requires_human_approval=res.requires_human_approval,
            safety_label=res.safety_label
        )

    def get_available_tools(self) -> List[Dict[str, Any]]:
        return self.tools.get_tool_definitions()

disaster_orchestrator = DisasterOrchestrator()
