export const NativeVendors = Object.freeze([
  'OpenAI',
  'Anthropic',
  'Azure',
  'Bedrock',
  'Vertex',
  'GenericREST'
]);

export class ModelAdapter {
  constructor(name) {
    this.name = name;
  }

  async getCapabilities(_model) {
    throw new Error('Not implemented');
  }

  async generate(_request) {
    throw new Error('Not implemented');
  }
}

export class OpenAICompatibleAdapter extends ModelAdapter {
  constructor({ baseUrl, apiKey, fetchImpl = fetch }) {
    super('OpenAICompatible');
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
    this.fetchImpl = fetchImpl;
  }

  async getCapabilities(model) {
    return {
      provider: 'OpenAICompatible',
      model,
      features: { toolCalling: true, jsonMode: true, vision: true, streaming: true },
      limits: { maxInputTokens: 128000, maxOutputTokens: 4096, maxTools: 128, maxContextMessages: 1000 }
    };
  }

  async generate(request) {
    const response = await this.fetchImpl(`${this.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        authorization: `Bearer ${this.apiKey}`
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`OpenAI-compatible request failed: ${response.status}`);
    }

    return response.json();
  }
}

export class NativeVendorAdapterContract extends ModelAdapter {
  constructor(vendor) {
    if (!NativeVendors.includes(vendor)) {
      throw new Error(`Unsupported vendor: ${vendor}`);
    }

    super(`NativeVendor:${vendor}`);
    this.vendor = vendor;
  }
}
