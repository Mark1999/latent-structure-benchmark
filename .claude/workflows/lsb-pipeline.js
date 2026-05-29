// DRAFT — INACTIVE. Saved Workflow script; only runs when explicitly invoked
// via the Workflow tool (which requires explicit opt-in). Writing this file does
// NOT run anything. VALIDATE before relying on it — see
// docs/proposed/2026-05-29-tier1-2-activation-runbook.md.
//
// Encodes the LSB gated pipeline deterministically:
//   Architect -> CDA SME gate -> (UI/UX gate if frontend) -> Coder -> Reviewer -> Tester
// using the project's custom subagents (agentType: 'architect' | 'cda_sme' | ...).
//
// Why: replaces ad-hoc, one-at-a-time Agent dispatches. The Coder stage runs with
// isolation:"worktree" so parallel/iterative writes can't race into a bundled commit
// (the bug that bit us on 2026-05-28). Gate FAILs stop the run and bounce to the
// Architect rather than proceeding.
//
// Invoke (example): Workflow({ name: "lsb-pipeline", args: {
//   task: "<one Coder-sized task description>",
//   kind: "methodology" | "frontend" | "other",
//   contextFiles: ["docs/status/....md"]   // optional pointers the agents should read
// }})

export const meta = {
  name: 'lsb-pipeline',
  description: 'LSB gated pipeline: Architect → CDA SME → (UI/UX) → Coder → Reviewer → Tester',
  phases: [
    { title: 'Decompose' },
    { title: 'CDA SME gate' },
    { title: 'UI/UX gate' },
    { title: 'Implement' },
    { title: 'Review' },
    { title: 'Test' },
  ],
}

const VERDICT = {
  type: 'object',
  required: ['verdict', 'summary'],
  properties: {
    verdict: { type: 'string', enum: ['PASS', 'PASS-WITH-NOTES', 'FAIL'] },
    summary: { type: 'string' },
    notes: { type: 'array', items: { type: 'string' } },
  },
}
const REVIEW = {
  type: 'object',
  required: ['verdict', 'summary'],
  properties: {
    verdict: { type: 'string', enum: ['PASS', 'PASS-WITH-NOTES', 'REJECT'] },
    summary: { type: 'string' },
    notes: { type: 'array', items: { type: 'string' } },
  },
}

const task = (args && args.task) || 'UNSPECIFIED TASK'
const kind = (args && args.kind) || 'other'
const ctx = (args && args.contextFiles ? args.contextFiles.join(', ') : 'none')
const isFrontend = kind === 'frontend'
const isMethodology = kind === 'methodology' || isFrontend === false /* SME reviews most non-trivial work */

const readFirst = `Read CLAUDE.md (esp. §1.5 framing + §7 forbidden vocab) and these context files first: ${ctx}.`

// 1. Decompose
phase('Decompose')
const plan = await agent(
  `${readFirst}\nYou are the LSB Architect. Decompose this into ONE Coder-sized task with acceptance criteria, files touched, and which gates it needs. Task: ${task}`,
  { agentType: 'architect', phase: 'Decompose' }
)

// 2. CDA SME gate (methodology-significant work)
phase('CDA SME gate')
let smeVerdict = { verdict: 'PASS', summary: 'skipped — not methodology-significant' }
if (isMethodology) {
  smeVerdict = await agent(
    `You are the LSB CDA SME. Review this plan on your four axes; issue PASS / PASS-WITH-NOTES / FAIL.\nPLAN:\n${plan}`,
    { agentType: 'cda_sme', phase: 'CDA SME gate', schema: VERDICT }
  )
  if (smeVerdict.verdict === 'FAIL') {
    return { stoppedAt: 'CDA SME', smeVerdict, plan }
  }
}

// 3. UI/UX gate (frontend only)
phase('UI/UX gate')
let uiVerdict = { verdict: 'PASS', summary: 'skipped — not frontend' }
if (isFrontend) {
  uiVerdict = await agent(
    `You are the LSB UI/UX agent. Review this frontend plan on your four criteria; issue PASS / PASS-WITH-NOTES / FAIL.\nPLAN:\n${plan}\nSME notes: ${JSON.stringify(smeVerdict.notes || [])}`,
    { agentType: 'ui_ux', phase: 'UI/UX gate', schema: VERDICT }
  )
  if (uiVerdict.verdict === 'FAIL') {
    return { stoppedAt: 'UI/UX', uiVerdict, smeVerdict, plan }
  }
}

// 4. Implement (worktree isolation — prevents commit races)
phase('Implement')
const impl = await agent(
  `${readFirst}\nYou are the LSB Coder. Implement EXACTLY this plan; apply all gate notes; one commit; run ruff/mypy/pytest (and npm build/test/lint if frontend) before committing.\nPLAN:\n${plan}\nMandatory SME notes: ${JSON.stringify(smeVerdict.notes || [])}\nMandatory UI/UX notes: ${JSON.stringify(uiVerdict.notes || [])}`,
  { agentType: 'coder', phase: 'Implement', isolation: 'worktree' }
)

// 5. Review (bounded retry on REJECT)
phase('Review')
let review = await agent(
  `You are the LSB Reviewer. Enforce the 15 binding rules + SECURITY_AND_HARDENING §9. Issue PASS / PASS-WITH-NOTES / REJECT.\nIMPLEMENTATION REPORT:\n${impl}`,
  { agentType: 'reviewer', phase: 'Review', schema: REVIEW }
)
if (review.verdict === 'REJECT') {
  // one bounded fix-forward attempt
  const fix = await agent(
    `You are the LSB Coder. The Reviewer REJECTED. Address every point, then report.\nREJECTION:\n${JSON.stringify(review)}`,
    { agentType: 'coder', phase: 'Implement', isolation: 'worktree', label: 'coder:fix' }
  )
  review = await agent(
    `You are the LSB Reviewer. Re-review after the fix. PASS / PASS-WITH-NOTES / REJECT.\nFIX REPORT:\n${fix}`,
    { agentType: 'reviewer', phase: 'Review', schema: REVIEW, label: 'review:2' }
  )
  if (review.verdict === 'REJECT') {
    return { stoppedAt: 'Reviewer (after 1 fix)', review, smeVerdict, uiVerdict, plan }
  }
}

// 6. Test
phase('Test')
const tests = await agent(
  `You are the LSB Tester. Write/Update tests with fixtures (no real API calls). Report pass/fail.\nIMPLEMENTATION:\n${impl}`,
  { agentType: 'tester', phase: 'Test' }
)

return { task, kind, smeVerdict, uiVerdict, review, plan, impl, tests }
