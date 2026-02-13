import test from 'node:test';
import assert from 'node:assert/strict';
import { observabilityScope } from '../src/index.js';

test('observability package scaffold exists', () => {
  assert.equal(observabilityScope.includes('tracing'), true);
});
