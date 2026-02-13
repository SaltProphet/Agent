import test from 'node:test';
import assert from 'node:assert/strict';
import { appName } from '../src/index.js';

test('builder-ui package scaffold exists', () => {
  assert.equal(appName, 'builder-ui');
});
