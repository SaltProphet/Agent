export class InMemoryRunStateStore {
  constructor() {
    this.store = new Map();
  }

  async load(runId) {
    return this.store.get(runId) ?? null;
  }

  async save(runId, state) {
    this.store.set(runId, state);
    return state;
  }
}

export class GraphWorkflowEngine {
  constructor({ stateStore = new InMemoryRunStateStore() } = {}) {
    this.stateStore = stateStore;
  }

  async run({ runId, graph, context = {} }) {
    const persisted = (await this.stateStore.load(runId)) ?? {
      runId,
      cursor: 0,
      results: [],
      context
    };

    for (let i = persisted.cursor; i < graph.length; i += 1) {
      const node = graph[i];
      const output = await node.execute({ context: persisted.context, results: persisted.results });
      persisted.results.push({ nodeId: node.id, output });
      persisted.cursor = i + 1;
      await this.stateStore.save(runId, persisted);
    }

    return persisted;
  }
}
