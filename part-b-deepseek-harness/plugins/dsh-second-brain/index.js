/**
 * dsh-second-brain — a DeepSeek Harness (Cordis) plugin, written from scratch.
 *
 * Gives the agent a PERSISTENT memory via two model-facing tools:
 *   • remember(text, tags?)  — save a note to ~/.dsh-second-brain.json
 *   • recall(query)          — search saved notes by text or tag
 * The agent can jot facts in one session and look them up in a later one.
 *
 * Plugin contract (docs/user/develop/basic/{index,tool}.md):
 *   a plugin is a module exporting `apply(ctx)` (+ optional `name`, `inject`);
 *   `inject = ['tools']` waits for the tool registry; `defineTool(...)` +
 *   `ctx.tools.register(...)` registers a model-facing tool.
 */
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { homedir } from 'node:os'
import { join } from 'node:path'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'second-brain'
export const inject = ['tools']

const STORE = join(homedir(), '.dsh-second-brain.json')

function load() {
  try { return existsSync(STORE) ? JSON.parse(readFileSync(STORE, 'utf8')) : [] }
  catch { return [] }
}
function save(notes) {
  writeFileSync(STORE, JSON.stringify(notes, null, 2))
}

export function apply(ctx) {
  // --- tool 1: remember ---
  ctx.tools.register(defineTool({
    name: 'remember',
    description: 'Save a note or fact to the persistent "second brain" for later recall.',
    parameters: {
      text: { type: 'string', required: true, description: 'The note to remember' },
      tags: { type: 'string', description: 'Optional comma-separated tags' },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      const notes = load()
      const note = {
        id: notes.length + 1,
        text: args.text,
        tags: (args.tags ?? '').split(',').map((s) => s.trim()).filter(Boolean),
        ts: new Date().toISOString(),
      }
      notes.push(note)
      save(notes)
      const tagStr = note.tags.length ? ` [${note.tags.join(', ')}]` : ''
      return `Remembered note #${note.id}: "${note.text}"${tagStr}`
    },
  }))

  // --- tool 2: recall ---
  ctx.tools.register(defineTool({
    name: 'recall',
    description: 'Search the second brain for saved notes matching a query (text or tag).',
    parameters: {
      query: { type: 'string', required: true, description: 'Search text or tag' },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      const q = args.query.toLowerCase()
      const hits = load().filter(
        (n) => n.text.toLowerCase().includes(q) || n.tags.some((t) => t.toLowerCase().includes(q)),
      )
      if (!hits.length) return `No notes match "${args.query}".`
      return hits
        .map((n) => `#${n.id} [${n.ts.slice(0, 10)}] ${n.text}` +
          (n.tags.length ? ` (${n.tags.join(', ')})` : ''))
        .join('\n')
    },
  }))

  console.log('[second-brain] registered tools: remember, recall')
}
