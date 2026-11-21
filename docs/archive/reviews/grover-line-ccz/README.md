# Review record: iqm_grover_line: seven-CZ line-native CCZ Grover case for Garnet

Pull request: gororoba-quantum #966, branch iqm-garnet-grover-line-ccz.

Local round on head 5417bc0df6bc8d41067507de1be83d6822f582d2, one brief
([brief.md](brief.md)) for both reviewers, the owner's selection for this
pull request:

- codex on gpt-daybreak-blue at high effort, read-only sandbox: report
  "HOLD the Garnet run", four findings; its self-test was not run (qiskit
  could not import in the read-only sandbox).
- opencode on OpenCode Go glm-5.3 as red-teamer, on the same brief with a
  red-team paragraph: no run-wasting defect, four findings.
- Advisor: not run; the advisor tool returned "unavailable" when called
  after the fixes.

Fixes landed in 5f44c4419 before any Garnet credit was spent; the hosted
Codex round reads the head that carries this record.
[reconciliation.md](reconciliation.md) states every finding with its
disposition and the check that closes it.
