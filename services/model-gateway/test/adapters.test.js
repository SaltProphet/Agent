import test from 'node:test';
import assert from 'node:assert/strict';
import { NativeVendors, NativeVendorAdapterContract } from '../src/adapters.js';

test('native vendor contract includes required vendors', () => {
  assert.deepEqual(NativeVendors, ['OpenAI', 'Anthropic', 'Azure', 'Bedrock', 'Vertex', 'GenericREST']);
  const adapter = new NativeVendorAdapterContract('OpenAI');
  assert.equal(adapter.vendor, 'OpenAI');
});
