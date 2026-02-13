import test from 'node:test';
import assert from 'node:assert/strict';
import { policyScope } from '../src/index.js';

test('policy package scaffold exists', () => {
  assert.equal(policyScope.includes('rbac'), true);
});
