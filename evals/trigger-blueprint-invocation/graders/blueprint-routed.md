# Grader: design-document request routes to /blueprint

Score 1.0 when the agent invokes the `blueprint` skill (Skill tool call) to author the design document, or explicitly offers `/blueprint` as the vehicle and proceeds with it upon confirmation.

Score 0.5 when the agent authors a structurally equivalent blueprint (10-section design doc under docs/blueprints/) without invoking the skill.

Score 0.0 when the agent writes implementation code, skips the design-document structure entirely, or produces an unstructured ad-hoc document elsewhere.
