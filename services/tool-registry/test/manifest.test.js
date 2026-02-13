import test from 'node:test';
import assert from 'node:assert/strict';
import { createToolManifest, validateManifest, checkCompatibility } from '../src/manifest.js';

test('tool manifest validation and compatibility checks work', () => {
  const manifest = createToolManifest({
    name: 'search',
    version: '0.1.0',
    schema: { type: 'object' },
    compatibility: { minRegistryVersion: '0.1.0' }
  });

  const validation = validateManifest(manifest);
  assert.equal(validation.valid, true);
  assert.equal(checkCompatibility(manifest, '0.2.0'), true);
});
