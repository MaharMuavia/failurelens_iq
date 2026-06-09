# Responsible AI Controls

FailureLens IQ uses synthetic data and local reasoning only. It is designed to support team learning, not to assign individual blame or automate production decisions.

## Controls

- No individual blame: outputs use team process gap, systematic knowledge gap, organizational learning opportunity, and team skill area language.
- Human review for low confidence: the confidence gate halts downstream learning actions when diagnosis confidence is below the planner threshold.
- Bias and fairness warning: any protected-attribute, fairness, demographic, disparate impact, or bias signal sets a Responsible AI notice.
- Evidence vs inference separation: reports list evidence, counter-evidence, self-reflection, confidence, and grounding citations separately.
- Audit trail: each agent records action, input summary, output summary, timestamp, and duration.
- Synthetic data notice: all experiments, teams, and contexts are synthetic hackathon data.
- No automated production decisions: remediation and certification recommendations require human approval before deployment or model update.
