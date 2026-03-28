"""Seed Waypoint 360 database from Commercial Workshop PDF (3/9/26) data.

This file contains all program data extracted from the Delivery Planning Work Session
and supplemented with context from Alex's CLAUDE.md project documentation.
"""
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import (
    Program, Phase, Gate, GateExitCriteria, Workstream, Person,
    Deliverable, Dependency, Risk, Decision,
)
from app.models.gate import GateStatus, CriteriaStatus
from app.models.workstream import WorkstreamStatus
from app.models.deliverable import DeliverableStatus
from app.models.dependency import DependencyType, DependencyStatus, Criticality
from app.models.risk import Severity, Likelihood, RiskStatus
from app.models.decision import DecisionStatus
from app.models.person import UserRole


async def seed_waypoint_data(db: AsyncSession):
    """Seed full Waypoint program from Commercial Workshop PDF."""

    # Check if already seeded
    existing = await db.execute(select(Program).limit(1))
    if existing.scalar_one_or_none():
        return

    # --- PROGRAM ---
    program = Program(
        name="Project Waypoint",
        description="Agentic Shopping & Booking -- Help customers search, compare, and book flights through natural dialog via 1P (southwest.com) and 3P (ChatGPT) channels, with merchandising integration.",
        start_date=date(2026, 3, 9),
        end_date=date(2026, 6, 15),
        status="active",
    )
    db.add(program)
    await db.flush()

    # --- PHASES ---
    phases = [
        Phase(program_id=program.id, name="Align", description="Communicate scope priorities, stand up the team, decision structures, and plans so inception starts at pace.", start_week=0, end_week=2, goal="Core team confirmed; inception workplan approved; decision forums defined", key_activities="Confirm core team; define decision forums; build inception delivery plan and milestones", exit_criteria="Core team confirmed; inception workplan approved; decision forums defined; no-regrets tech work signaled", sort_order=0),
        Phase(program_id=program.id, name="Incept", description="Converge on a build-ready, value-backed scope and MVP solutions for Agentic Shopping & Booking mission.", start_week=3, end_week=12, goal="Gate 5 passed: development readiness confirmed", key_activities="Integrated discovery, design, feasibility, and value definition across workstreams; stage gate reviews at Wk 4, 6, 8, 10, 12", exit_criteria="Gate 5 passed: development readiness confirmed", sort_order=1),
        Phase(program_id=program.id, name="Deliver", description="Translate inception outputs into an executable backlog; begin development.", start_week=13, end_week=None, goal="MVPs delivered; delivery governance operating at cadence", key_activities="Features/stories; integrated delivery plan; steady-state governance cadence", exit_criteria="MVPs delivered; delivery governance operating at cadence", sort_order=2),
    ]
    db.add_all(phases)
    await db.flush()

    phase_map = {p.name: p.id for p in phases}

    # --- GATES (from PDF: Draft Align & Incept Stage Gates) ---
    gates_data = [
        {
            "name": "Establish Operating Clarity",
            "short_name": "ALIGN",
            "phase": "Align",
            "week": 2,
            "description": "Communicate scope priorities, stand up the operating model, and ensure the team, decision structures, and plans are in place so inception starts at pace.",
            "criteria": [
                "Scope cascaded: High-level scope/priorities confirmed -- enough direction to begin inception planning",
                "Workstream ownership confirmed: All owners have capacity committed; boundaries between workstreams documented",
                "Operating structure defined: Inception workplan, decision forums, and mtg/status cadence established",
                "No-regrets work signaled: Technology work identified and communicated ahead of PI planning",
            ],
        },
        {
            "name": "Set the Direction",
            "short_name": "INCEPT 1",
            "phase": "Incept",
            "week": 4,
            "description": "Confirm enough directional guidance across all workstreams that detailed scoping, design, and architecture can begin with confidence.",
            "criteria": [
                "Shared context established: Directional traveler insights, business process maps, initial technical landscape, and draft MVP scope in hand -- enough for detailed design, scoping, and architecture to advance",
                "Constraints inventoried: Technical, regulatory, and organizational constraints mapped -- enough to inform scope and trade-off decisions leading into Gate 2",
            ],
        },
        {
            "name": "Lock Scope & Requirements",
            "short_name": "INCEPT 2",
            "phase": "Incept",
            "week": 6,
            "description": "Lock business scope, technical requirements, and testing plans. After this gate, scope changes require explicit trade-off decisions.",
            "criteria": [
                "Scope locked: MVP scope and requirements confirmed, informed by discovery findings -- further changes require explicit trade-off decisions",
                "Process requirements emerging: Draft Agent Design Cards in progress for primary booking flows",
                "Value framework defined: KPIs, measurement approach, and preliminary value estimates in place",
                "Prototype test plan finalized: Who we're testing with, what we're testing, how findings are captured, and who's in the room",
            ],
        },
        {
            "name": "Validate with Customers",
            "short_name": "INCEPT 3",
            "phase": "Incept",
            "week": 8,
            "description": "Test the experience concept with real travelers and capture evidence -- across customer desirability, technical feasibility, and process reality -- that confirms the direction or forces a pivot.",
            "criteria": [
                "Prototypes tested: Real travelers validate the experience with Customer Experience / Agent & Solution Delivery participating",
                "Evidence synthesized: Customer desirability, technical feasibility, and process reality assessed -- direction confirmed or pivot(s) identified",
                "Architecture converging: Substantially complete; knowledge and data strategy defined",
                "Governance/risk/compliance drafted: Compliance and regulatory requirements drafted",
            ],
        },
        {
            "name": "Finalize Solution & Value",
            "short_name": "INCEPT 4",
            "phase": "Incept",
            "week": 10,
            "description": "Converge prototype evidence, refined designs, architecture, and financial analysis into a fully defined solution and credible business case.",
            "criteria": [
                "Specifications complete: Experience design, solution architecture, data, governance/risk/compliance, and process specs defined",
                "Business case quantified: Initial evidence-grounded ROI incorporating prototype findings",
                "Delivery readiness staged: Dev capacity secured and high-level delivery plan in place",
            ],
        },
        {
            "name": "Confirm Dev Readiness",
            "short_name": "INCEPT 5",
            "phase": "Incept",
            "week": 12,
            "description": "Confirm dev teams are secured and equipped to begin translating solution requirements into detailed development plans.",
            "criteria": [
                "Specs accepted: Reviewed by development teams with no open ambiguities blocking sprint planning",
                "Business case packaged: Ready for executive review",
            ],
        },
    ]

    gate_objects = []
    for i, gd in enumerate(gates_data):
        gate = Gate(
            program_id=program.id,
            phase_id=phase_map[gd["phase"]],
            name=gd["name"],
            short_name=gd["short_name"],
            description=gd["description"],
            week_number=gd["week"],
            status=GateStatus.IN_PROGRESS if i == 0 else GateStatus.NOT_STARTED,
            sort_order=i,
        )
        db.add(gate)
        await db.flush()

        for j, crit in enumerate(gd["criteria"]):
            ec = GateExitCriteria(
                gate_id=gate.id,
                description=crit,
                status=CriteriaStatus.IN_PROGRESS if i == 0 else CriteriaStatus.NOT_STARTED,
                sort_order=j,
            )
            db.add(ec)

        gate_objects.append(gate)

    await db.flush()
    gate_map = {g.short_name: g for g in gate_objects}

    # --- PEOPLE (from PDF workstream table) ---
    people_data = [
        ("Nicola", "Customer Experience Lead", "SWA", UserRole.OWNER),
        ("Haylee", "Process Discovery & Design Lead", "SWA", UserRole.OWNER),
        ("Hursh", "Business Strategy & Experience Design Lead", "ProServ", UserRole.OWNER),
        ("Preethi Elango", "Agent & Solution Delivery Sr. Manager", "SWA", UserRole.OWNER),
        ("Jon H (John Hartfield)", "Solution Architect", "SWA", UserRole.OWNER),
        ("Julie", "AgentOps Manager", "SWA", UserRole.OWNER),
        ("Alex Kirschke", "AgentOps Lead", "SWA", UserRole.ADMIN),
        ("Jenn", "AI Governance, Risk & Compliance Lead", "SWA", UserRole.OWNER),
        ("John", "Program Management Lead", "SWA", UserRole.OWNER),
        ("TBD - Cyber Owner", "Cyber Lead", "SWA", UserRole.OWNER),
        ("Peter", "Program Lead - Waypoint Inception", "SWA", UserRole.VIEWER),
        ("Tamara", "Skip-Level Leader", "SWA", UserRole.VIEWER),
        ("Justin", "Leadership", "SWA", UserRole.VIEWER),
        ("Mark", "Business Lead", "SWA", UserRole.VIEWER),
        ("Tess (Tesfagabir Meharizghi)", "Tech Lead - Delivery", "SWA", UserRole.VIEWER),
        ("Chris Haseltine", "Sr. Data Scientist / AI Engineer", "SWA", UserRole.VIEWER),
        ("Aaron Chew", "AgentOps", "SWA", UserRole.VIEWER),
        ("Isaac", "Platform & Data", "SWA", UserRole.VIEWER),
        ("Britton", "Technical Collaborator", "SWA", UserRole.VIEWER),
        ("Kevin", "Data Engineering - Dashboard Lead", "SWA", UserRole.VIEWER),
        ("Suresh", "Architecture", "SWA", UserRole.VIEWER),
        ("Bri", "Solution Design", "SWA", UserRole.VIEWER),
        ("Stephanie Baxter", "Waypoint Build Team", "SWA", UserRole.VIEWER),
    ]
    person_objects = {}
    for name, title, org, role in people_data:
        p = Person(name=name, title=title, organization=org, role=role)
        db.add(p)
        await db.flush()
        person_objects[name] = p

    # --- WORKSTREAMS (from PDF: Draft Inception Workstreams table) ---
    workstreams_data = [
        {
            "name": "Customer Experience",
            "short_name": "CX",
            "owner": "Nicola",
            "purpose": "Surface traveler needs, define validation criteria for prototype testing, and facilitate/validate prototype testing to ensure customer needs are met.",
            "scope_in": "Customer research, interaction findings, concept test results, validation criteria definition, prototype testing facilitation",
            "scope_out": "Agent implementation, architecture decisions, commercial strategy",
            "deliverables": {
                "ALIGN": ["Customer research plan", "Initial traveler insight inventory"],
                "INCEPT 1": ["Directional traveler insights", "Concept test criteria"],
                "INCEPT 2": ["Validated interaction findings", "Prototype testing plan"],
                "INCEPT 3": ["Concept test results with real travelers", "Validation criteria refinement"],
                "INCEPT 4": ["Final customer validation report", "Experience recommendation brief"],
                "INCEPT 5": ["Customer acceptance criteria for sprint planning"],
            },
        },
        {
            "name": "Process Discovery & Design",
            "short_name": "Process",
            "owner": "Haylee",
            "purpose": "Map current-state business processes and define process-level requirements (Agent Design Cards).",
            "scope_in": "Current/future state process maps, Agent Design Cards, booking flow documentation",
            "scope_out": "Technology implementation, UI/UX design, prototype building",
            "deliverables": {
                "ALIGN": ["Process discovery kickoff plan"],
                "INCEPT 1": ["Current-state business process maps", "Initial Agent Design Card templates"],
                "INCEPT 2": ["Draft Agent Design Cards for primary booking flows"],
                "INCEPT 3": ["Validated process maps incorporating prototype feedback"],
                "INCEPT 4": ["Finalized Agent Design Cards", "Future-state process specifications"],
                "INCEPT 5": ["Process specs reviewed by dev teams"],
            },
        },
        {
            "name": "Business Strategy & Value Case",
            "short_name": "BizStrat",
            "owner": "Hursh",
            "purpose": "Define what we're building and why; size value pools, establish KPIs and measurement approach, and build the evidence-grounded business case.",
            "scope_in": "Competitive analysis, MVP scope doc, value model, KPI framework, business case",
            "scope_out": "Technical architecture, prototype building, customer research execution",
            "deliverables": {
                "ALIGN": ["Competitive landscape draft", "Value pool sizing approach"],
                "INCEPT 1": ["Competitive analysis v1", "Draft MVP scope document"],
                "INCEPT 2": ["KPI framework", "Preliminary value estimates", "Measurement approach"],
                "INCEPT 3": ["Value model updated with prototype evidence"],
                "INCEPT 4": ["Evidence-grounded business case", "ROI analysis"],
                "INCEPT 5": ["Executive-ready business case package"],
            },
        },
        {
            "name": "Experience & Conversation Design",
            "short_name": "ExpDesign",
            "owner": "Hursh",
            "purpose": "Design the conversational booking experience -- agent behavior, traveler interaction, fit within shopping/booking flow.",
            "scope_in": "UX concepts, conversation flows, prototype mockups, degradation specs",
            "scope_out": "Backend implementation, infrastructure, data modeling",
            "deliverables": {
                "ALIGN": ["Design approach and principles"],
                "INCEPT 1": ["UX concept directions", "Initial conversation flow drafts"],
                "INCEPT 2": ["Prototype mockups for testing", "Degradation specifications"],
                "INCEPT 3": ["Refined designs incorporating test feedback"],
                "INCEPT 4": ["Final experience design specifications"],
                "INCEPT 5": ["Design specs accepted by dev teams"],
            },
        },
        {
            "name": "Agent & Solution Delivery",
            "short_name": "SolDel",
            "owner": "Preethi Elango",
            "purpose": "Design the solution -- systems, agent orchestration, infrastructure. Map knowledge/data requirements, schemas, sourcing, integration complexity. Participate in prototype testing to inform feasibility/LOE.",
            "scope_in": "Technical discovery, feasibility assessment, MVP architecture, integration specs, NFRs, data landscape, data model, sourcing plan, complexity assessment",
            "scope_out": "Business strategy, customer research, regulatory policy",
            "deliverables": {
                "ALIGN": ["Technical discovery plan", "Architecture approach"],
                "INCEPT 1": ["Initial technical landscape assessment", "Draft architecture direction"],
                "INCEPT 2": ["MVP architecture spec", "Integration specs", "NFR baseline", "Data model draft"],
                "INCEPT 3": ["Feasibility report from prototype testing", "Architecture convergence doc"],
                "INCEPT 4": ["Final solution architecture", "Data landscape", "Sourcing plan", "Complexity assessment"],
                "INCEPT 5": ["Architecture specs reviewed by dev teams", "Sprint-ready technical backlog"],
            },
        },
        {
            "name": "AgentOps",
            "short_name": "AgentOps",
            "owner": "Julie",
            "purpose": "Define evaluation framework, observability, and analytics requirements for agentic experiences.",
            "scope_in": "Evaluation framework, observability/analytics requirements, 14 evaluators, cost architecture, DTC pipeline integration, 1P vs 3P observability scoping",
            "scope_out": "Agent implementation, UI development, business case",
            "deliverables": {
                "ALIGN": ["AgentOps inception plan", "1P vs 3P observability scoping"],
                "INCEPT 1": ["Observability landscape assessment", "Draft eval/metrics framework"],
                "INCEPT 2": ["Evaluation framework spec", "Metrics taxonomy", "FMEA session output"],
                "INCEPT 3": ["Prototype observability integration", "Evaluator coverage validation"],
                "INCEPT 4": ["Final evaluation framework", "Cost model", "Dashboard requirements"],
                "INCEPT 5": ["Eval framework reviewed by dev teams", "Monitoring group configuration"],
            },
        },
        {
            "name": "Prototyping & Validation",
            "short_name": "Proto",
            "owner": "Hursh",
            "purpose": "Design, build, and test prototypes with real travelers -- in collaboration with Customer Experience (validation) and Solution Delivery (feasibility) -- and synthesize findings across workstreams.",
            "scope_in": "Prototype designs, user testing results, findings synthesis",
            "scope_out": "Production code, final architecture, business case financials",
            "deliverables": {
                "ALIGN": ["Prototype approach and tooling plan"],
                "INCEPT 1": ["Prototype concept directions"],
                "INCEPT 2": ["Testable prototype v1", "Test plan finalized"],
                "INCEPT 3": ["User testing results", "Findings synthesis report"],
                "INCEPT 4": ["Refined prototype incorporating feedback", "Final findings report"],
                "INCEPT 5": ["Prototype artifacts handed off to dev teams"],
            },
        },
        {
            "name": "AI Governance, Risk & Compliance",
            "short_name": "GovRisk",
            "owner": "Jenn",
            "purpose": "Identify regulatory, privacy, disclosure, and policy requirements early.",
            "scope_in": "Compliance landscape assessment, requirement drafts, finalized requirements, regulatory review, privacy assessment, disclosure requirements",
            "scope_out": "Technical implementation, testing, business strategy",
            "deliverables": {
                "ALIGN": ["Regulatory landscape scan", "Initial compliance checklist"],
                "INCEPT 1": ["Compliance landscape assessment draft"],
                "INCEPT 2": ["Draft compliance requirements", "Privacy impact assessment"],
                "INCEPT 3": ["Governance/risk/compliance requirements drafted"],
                "INCEPT 4": ["Finalized compliance requirements", "Disclosure specifications"],
                "INCEPT 5": ["Compliance requirements accepted by dev teams"],
            },
        },
        {
            "name": "Program Management",
            "short_name": "PgmMgmt",
            "owner": "John",
            "purpose": "Coordinate timelines, dependencies, resourcing; facilitate cross-workstream integration & stage-gate reviews; produce MVP delivery plan.",
            "scope_in": "Delivery plan, RAID log, resource plan, cross-workstream coordination, gate reviews",
            "scope_out": "Technical decisions, business strategy, customer research",
            "deliverables": {
                "ALIGN": ["Inception workplan", "Decision forum structure", "RAID log v1"],
                "INCEPT 1": ["Updated delivery plan", "Resource allocation matrix"],
                "INCEPT 2": ["RAID log updated", "Dependency map v1", "Gate review facilitation"],
                "INCEPT 3": ["Cross-workstream integration report", "Updated resource plan"],
                "INCEPT 4": ["High-level delivery plan", "Final resource commitments"],
                "INCEPT 5": ["Sprint-ready delivery plan", "Dev resourcing confirmed"],
            },
        },
        {
            "name": "Cyber",
            "short_name": "Cyber",
            "owner": "TBD - Cyber Owner",
            "purpose": "Assess cyber threat landscape and define security requirements for agentic experiences -- including threat monitoring, data protection, and secure integration with internal systems and third-party platforms.",
            "scope_in": "Cyber threat assessment, security requirements, threat monitoring plan, secure integration specifications",
            "scope_out": "Business logic, customer experience design, financial modeling",
            "deliverables": {
                "ALIGN": ["Cyber engagement plan", "Initial threat landscape scan"],
                "INCEPT 1": ["Threat landscape assessment draft"],
                "INCEPT 2": ["Security requirements draft", "Data protection assessment"],
                "INCEPT 3": ["Threat monitoring plan draft", "Secure integration review"],
                "INCEPT 4": ["Finalized security requirements", "Threat monitoring plan"],
                "INCEPT 5": ["Security specs accepted by dev teams", "Secure integration specifications"],
            },
        },
    ]

    ws_objects = {}
    for i, wsd in enumerate(workstreams_data):
        owner = person_objects.get(wsd["owner"])
        ws = Workstream(
            program_id=program.id,
            name=wsd["name"],
            short_name=wsd["short_name"],
            purpose=wsd["purpose"],
            scope_in=wsd["scope_in"],
            scope_out=wsd["scope_out"],
            baseline_scope=wsd["scope_in"],  # Baseline = initial scope for creep detection
            owner_id=owner.id if owner else None,
            status=WorkstreamStatus.ON_TRACK if i < 9 else WorkstreamStatus.AT_RISK,
            sort_order=i,
        )
        db.add(ws)
        await db.flush()
        ws_objects[wsd["short_name"]] = ws

        # Create deliverables per gate
        for gate_short, deliverable_names in wsd["deliverables"].items():
            gate = gate_map.get(gate_short)
            if gate:
                for dn in deliverable_names:
                    d = Deliverable(
                        workstream_id=ws.id,
                        gate_id=gate.id,
                        name=dn,
                        status=DeliverableStatus.IN_PROGRESS if gate_short == "ALIGN" else DeliverableStatus.NOT_STARTED,
                    )
                    db.add(d)

    await db.flush()

    # --- DEPENDENCIES (cross-workstream, extracted from PDF relationships + CLAUDE.md context) ---
    deps_data = [
        # CX <-> Proto (tight coupling on prototype testing)
        ("Proto", "CX", "INCEPT 2", "Prototype test plan requires CX validation criteria", DependencyType.NEEDS_FROM, Criticality.CRITICAL),
        ("CX", "Proto", "INCEPT 3", "CX needs prototype test results to validate findings", DependencyType.NEEDS_FROM, Criticality.CRITICAL),

        # Proto <-> SolDel (feasibility)
        ("Proto", "SolDel", "INCEPT 3", "Prototype testing needs Solution Delivery participation for feasibility assessment", DependencyType.NEEDS_FROM, Criticality.HIGH),

        # ExpDesign -> Proto (designs feed prototypes)
        ("Proto", "ExpDesign", "INCEPT 2", "Prototypes require conversation design mockups", DependencyType.NEEDS_FROM, Criticality.CRITICAL),

        # Process -> SolDel (Agent Design Cards inform architecture)
        ("SolDel", "Process", "INCEPT 2", "Architecture needs Agent Design Cards to define agent behaviors", DependencyType.NEEDS_FROM, Criticality.HIGH),

        # SolDel -> AgentOps (architecture informs observability)
        ("AgentOps", "SolDel", "INCEPT 1", "AgentOps needs architecture direction to scope observability", DependencyType.NEEDS_FROM, Criticality.CRITICAL),

        # BizStrat -> Proto (value model needs prototype evidence)
        ("BizStrat", "Proto", "INCEPT 3", "Business case needs prototype testing evidence for ROI grounding", DependencyType.NEEDS_FROM, Criticality.HIGH),

        # GovRisk -> SolDel (compliance requirements constrain architecture)
        ("SolDel", "GovRisk", "INCEPT 2", "Architecture must incorporate compliance/regulatory requirements", DependencyType.NEEDS_FROM, Criticality.HIGH),

        # Cyber -> SolDel (security requirements constrain integration)
        ("SolDel", "Cyber", "INCEPT 2", "Solution design needs security requirements for integration specs", DependencyType.NEEDS_FROM, Criticality.HIGH),

        # AgentOps -> GovRisk (eval framework needs governance alignment)
        ("AgentOps", "GovRisk", "INCEPT 2", "Evaluation framework needs governance requirements for compliance evaluators", DependencyType.NEEDS_FROM, Criticality.MEDIUM),

        # PgmMgmt depends on ALL workstreams for status
        ("PgmMgmt", "SolDel", "INCEPT 2", "Delivery plan needs architecture direction and complexity assessment", DependencyType.NEEDS_FROM, Criticality.HIGH),
        ("PgmMgmt", "BizStrat", "INCEPT 4", "Delivery plan needs business case for executive review", DependencyType.NEEDS_FROM, Criticality.MEDIUM),

        # CX -> ExpDesign (traveler insights inform design)
        ("ExpDesign", "CX", "INCEPT 1", "Experience design needs directional traveler insights", DependencyType.NEEDS_FROM, Criticality.HIGH),

        # SolDel -> BizStrat (technical feasibility informs value model)
        ("BizStrat", "SolDel", "INCEPT 3", "Value model needs technical feasibility assessment for cost estimates", DependencyType.NEEDS_FROM, Criticality.MEDIUM),
    ]

    for src_short, tgt_short, gate_short, desc, dep_type, crit in deps_data:
        src = ws_objects.get(src_short)
        tgt = ws_objects.get(tgt_short)
        gate = gate_map.get(gate_short)
        if src and tgt and gate:
            dep = Dependency(
                source_workstream_id=src.id,
                target_workstream_id=tgt.id,
                gate_id=gate.id,
                description=desc,
                dep_type=dep_type,
                status=DependencyStatus.OPEN,
                criticality=crit,
            )
            db.add(dep)

    # --- RISKS (from CLAUDE.md critical blockers + inferred from PDF) ---
    risks_data = [
        ("SolDel", "Legal hasn't cleared OpenAI/SWA agreement -- blocks all 3P architecture work", Severity.CRITICAL, Likelihood.HIGH, "Escalate to leadership immediately", "dependency"),
        ("SolDel", "3P architecture pattern not formalized (Pattern 1 vs 2 vs 3) -- blocks evaluator scoping, cost modeling, FMEA", Severity.HIGH, Likelihood.HIGH, "Target Pattern 2 ratification by Gate 2", "technical"),
        ("SolDel", "Chris Haseltine leaving ~7 weeks -- key 3P architecture voice unavailable during critical decision period", Severity.HIGH, Likelihood.HIGH, "Identify Tess as backup for 3P pattern decision", "resourcing"),
        ("SolDel", "Dotcom team capacity = 0 planned for Waypoint -- 1P stalls if unresolved by Gate 2", Severity.CRITICAL, Likelihood.MEDIUM, "Requires LPM/leadership mandate", "resourcing"),
        ("AgentOps", "Cannot baseline AgentOps eval without scope locked -- mitigated by Herbie dev environment for directional baselines", Severity.MEDIUM, Likelihood.MEDIUM, "Use Herbie dev infrastructure for observability/eval baselines", "scope"),
        ("AgentOps", "Infeasible task handling -- best models at 53.9% accuracy on infeasible task refusal", Severity.MEDIUM, Likelihood.HIGH, "Phase 1: pattern analysis. Phase 2: dedicated evaluator", "technical"),
        ("ExpDesign", "ChatGPT framing misrepresentation -- wraps SWA data in its own language around HTML widgets", Severity.MEDIUM, Likelihood.HIGH, "HTML widgets mitigate for structured data; conversational framing unchecked", "technical"),
        ("Cyber", "Cyber workstream owner TBD -- no assigned lead creates governance gap", Severity.HIGH, Likelihood.HIGH, "Escalate to leadership for assignment", "resourcing"),
        ("PgmMgmt", "Partner team capacity not secured -- blocked", Severity.HIGH, Likelihood.MEDIUM, "Requires leadership engagement", "resourcing"),
        ("CX", "Business SMEs for customer intent not identified -- may use CS reps as fallback", Severity.MEDIUM, Likelihood.MEDIUM, "Identify SMEs or formally approve CS rep fallback", "resourcing"),
        ("BizStrat", "Merchandising scope decision pending -- in/out of discovery TBD by Mark", Severity.MEDIUM, Likelihood.MEDIUM, "Mark to decide merchandising scope for discovery", "scope"),
        ("SolDel", "API connectivity is long pole -- mapping functional requirements to digital APIs", Severity.HIGH, Likelihood.HIGH, "Jeff Hill leading API mapping; scores of APIs need distilling", "technical"),
    ]

    for ws_short, desc, sev, lik, mit, cat in risks_data:
        ws = ws_objects.get(ws_short)
        if ws:
            risk = Risk(
                workstream_id=ws.id,
                description=desc,
                severity=sev,
                likelihood=lik,
                mitigation=mit,
                status=RiskStatus.OPEN,
                category=cat,
            )
            db.add(risk)

    # --- DECISIONS NEEDED (from PDF + CLAUDE.md) ---
    decisions_data = [
        ("SolDel", "INCEPT 1", "Formalize 3P integration pattern (Pattern 1 vs 2 vs 3)", "Peter / Tess / Chris", "Blocks evaluator scoping, cost modeling, and FMEA"),
        ("SolDel", "ALIGN", "Resolve 1P vs 3P go-live sequencing contradiction", "Peter / Leadership", "3P first on paper vs 1P backend must come first in reality"),
        ("BizStrat", "INCEPT 1", "Confirm merchandising scope (in/out of discovery)", "Mark", "Affects discovery scope and business case"),
        ("Cyber", "ALIGN", "Assign Cyber workstream owner", "Leadership", "No lead creates governance gap across all gates"),
        ("SolDel", "ALIGN", "Legal clearance of OpenAI/SWA agreement", "Legal / Leadership", "Blocks all 3P architecture work"),
        ("SolDel", "INCEPT 2", "Confirm UI parity requirements across ChatGPT and Dotcom", "John Hartfield", "Affects 1P/3P architecture and component design"),
        ("AgentOps", "INCEPT 2", "Validate evaluation phasing (Phase 1 MVP vs Phase 2 R1)", "Alex / Britton / Peter", "Determines monitoring group configuration and cost model"),
        ("PgmMgmt", "INCEPT 1", "Secure Dotcom team capacity for Waypoint", "LPM / Leadership", "If unresolved by Gate 2, 1P stalls"),
    ]

    for ws_short, gate_short, desc, maker, impact in decisions_data:
        ws = ws_objects.get(ws_short)
        gate = gate_map.get(gate_short)
        if ws and gate:
            dec = Decision(
                workstream_id=ws.id,
                gate_id=gate.id,
                description=desc,
                status=DecisionStatus.NEEDED,
                decision_maker=maker,
                impact=impact,
            )
            db.add(dec)

    await db.commit()
