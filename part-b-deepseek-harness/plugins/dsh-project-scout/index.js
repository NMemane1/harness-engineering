/**
 * dsh-project-scout — a DeepSeek Harness (Cordis) plugin, written from scratch.
 *
 * Registers one model-facing tool, `scan_project`, that walks a code directory
 * and returns a compact summary: file counts by language, total lines of code,
 * and TODO/FIXME markers — so a coding agent can orient itself in an unfamiliar
 * repo before making changes. Also demonstrates `ctx.effect()` for lifecycle
 * (an in-memory cache dropped when the plugin unloads).
 */
import { readdirSync, statSync, readFileSync } from 'node:fs'
import { join, extname } from 'node:path'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'project-scout'
export const inject = ['tools']

const SKIP = new Set([
  'node_modules', '.git', 'dist', 'build', '.next', 'out',
  '__pycache__', 'venv', '.venv', '.turbo', 'coverage',
])
const LANG = {
  '.ts': 'TypeScript', '.tsx': 'TypeScript', '.js': 'JavaScript', '.jsx': 'JavaScript',
  '.py': 'Python', '.go': 'Go', '.rs': 'Rust', '.java': 'Java', '.rb': 'Ruby',
  '.c': 'C', '.cpp': 'C++', '.css': 'CSS', '.html': 'HTML', '.md': 'Markdown',
  '.json': 'JSON', '.yml': 'YAML', '.yaml': 'YAML', '.sh': 'Shell',
}

function walk(dir, acc, depth = 0) {
  if (depth > 8) return
  let entries
  try { entries = readdirSync(dir) } catch { return }
  for (const entry of entries) {
    if (SKIP.has(entry) || entry.startsWith('.')) continue
    const full = join(dir, entry)
    let st
    try { st = statSync(full) } catch { continue }
    if (st.isDirectory()) { walk(full, acc, depth + 1); continue }
    const lang = LANG[extname(entry)]
    if (!lang) continue
    acc.files++
    acc.byLang[lang] = (acc.byLang[lang] ?? 0) + 1
    try {
      const lines = readFileSync(full, 'utf8').split('\n')
      acc.lines += lines.length
      lines.forEach((ln, i) => {
        if (/\b(TODO|FIXME)\b/.test(ln) && acc.todos.length < 40)
          acc.todos.push(`${full}:${i + 1}: ${ln.trim().slice(0, 100)}`)
      })
    } catch { /* skip unreadable/binary */ }
  }
}

export function apply(ctx) {
  const cache = new Map()
  ctx.effect(() => () => cache.clear())   // dropped on unload

  ctx.tools.register(defineTool({
    name: 'scan_project',
    description: 'Summarize a code project: file counts by language, total lines, and TODO/FIXME markers.',
    parameters: {
      path: { type: 'string', description: 'Project root directory (default ".")' },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      const root = args.path ?? '.'
      let scan = cache.get(root)
      if (!scan) {
        scan = { files: 0, byLang: {}, lines: 0, todos: [] }
        walk(root, scan)
        cache.set(root, scan)
      }
      const langs = Object.entries(scan.byLang)
        .sort((a, b) => b[1] - a[1])
        .map(([l, n]) => `  ${l}: ${n} files`).join('\n')
      const todos = scan.todos.length
        ? '\n\nTODO/FIXME markers:\n' + scan.todos.map((t) => '  • ' + t).join('\n')
        : '\n\nNo TODO/FIXME markers found.'
      return `Project scan of "${root}":\n` +
        `  ${scan.files} source files, ${scan.lines.toLocaleString()} total lines\n` +
        `Languages:\n${langs}${todos}`
    },
  }))

  console.log('[project-scout] registered tool: scan_project')
}
