export class OrchestratorError extends Error {
  constructor(type, message, details = {}) {
    super(message);
    this.type = type;
    this.details = details;
  }
}

export const ErrorTypes = Object.freeze({
  model_error: 'model_error',
  tool_error: 'tool_error',
  policy_error: 'policy_error'
});

export const RetryPolicies = Object.freeze({
  model_error: { maxAttempts: 3, backoffMs: 500 },
  tool_error: { maxAttempts: 2, backoffMs: 250 },
  policy_error: { maxAttempts: 0, backoffMs: 0 }
});
