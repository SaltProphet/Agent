import test from 'node:test';
import assert from 'node:assert/strict';
import {
  unifiedMessageSchema,
  capabilityDescriptorSchema,
  runSnapshotMetadataSchema
} from '../src/index.js';

test('contracts export core schemas', () => {
  assert.equal(unifiedMessageSchema.title, 'UnifiedMessage');
  assert.equal(capabilityDescriptorSchema.title, 'CapabilityDescriptor');
  assert.equal(runSnapshotMetadataSchema.title, 'RunSnapshotMetadata');
});
