/**
 * Offline smoke test for the two from-scratch DSH plugins — NO harness, NO API key.
 *
 * It builds a minimal fake Cordis `ctx` (a tool registry + effect stub), loads each
 * real plugin's `apply(ctx)`, then invokes the registered tools' `execute()` exactly
 * as the harness would, and checks the results. Proves the plugin logic runs.
 *
 * Run:  node tests/plugin-smoke.mjs
 * (A dev shim at node_modules/@deepseek-ai/dsh-tools lets the plugins resolve import.)
 */
import assert from 'node:assert'
import { rmSync, existsSync, mkdirSync, writeFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

// Self-provision a dev shim for @deepseek-ai/dsh-tools so the plugins resolve
// their import outside the harness. (Inside DSH, the real package is provided.)
const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const shimDir = join(root, 'node_modules', '@deepseek-ai', 'dsh-tools')
mkdirSync(shimDir, { recursive: true })
writeFileSync(join(shimDir, 'package.json'),
  JSON.stringify({ name: '@deepseek-ai/dsh-tools', version: '0.0.0-shim', type: 'module', main: 'index.js' }))
writeFileSync(join(shimDir, 'index.js'), 'export const defineTool = (def) => def\n')

function makeCtx() {
  const tools = new Map()
  return {
    tools: { register: (def) => tools.set(def.name, def) },
    effect: (_fn) => {},          // lifecycle stub
    _tools: tools,
  }
}

// ---------- second-brain ----------
const STORE = join(homedir(), '.dsh-second-brain.json')
if (existsSync(STORE)) rmSync(STORE)                    // clean slate

const sb = await import('../plugins/dsh-second-brain/index.js')
const ctx1 = makeCtx()
sb.apply(ctx1)
assert.deepEqual([...ctx1._tools.keys()].sort(), ['recall', 'remember'])

const r1 = await ctx1._tools.get('remember').execute(
  { text: 'OpenRouter base URL is https://openrouter.ai/api/v1', tags: 'api,openrouter' })
const r2 = await ctx1._tools.get('remember').execute(
  { text: 'DSH web UI runs on port 3080', tags: 'dsh' })
const found = await ctx1._tools.get('recall').execute({ query: 'openrouter' })
assert.ok(r1.includes('#1'), 'first note id')
assert.ok(found.includes('api/v1'), 'recall returns the saved note')
assert.ok(!(await ctx1._tools.get('recall').execute({ query: 'zzz' })).includes('#'),
  'recall of unknown term returns nothing')
console.log('  second-brain: remember x2 + recall ✓')
console.log('    recall("openrouter") →', found.split('\n')[0])

// ---------- project-scout ----------
const ps = await import('../plugins/dsh-project-scout/index.js')
const ctx2 = makeCtx()
ps.apply(ctx2)
assert.deepEqual([...ctx2._tools.keys()], ['scan_project'])
const scan = await ctx2._tools.get('scan_project').execute({ path: '.' })
assert.ok(/source files/.test(scan), 'scan reports files')
assert.ok(/JavaScript|Markdown|JSON/.test(scan), 'scan detects languages')
console.log('  project-scout: scan_project ✓')
console.log('    ' + scan.split('\n').slice(0, 2).join(' | '))

rmSync(STORE, { force: true })
console.log('\n\x1b[32m\x1b[1mPASS\x1b[0m — both from-scratch plugins register and execute correctly.')
