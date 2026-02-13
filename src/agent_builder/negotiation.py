from __future__ import annotations

from .schemas import CapabilitySet, DegradationPlan, RequestedBehavior


def negotiate_capabilities(
    requested: RequestedBehavior,
    available: CapabilitySet,
) -> DegradationPlan:
    """Negotiate requested agent behaviors against model/provider capabilities.

    This returns a plan that is either accepted as-is or accepted with degradations,
    unless a required capability cannot be fulfilled and no fallback is allowed.
    """
    plan = DegradationPlan(accepted=True)

    if requested.require_tool_calling and not available.tool_calling:
        if requested.planner_executor_fallback_allowed:
            plan.actions.append("enable_planner_executor_split")
            plan.reasons.append("tool_calling_unavailable")
        else:
            plan.accepted = False
            plan.reasons.append("required_tool_calling_unavailable")

    if requested.require_structured_output and not available.structured_output:
        plan.actions.append("enforce_schema_post_validation")
        plan.reasons.append("native_structured_output_unavailable")

    if requested.require_streaming and not available.streaming:
        plan.actions.append("switch_to_polled_non_streaming")
        plan.reasons.append("streaming_unavailable")

    if requested.require_tool_calling and not available.parallel_tool_calls:
        plan.actions.append("tool_calls_serial_only")
        plan.reasons.append("parallel_tool_calls_unavailable")

    return plan
