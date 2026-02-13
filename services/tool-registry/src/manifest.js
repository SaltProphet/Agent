export const TOOL_MANIFEST_VERSION = '1.0.0';

export function createToolManifest({ name, version, schema, compatibility }) {
  return {
    manifestVersion: TOOL_MANIFEST_VERSION,
    name,
    version,
    schema,
    compatibility
  };
}

export function validateManifest(manifest) {
  const errors = [];
  if (manifest.manifestVersion !== TOOL_MANIFEST_VERSION) {
    errors.push('Unsupported manifest version');
  }
  if (!manifest.name || !manifest.version || !manifest.schema) {
    errors.push('Manifest requires name, version, and schema');
  }
  if (!manifest.compatibility?.minRegistryVersion) {
    errors.push('Manifest compatibility.minRegistryVersion is required');
  }
  return { valid: errors.length === 0, errors };
}

export function checkCompatibility(manifest, registryVersion) {
  return registryVersion >= manifest.compatibility.minRegistryVersion;
}
