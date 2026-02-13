import test from 'node:test';
import assert from 'node:assert/strict';
import { GraphWorkflowEngine } from '../src/engine.js';

test('graph workflow engine persists resumable state', async () => {
  const engine = new GraphWorkflowEngine();
  const graph = [
    { id: 'a', execute: async () => 'one' },
    { id: 'b', execute: async () => 'two' }
  ];

  const state = await engine.run({ runId: 'run-1', graph, context: {} });
  assert.equal(state.cursor, 2);
  assert.equal(state.results.length, 2);
});
