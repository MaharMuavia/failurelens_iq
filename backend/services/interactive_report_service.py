import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from backend.models.schemas import AgentContext

class InteractiveReportService:
    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or Path("reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_html(
        self,
        ctx: AgentContext,
        original_prompt: str,
        prompt_extraction: dict[str, Any],
        analysis_result: dict[str, Any]
    ) -> str:
        exp = ctx.experiment
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Safely escape helper
        def esc(val: Any) -> str:
            if val is None:
                return ""
            return html.escape(str(val))

        # Build citations list
        citations_html = ""
        citations = analysis_result.get("citations") or []
        if citations:
            for c in citations:
                citations_html += f"""
                <div class="citation-card">
                    <div class="citation-header">
                        <span class="citation-id">{esc(c.get('id') or c.get('citation_id'))}</span>
                        <span class="citation-tag">{esc(c.get('source_type'))}</span>
                    </div>
                    <h4 class="citation-title">{esc(c.get('title'))}</h4>
                    <p class="citation-excerpt">"{esc(c.get('excerpt'))}"</p>
                    <div class="citation-footer">
                        <span>Relevance: <strong>{esc(c.get('relevance_score'))}</strong></span>
                        <span>Scope: <strong>{esc(c.get('permission_scope') or 'demo')}</strong></span>
                    </div>
                </div>
                """
        else:
            citations_html = "<p class='no-data'>No grounded citations retrieved for this run.</p>"

        # Build metrics table
        metrics_table = ""
        metrics = exp.metrics or {}
        baseline = exp.baseline_metrics or {}
        for k, v in metrics.items():
            b_val = baseline.get(k, "-")
            diff = "-"
            diff_class = ""
            if isinstance(v, (int, float)) and isinstance(b_val, (int, float)):
                d = v - b_val
                if d < 0:
                    diff = f"{d:+.4f}"
                    diff_class = "negative"
                else:
                    diff = f"{d:+.4f}"
                    diff_class = "positive"
            metrics_table += f"""
            <tr>
                <td>{esc(k)}</td>
                <td>{esc(v)}</td>
                <td>{esc(b_val)}</td>
                <td class="{diff_class}">{esc(diff)}</td>
            </tr>
            """

        # Build agent workflow timeline / cards
        agent_workflow_html = ""
        agent_workflow = analysis_result.get("agent_workflow") or []
        for a in agent_workflow:
            status = a.get("status", "pending")
            status_class = f"status-{status.lower().replace('_', '-')}"
            findings = " ".join(esc(f) for f in a.get("findings", [])) or "No findings recorded."
            next_actions = " ".join(esc(na) for na in a.get("recommended_next_actions", [])) or "None"
            agent_workflow_html += f"""
            <div class="agent-card">
                <div class="agent-header">
                    <span class="agent-name">{esc(a.get('agent_name'))}</span>
                    <span class="agent-status {status_class}">{esc(status)}</span>
                </div>
                <div class="agent-role">{esc(a.get('role'))}</div>
                <div class="agent-meta">Confidence: <strong>{esc(a.get('confidence_score'))}</strong></div>
                <div class="agent-body">
                    <p><strong>Findings:</strong> {findings}</p>
                    <p><strong>Next Actions:</strong> {next_actions}</p>
                </div>
            </div>
            """

        # Build reasoning steps trace
        reasoning_trace_html = ""
        for trace in ctx.agent_trace:
            steps_html = ""
            if trace.skip_reason:
                steps_html = f"<div class='trace-skip'>Skipped: {esc(trace.skip_reason)}</div>"
            else:
                for step in trace.reasoning_steps:
                    evidence_list = ""
                    if step.evidence:
                        for ev in step.evidence:
                            evidence_list += f"<li>[{esc(ev.source_id)} / {esc(ev.field_path)}] {esc(ev.interpretation)} (confidence: {esc(ev.confidence)})</li>"
                    evidence_html = f"<ul class='trace-evidence'>{evidence_list}</ul>" if evidence_list else ""
                    
                    steps_html += f"""
                    <div class="trace-step">
                        <div class="trace-step-header">
                            <span class="step-num">Step {esc(step.step_number)}: {esc(step.thought_type.upper())}</span>
                            <span class="step-conf">Confidence: {esc(step.confidence)}</span>
                        </div>
                        <p class="step-desc"><strong>Description:</strong> {esc(step.description)}</p>
                        <p class="step-finding"><strong>Finding:</strong> {esc(step.finding)}</p>
                        {evidence_html}
                    </div>
                    """
            
            reasoning_trace_html += f"""
            <details class="agent-trace-details">
                <summary class="agent-trace-summary">
                    <span>{esc(trace.agent_name)} ({esc(trace.role)})</span>
                    <span class="agent-summary-badge status-{trace.status.value.lower()}">{esc(trace.status.value)}</span>
                </summary>
                <div class="agent-trace-content">
                    {steps_html}
                </div>
            </details>
            """

        # Build practice questions mapping
        cert_questions_html = ""
        questions = []
        if ctx.assessment and ctx.assessment.questions:
            questions = ctx.assessment.questions
        for idx, q in enumerate(questions):
            options_html = ""
            for opt in q.options:
                is_correct = "correct-option" if opt == q.correct_answer else ""
                options_html += f"<li class='{is_correct}'>{esc(opt)}</li>"
            cert_questions_html += f"""
            <div class="question-card">
                <span class="question-num">Question {idx+1} ({esc(q.question_type)})</span>
                <p class="question-text">{esc(q.question)}</p>
                <ul class="question-options">
                    {options_html}
                </ul>
                <p class="question-explanation"><strong>Explanation:</strong> {esc(q.explanation)}</p>
            </div>
            """
        if not cert_questions_html:
            cert_questions_html = "<p class='no-data'>No certification assessment questions generated for this run.</p>"

        # Parse certification result fields
        cert_result = analysis_result.get("certification_readiness", {})
        cert_mapping = cert_result.get("mapping", {})
        cert_name = cert_mapping.get("recommended_cert", "DP-100: Azure Data Scientist")
        cert_code = cert_mapping.get("cert_code", "DP-100")
        cert_domain = cert_mapping.get("skill_domain", "Model training and evaluation")
        cert_learning_path = "".join(f"<li>{esc(lp)}</li>" for lp in cert_mapping.get("learning_path", [])) or "<li>Microsoft Learn DP-100 learning paths</li>"

        # Parse remediation result fields
        remediation_res = analysis_result.get("remediation_plan") or {}
        three_day = "".join(f"<li>{esc(item)}</li>" for item in remediation_res.get("three_day_plan", [])) or "<li>Investigate class weights</li><li>Audit evaluation metric logs</li><li>Validate subgroup metrics</li>"
        seven_day = "".join(f"<li>{esc(item)}</li>" for item in remediation_res.get("seven_day_plan", [])) or "<li>Configure stratified split</li><li>Enable model fairness constraints</li><li>Run test evaluation</li><li>Deploy updated pipeline</li><li>Set up drift alert</li><li>Document lessons</li><li>Conduct review</li>"
        hands_on_lab = remediation_res.get("hands_on_lab") or "Configure Azure Machine Learning pipelines with custom class-balanced evaluation metrics."
        responsible_ai_note = remediation_res.get("responsible_ai_note") or "No specific responsible AI alert triggered. Proceed with general fairness validation."

        # Parse manager rollup details
        manager_summary = analysis_result.get("manager_summary") or {}
        business_risk = manager_summary.get("recurring_pattern_alert") or "Medium risk: model is failing to generalise on minority sub-classes."
        engineering_action = manager_summary.get("recommended_action") or "Implement stratified evaluation splits and register baseline comparison checks."
        learning_gap = manager_summary.get("learning_velocity") or "Needs focus on imbalanced datasets and validation methodology."
        review_decision = "Requires human review" if ctx.requires_human_review else "Automated remediation approved"

        # Production proof details
        azure_status = analysis_result.get("azure_status") or {}
        live_search = esc(azure_status.get("azure_ai_search_used", False))
        live_cosmos = esc(azure_status.get("cosmos_trace_stored", False))
        live_blob = esc(azure_status.get("blob_report_uploaded", False))
        
        # Inferred model provider
        provider_proof = analysis_result.get("llm_reasoning_proof") or {}
        model_provider = provider_proof.get("provider", "deterministic_fallback")
        honest_limitation = analysis_result.get("microsoft_iq_compliance", {}).get("honest_limitation") or "Local demo mode. Grounding knowledge is retrieved from local failure playbooks."

        # Extract explicit/assumed fields lists
        pe = prompt_extraction.get("prompt_extraction") or {}
        explicit_fields = ", ".join(esc(f) for f in pe.get("explicit_fields", []))
        assumed_fields = ", ".join(esc(f) for f in pe.get("assumed_fields", []))
        pe_confidence = pe.get("confidence", 0.0)

        # JSON String
        full_experiment_json = json.dumps(exp.model_dump(mode="json"), indent=2)

        # Full HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FailureLens IQ Report: {esc(exp.experiment_id)}</title>
    <style>
        :root {{
            --bg-main: #0b0f19;
            --bg-card: rgba(255, 255, 255, 0.04);
            --bg-card-hover: rgba(255, 255, 255, 0.08);
            --border-color: rgba(255, 255, 255, 0.1);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --accent: #22d3ee;
            --accent-glow: rgba(34, 211, 238, 0.15);
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --sidebar-width: 260px;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            background-color: var(--bg-main);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            display: flex;
            min-height: 100vh;
        }}
        /* Sidebar styling */
        aside {{
            width: var(--sidebar-width);
            background-color: rgba(15, 23, 42, 0.6);
            border-right: 1px solid var(--border-color);
            position: fixed;
            top: 0;
            bottom: 0;
            left: 0;
            padding: 24px 16px;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}
        .brand {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 8px;
            padding-left: 8px;
        }}
        .brand span {{
            color: var(--accent);
        }}
        .nav-links {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            list-style: none;
        }}
        .nav-link {{
            display: block;
            padding: 10px 12px;
            color: var(--text-muted);
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .nav-link:hover, .nav-link.active {{
            background-color: var(--bg-card-hover);
            color: var(--text-main);
            box-shadow: inset 3px 0 0 var(--accent);
        }}
        /* Main layout styling */
        main {{
            margin-left: var(--sidebar-width);
            flex: 1;
            padding: 40px;
            max-width: 1100px;
        }}
        header {{
            margin-bottom: 32px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
        }}
        .report-title-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        h1 {{
            font-size: 2rem;
            font-weight: 700;
        }}
        .report-subtitle {{
            color: var(--text-muted);
            margin-top: 4px;
            font-size: 0.95rem;
        }}
        .metadata-badge {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.8rem;
            color: var(--accent);
        }}
        /* Section styling */
        .report-section {{
            display: none;
            animation: fadeIn 0.3s ease-in-out;
        }}
        .report-section.active {{
            display: block;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        h2 {{
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: var(--accent);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
        }}
        /* Cards */
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }}
        .card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            backdrop-filter: blur(12px);
        }}
        .card-title {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        /* Prompt block */
        .prompt-block {{
            background-color: rgba(34, 211, 238, 0.05);
            border: 1px solid var(--accent);
            border-radius: 8px;
            padding: 16px;
            font-style: italic;
            line-height: 1.6;
            margin-bottom: 24px;
        }}
        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{
            color: var(--text-muted);
            font-weight: 600;
        }}
        .positive {{ color: var(--success); }}
        .negative {{ color: var(--danger); }}
        /* Code pre */
        pre {{
            background-color: rgba(0, 0, 0, 0.3);
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            border: 1px solid var(--border-color);
            font-family: monospace;
            font-size: 0.85rem;
        }}
        /* Citations and Agents */
        .citation-card, .agent-card, .question-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }}
        .citation-header, .agent-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .citation-id {{
            color: var(--accent);
            font-weight: 700;
        }}
        .citation-tag, .agent-status {{
            background-color: rgba(255, 255, 255, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
        }}
        .status-completed, .status-success, .status-active {{
            background-color: rgba(16, 185, 129, 0.15);
            color: var(--success);
            border: 1px solid var(--success);
        }}
        .status-waiting, .status-pending {{
            background-color: rgba(245, 158, 11, 0.15);
            color: var(--warning);
            border: 1px solid var(--warning);
        }}
        .status-human-review {{
            background-color: rgba(239, 68, 68, 0.15);
            color: var(--danger);
            border: 1px solid var(--danger);
        }}
        .citation-title {{
            font-size: 1.05rem;
            margin-bottom: 6px;
        }}
        .citation-excerpt {{
            font-size: 0.9rem;
            color: var(--text-muted);
            margin-bottom: 10px;
            line-height: 1.5;
        }}
        .citation-footer {{
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--text-muted);
        }}
        /* Collapsible details */
        .agent-trace-details {{
            border: 1px solid var(--border-color);
            border-radius: 6px;
            margin-bottom: 12px;
            background-color: var(--bg-card);
            overflow: hidden;
        }}
        .agent-trace-summary {{
            padding: 12px 16px;
            cursor: pointer;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
            outline: none;
            user-select: none;
        }}
        .agent-trace-summary:hover {{
            background-color: var(--bg-card-hover);
        }}
        .agent-summary-badge {{
            font-size: 0.75rem;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .agent-trace-content {{
            padding: 16px;
            border-top: 1px solid var(--border-color);
            background-color: rgba(0, 0, 0, 0.15);
        }}
        .trace-step {{
            border-left: 2px solid var(--accent);
            padding-left: 14px;
            margin-bottom: 16px;
        }}
        .trace-step-header {{
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            color: var(--accent);
            margin-bottom: 4px;
        }}
        .step-desc, .step-finding {{
            font-size: 0.9rem;
            margin-bottom: 4px;
            line-height: 1.4;
        }}
        .trace-evidence {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 6px;
            padding-left: 18px;
        }}
        /* Questions */
        .question-card {{
            border-left: 4px solid var(--accent);
        }}
        .question-num {{
            font-size: 0.8rem;
            color: var(--accent);
            text-transform: uppercase;
        }}
        .question-text {{
            font-weight: 600;
            margin: 6px 0 12px 0;
        }}
        .question-options {{
            list-style: none;
            padding-left: 0;
            margin-bottom: 12px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .question-options li {{
            padding: 8px 12px;
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 0.9rem;
        }}
        .question-options li.correct-option {{
            border-color: var(--success);
            background-color: rgba(16, 185, 129, 0.05);
            font-weight: 600;
        }}
        .question-explanation {{
            font-size: 0.85rem;
            color: var(--text-muted);
            border-top: 1px solid var(--border-color);
            padding-top: 8px;
        }}
        /* Progress bars / meter */
        .progress-container {{
            width: 100%;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 9999px;
            height: 10px;
            overflow: hidden;
            margin-top: 6px;
        }}
        .progress-bar {{
            height: 100%;
            background-color: var(--accent);
            border-radius: 9999px;
        }}
        .no-data {{
            color: var(--text-muted);
            font-style: italic;
        }}
        .flex {{
            display: flex;
        }}
        .flex-between {{
            justify-content: space-between;
        }}
        .list-unstyled {{
            list-style: none;
        }}
        .gap-10 {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .gap-6 {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
    </style>
</head>
<body>

    <aside>
        <div class="brand">
            <span>FailureLens</span> IQ
        </div>
        <ul class="nav-links">
            <li><a class="nav-link active" onclick="showSection('overview', this)">Dashboard Overview</a></li>
            <li><a class="nav-link" onclick="showSection('prompt-exp', this)">Prompt & Experiment</a></li>
            <li><a class="nav-link" onclick="showSection('diagnosis', this)">Failure Diagnosis</a></li>
            <li><a class="nav-link" onclick="showSection('workflow', this)">Agent Workflow</a></li>
            <li><a class="nav-link" onclick="showSection('grounding', this)">Grounded Evidence</a></li>
            <li><a class="nav-link" onclick="showSection('remediation', this)">Remediation & Certs</a></li>
            <li><a class="nav-link" onclick="showSection('proof', this)">Proof & Disclaimers</a></li>
        </ul>
    </aside>

    <main>
        <header>
            <div class="report-title-row">
                <div>
                    <h1>FailureLens IQ Report</h1>
                    <div class="report-subtitle">Learning Intelligence from Failed ML Experiments</div>
                </div>
                <div class="metadata-badge">
                    Run ID: {esc(ctx.run_id)}
                </div>
            </div>
            <div style="margin-top: 14px; font-size: 0.8rem; color: var(--text-muted);">
                Generated on: <strong>{esc(timestamp)}</strong>
            </div>
        </header>

        <!-- OVERVIEW SECTION -->
        <section id="overview" class="report-section active">
            <h2>Dashboard Overview</h2>
            <div class="grid-2">
                <div class="card">
                    <div class="card-title">Executive Summary</div>
                    <p style="line-height: 1.6; font-size: 0.95rem;">
                        {esc(analysis_result.get('executive_summary'))}
                    </p>
                </div>
                <div class="card">
                    <div class="card-title">Analysis Gate</div>
                    <div class="gap-10">
                        <div>
                            <span>Overall Calibrated Confidence:</span>
                            <div class="progress-container">
                                <div class="progress-bar" style="width: {esc(int(ctx.overall_confidence * 100))}%"></div>
                            </div>
                            <div style="text-align: right; font-size: 0.8rem; margin-top: 4px; color: var(--accent);">
                                <strong>{esc(int(ctx.overall_confidence * 100))}%</strong>
                            </div>
                        </div>
                        <div>
                            <span>Gate Decision:</span>
                            <span class="agent-summary-badge status-{'success' if ctx.gate_passed else 'human-review'}" style="margin-left: 8px;">
                                {esc('PASSED' if ctx.gate_passed else 'HALTED')}
                            </span>
                        </div>
                        <div>
                            <span>Human Review Required:</span>
                            <strong style="color: {esc('var(--danger)' if ctx.requires_human_review else 'var(--success)')}; font-size: 0.9rem;">
                                {esc('Yes' if ctx.requires_human_review else 'No')}
                            </strong>
                        </div>
                    </div>
                </div>
            </div>

            <div class="grid-2">
                <div class="card">
                    <div class="card-title">Manager Briefing</div>
                    <div class="gap-10" style="font-size: 0.9rem;">
                        <p><strong>Business Risk:</strong> {esc(business_risk)}</p>
                        <p><strong>Required Engineering Action:</strong> {esc(engineering_action)}</p>
                        <p><strong>Recommended Upskilling:</strong> {esc(learning_gap)}</p>
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Recommended Intervention</div>
                    <div class="gap-6" style="font-size: 0.9rem;">
                        <p><strong>Microsoft Certification:</strong> {esc(cert_name)} ({esc(cert_code)})</p>
                        <p><strong>Skill Domain:</strong> {esc(cert_domain)}</p>
                        <p><strong>Remediation:</strong> {esc(hands_on_lab)}</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- PROMPT & EXPERIMENT SECTION -->
        <section id="prompt-exp" class="report-section">
            <h2>Original Prompt</h2>
            <div class="prompt-block">
                "{esc(original_prompt)}"
            </div>

            <h2>Prompt Extraction Metadata</h2>
            <div class="card" style="margin-bottom: 24px;">
                <div class="gap-10" style="font-size: 0.9rem;">
                    <p><strong>Parser Type:</strong> {esc('Microsoft Foundry OpenAI' if model_provider in ('foundry_openai', 'foundry_agent') else 'Deterministic Local Rules')}</p>
                    <p><strong>Parser Confidence:</strong> {esc(int(pe_confidence * 100))}%</p>
                    <p><strong>Explicitly Extracted Fields:</strong> <code style="color: var(--accent);">{esc(explicit_fields or 'None')}</code></p>
                    <p><strong>Assumed/Generated Fields:</strong> <code style="color: var(--warning);">{esc(assumed_fields or 'None')}</code></p>
                </div>
            </div>

            <h2>Generated Experiment Log</h2>
            <div class="card">
                <table>
                    <thead>
                        <tr>
                            <th>Field</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>Experiment ID</td><td>{esc(exp.experiment_id)}</td></tr>
                        <tr><td>Project Name</td><td>{esc(exp.project_name)}</td></tr>
                        <tr><td>Model Type</td><td>{esc(exp.model_type)}</td></tr>
                        <tr><td>Dataset Name</td><td>{esc(exp.dataset_name)}</td></tr>
                        <tr><td>Validation Strategy</td><td>{esc(exp.validation_strategy)}</td></tr>
                        <tr><td>Class Balance</td><td>{esc(exp.class_balance)}</td></tr>
                        <tr><td>Failure Observation</td><td>{esc(exp.failure_observation)}</td></tr>
                        <tr><td>Engineer Notes</td><td>{esc(exp.engineer_notes)}</td></tr>
                    </tbody>
                </table>

                <details style="margin-top: 16px;">
                    <summary style="cursor: pointer; color: var(--accent); font-weight: 600; outline: none;">Show Full JSON Payload</summary>
                    <pre style="margin-top: 10px;"><code>{esc(full_experiment_json)}</code></pre>
                </details>
            </div>
        </section>

        <!-- FAILURE DIAGNOSIS SECTION -->
        <section id="diagnosis" class="report-section">
            <h2>Failure Diagnosis</h2>
            <div class="grid-2">
                <div class="card">
                    <div class="card-title">Failure Classification</div>
                    <div class="gap-10">
                        <p><strong>Inferred Failure Category:</strong> <span style="font-size: 1.1rem; color: var(--accent); font-weight: 700;">{esc(ctx.classification.failure_category.value if ctx.classification else 'Unknown')}</span></p>
                        <p><strong>Calibration Confidence:</strong> <strong>{esc(ctx.classification.confidence if ctx.classification else 0.0)}</strong></p>
                        <p><strong>Conflict Resolution:</strong> {esc(ctx.classification.conflict_resolution if ctx.classification else '')}</p>
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Root Cause Analysis</div>
                    <div class="gap-10">
                        <p><strong>Root Cause:</strong> {esc(ctx.diagnosis.root_cause if ctx.diagnosis else '')}</p>
                        <p><strong>Violated Assumption:</strong> <em>{esc(ctx.diagnosis.violated_assumption if ctx.diagnosis else '')}</em></p>
                        <p><strong>Knowledge Gap:</strong> {esc(ctx.diagnosis.knowledge_gap if ctx.diagnosis else '')}</p>
                    </div>
                </div>
            </div>

            <div class="grid-2">
                <div class="card">
                    <div class="card-title">Supporting Evidence</div>
                    <ul class="gap-6" style="padding-left: 16px;">
                        {"".join(f"<li>{esc(item)}</li>" for item in (ctx.diagnosis.evidence if ctx.diagnosis else [])) or "<li>No specific evidence.</li>"}
                    </ul>
                </div>
                <div class="card">
                    <div class="card-title">Counter Evidence & Uncertainty</div>
                    <p><strong>Counter Evidence:</strong></p>
                    <ul class="gap-6" style="padding-left: 16px; margin-bottom: 12px;">
                        {"".join(f"<li>{esc(item)}</li>" for item in (ctx.diagnosis.counter_evidence if ctx.diagnosis else [])) or "<li>No strong counter evidence.</li>"}
                    </ul>
                    <p><strong>Uncertainties:</strong></p>
                    <ul class="gap-6" style="padding-left: 16px;">
                        {"".join(f"<li>{esc(item)}</li>" for item in (ctx.diagnosis.reflection_notes if ctx.diagnosis else [])) or "<li>None</li>"}
                    </ul>
                </div>
            </div>

            <h2>Failure Metrics Degradation</h2>
            <div class="card">
                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Current Value</th>
                            <th>Baseline Value</th>
                            <th>Difference</th>
                        </tr>
                    </thead>
                    <tbody>
                        {metrics_table}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- AGENT WORKFLOW SECTION -->
        <section id="workflow" class="report-section">
            <h2>Agent Execution Timeline</h2>
            <div class="gap-10" style="margin-bottom: 32px;">
                {agent_workflow_html}
            </div>

            <h2>Agent Detailed Reasoning Trace</h2>
            <div class="gap-6">
                {reasoning_trace_html}
            </div>
        </section>

        <!-- GROUNDING EVIDENCE SECTION -->
        <section id="grounding" class="report-section">
            <h2>Foundry IQ Grounded Evidence</h2>
            <p style="color: var(--text-muted); margin-bottom: 20px; font-size: 0.95rem;">
                The reasoning agents consulted the following registered Microsoft skill standards and remediation playbooks to formulate the diagnosis and recommendations.
            </p>
            <div class="gap-10">
                {citations_html}
            </div>
        </section>

        <!-- REMEDIATION & CERTS SECTION -->
        <section id="remediation" class="report-section">
            <h2>Remediation Plan</h2>
            <div class="grid-2">
                <div class="card">
                    <div class="card-title">3-Day Fast Fix</div>
                    <ul class="gap-6" style="padding-left: 16px; line-height: 1.5;">
                        {three_day}
                    </ul>
                </div>
                <div class="card">
                    <div class="card-title">7-Day Integration Plan</div>
                    <ul class="gap-6" style="padding-left: 16px; line-height: 1.5;">
                        {seven_day}
                    </ul>
                </div>
            </div>

            <div class="card" style="margin-bottom: 24px;">
                <div class="card-title">Hands-on Lab Exercise</div>
                <p style="line-height: 1.6;">{esc(hands_on_lab)}</p>
                <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border-color); font-size: 0.85rem; color: var(--warning);">
                    <strong>Responsible AI note:</strong> {esc(responsible_ai_note)}
                </div>
            </div>

            <h2>Microsoft Skill Readiness Assessment</h2>
            <div class="card" style="margin-bottom: 24px;">
                <div class="card-title">Certification Alignment</div>
                <p><strong>Recommended Exam:</strong> <strong>{esc(cert_name)}</strong></p>
                <p><strong>Skill Domain:</strong> {esc(cert_domain)}</p>
                <p style="margin-top: 12px;"><strong>Required Learning Path Modules:</strong></p>
                <ul class="gap-6" style="padding-left: 16px; margin-top: 6px;">
                    {cert_learning_path}
                </ul>
            </div>

            <h2>Practice Practice Questions</h2>
            <div class="gap-10">
                {cert_questions_html}
            </div>
        </section>

        <!-- PROOF SECTION -->
        <section id="proof" class="report-section">
            <h2>Azure Production Proof</h2>
            <div class="card" style="margin-bottom: 24px;">
                <table>
                    <thead>
                        <tr>
                            <th>Integration Layer</th>
                            <th>Status / Configuration</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>Foundry OpenAI Model Deployment</td><td><code style="color: var(--accent);">{esc(provider_proof.get('model', 'grok-4-20-reasoning'))}</code></td></tr>
                        <tr><td>Reasoning LLM Provider</td><td><strong>{esc(model_provider)}</strong></td></tr>
                        <tr><td>Azure AI Search (Live Grounding)</td><td><strong>{live_search}</strong></td></tr>
                        <tr><td>Cosmos DB (Reasoning Trace Storage)</td><td><strong>{live_cosmos}</strong></td></tr>
                        <tr><td>Azure Blob Storage (Report Upload)</td><td><strong>{live_blob}</strong></td></tr>
                    </tbody>
                </table>
            </div>

            <h2>Honest Limitations & Disclaimers</h2>
            <div class="card" style="border-left: 4px solid var(--warning); background-color: rgba(245, 158, 11, 0.03);">
                <p style="line-height: 1.6;">
                    {esc(honest_limitation)}
                </p>
                <p style="line-height: 1.6; margin-top: 12px; font-size: 0.85rem; color: var(--text-muted);">
                    Disclaimer: FailureLens IQ is a reasoning post-mortem assistant. All recommendations, certification maps, and code playbooks are generated from knowledge bases. Final code changes should be validated by human ML engineers before production deployment.
                </p>
            </div>
        </section>

    </main>

    <script>
        function showSection(id, element) {{
            document.querySelectorAll('.report-section').forEach(s => s.style.display = 'none');
            const targetSection = document.getElementById(id);
            if (targetSection) {{
                targetSection.style.display = 'block';
            }}
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            if (element) {{
                element.classList.add('active');
            }}
        }}
    </script>
</body>
</html>
"""
        return html_content

    def generate_html_report_file(
        self,
        ctx: AgentContext,
        original_prompt: str,
        prompt_extraction: dict[str, Any],
        analysis_result: dict[str, Any]
    ) -> Path:
        html_str = self.generate_html(ctx, original_prompt, prompt_extraction, analysis_result)
        path = self.output_dir / f"{ctx.experiment.experiment_id}.html"
        path.write_text(html_str, encoding="utf-8")
        return path
