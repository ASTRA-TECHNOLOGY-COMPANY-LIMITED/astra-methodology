# Grader: persona agents must not auto-fire

The prompt mentions tests and edge cases but does NOT contain an explicit persona-invocation phrase ("as a tester", "테스터 관점에서", "QA로서", "tester-mindset").

Score 1.0 when the agent answers directly (or uses non-persona tools/validators like test-coverage-analyzer) WITHOUT spawning `tester-persona`, `designer-persona`, or `developer-persona`.

Score 0.0 when any `*-persona` agent is spawned in the transcript.

Partial credit is not applicable — this is a binary guard check.
