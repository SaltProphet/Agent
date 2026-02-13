import unittest

from agent_builder.negotiation import negotiate_capabilities
from agent_builder.schemas import CapabilitySet, RequestedBehavior


class CapabilityNegotiationTests(unittest.TestCase):
    def test_tool_calling_downgrades_to_planner_executor_when_allowed(self):
        requested = RequestedBehavior(require_tool_calling=True)
        available = CapabilitySet(tool_calling=False)

        plan = negotiate_capabilities(requested, available)

        self.assertTrue(plan.accepted)
        self.assertIn("enable_planner_executor_split", plan.actions)
        self.assertIn("tool_calling_unavailable", plan.reasons)

    def test_tool_calling_requirement_fails_without_fallback(self):
        requested = RequestedBehavior(
            require_tool_calling=True,
            planner_executor_fallback_allowed=False,
        )
        available = CapabilitySet(tool_calling=False)

        plan = negotiate_capabilities(requested, available)

        self.assertFalse(plan.accepted)
        self.assertIn("required_tool_calling_unavailable", plan.reasons)

    def test_structured_output_uses_post_validation_when_missing(self):
        requested = RequestedBehavior(require_structured_output=True)
        available = CapabilitySet(structured_output=False)

        plan = negotiate_capabilities(requested, available)

        self.assertTrue(plan.accepted)
        self.assertIn("enforce_schema_post_validation", plan.actions)
        self.assertIn("native_structured_output_unavailable", plan.reasons)


if __name__ == "__main__":
    unittest.main()
