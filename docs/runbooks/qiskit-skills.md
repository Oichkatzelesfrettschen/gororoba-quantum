# Qiskit agent skills

The Qiskit agent skills come from https://github.com/Qiskit/skills, installed
by copy into `~/.claude/skills/`:

| skill | installed path | upstream commit |
|---|---|---|
| migrate-qiskit-ibm-runtime | `~/.claude/skills/migrate-qiskit-ibm-runtime/` | a5499c7c24f51633cbd0a5e7ea5902841e5b983e |

Upstream also publishes them as a Claude Code plugin:
`/plugin marketplace add Qiskit/skills`, then
`/plugin install qiskit-ai-skills@qiskit`.

## Monthly check

1. Compare `git ls-remote https://github.com/Qiskit/skills HEAD` with the
   pinned commit above.
2. On a difference, clone the new commit into a scratch directory and read
   every changed or added file in full before installing: skills are
   instructions an agent executes, so they get the review any code gets.
3. Copy the skill directories into `~/.claude/skills/`, update the table above
   in a PR, and rerun the audit described under "When to invoke". A new skill
   on the upstream roadmap (mitigation evaluation, layout selection, circuit
   optimization) also gets a written decision on whether it replaces anything
   in live_run.py.

## When to invoke

Run `/migrate-qiskit-ibm-runtime` with scope gororoba_quantum/ in these cases,
and follow its phases, grounding, and report format:
- any change that touches qiskit-ibm-runtime: primitives, options, jobs,
  service, backends, sessions, or batches;
- any change to the qiskit-ibm-runtime pin in requirements.txt;
- after every monthly skill update.

The skill sets the destination as the client-side
`qiskit_ibm_runtime.executor_sampler.Sampler` from runtime 0.50.0. It forbids
inventing an API path that its guides and the API reference do not enumerate,
so such a path is validated at run time and named in the error when absent.

## Rules the audit established

The skill's local verification ran circuits through the client-side Sampler
and established the job split live_run.py uses, recorded under "Dynamic-circuit
job split" in
[qpu-submission.md](../notes/ibm_quantum/qpu-submission.md#dynamic-circuit-job-split).
