import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = r"E:\nexus-mind\report_images"
os.makedirs(OUT_DIR, exist_ok=True)

def get_font(size, bold=False):
    font_names = [
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\tahoma.ttf",
    ]
    if bold:
        font_names.insert(0, "C:\\Windows\\Fonts\\segoeuib.ttf")
        font_names.insert(1, "C:\\Windows\\Fonts\\arialbd.ttf")
    for f in font_names:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_header(draw, title, subtitle, width, tag="Knowledge Engine"):
    draw.rectangle([0, 0, width, 70], fill="#0f172a")
    draw.rectangle([0, 70, width, 72], fill="#334155")
    draw.text((30, 15), title, fill="#f8fafc", font=get_font(24, bold=True))
    draw.text((30, 44), subtitle, fill="#94a3b8", font=get_font(13))
    draw.rounded_rectangle([width - 250, 18, width - 30, 52], radius=6, fill="#1e293b", outline="#3b82f6", width=1)
    draw.text((width - 235, 26), f"● Nexus Mind :: {tag}", fill="#38bdf8", font=get_font(12, bold=True))

# =============================================================================
# 5. GROUNDED RAG KNOWLEDGE SEARCH ENGINE OUTPUT
# =============================================================================
def generate_search_engine_output():
    w, h = 1300, 780
    img = Image.new("RGB", (w, h), color="#090d16")
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Grounded RAG Knowledge & Documentation Search Engine", "256-Dim Dense Hypersphere Cosine Matching + BM25 Lexical Hybrid Fusion", w, "Grounded RAG")

    # Search Bar Box
    sb_x1, sb_y1, sb_x2, sb_y2 = 40, 95, w - 40, 155
    draw.rounded_rectangle([sb_x1, sb_y1, sb_x2, sb_y2], radius=8, fill="#1e293b", outline="#3b82f6", width=2)
    # Search icon / prompt
    draw.text((sb_x1 + 20, sb_y1 + 18), "🔍", font=get_font(16))
    query_text = "How does the safe tool calling protocol handle task deadline modifications and human approval?"
    draw.text((sb_x1 + 55, sb_y1 + 17), query_text, fill="#f8fafc", font=get_font(14, bold=True))
    # Search Meta badges on right
    draw.rounded_rectangle([sb_x2 - 190, sb_y1 + 12, sb_x2 - 15, sb_y2 - 12], radius=5, fill="#0f172a", outline="#64748b", width=1)
    draw.text((sb_x2 - 180, sb_y1 + 19), "Cosine: 60% | BM25: 40%", fill="#38bdf8", font=get_font(10, bold=True))

    # Top stats bar
    draw.text((45, 170), "Found 3 Grounded Results in 42 ms  |  Grounded Score: 0.948  |  Hallucination Rate: 0.00% (Strict Out-of-Scope Fallback)", fill="#94a3b8", font=get_font(11))

    # Left Panel: Synthesized Answer with Verified Citations (width: 740)
    ans_x1, ans_y1, ans_x2, ans_y2 = 40, 195, 800, h - 35
    draw.rounded_rectangle([ans_x1, ans_y1, ans_x2, ans_y2], radius=8, fill="#0f172a", outline="#334155", width=1)
    # Header of AI synthesized response
    draw.rectangle([ans_x1, ans_y1, ans_x2, ans_y1 + 45], fill="#1e293b")
    draw.text((ans_x1 + 20, ans_y1 + 14), "VERIFIED SYNTHESIZED ANSWER (ZERO HALLUCINATION GUARANTEE)", fill="#10b981", font=get_font(12, bold=True))

    # Answer Paragraph
    lines = [
        "According to the Enterprise Operational Architecture, all state-mutating actions triggered by AI agents",
        "(such as shifting task deadlines, altering assignees, or re-budgeting) cannot write directly to the database.",
        "",
        "Instead, the Safe Tool Calling Protocol enforces a two-phase commit gate:",
        "1. Formulation of Diff Proposal: The AI persona creates a structured Proposal JSON payload detailing",
        "    the target task ID, the original deadline, the recommended revised deadline, and mathematical justification.",
        "2. Human-in-the-Loop Review: The proposal is placed into PENDING state. A real-time notification alerts the",
        "    authorized Project Manager via the Web Tray and Flutter client.",
        "3. Verification & Commit: Only when an authorized manager clicks 'Approve & Execute', an atomic database",
        "    transaction mutates the entity and appends the decision trace to the immutable audit ledger.",
        "",
        "If a manager rejects or dismisses the proposal, the state change is discarded without altering active schedules."
    ]
    cur_y = ans_y1 + 65
    for line in lines:
        if line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
            draw.text((ans_x1 + 20, cur_y), line, fill="#38bdf8", font=get_font(12, bold=True))
        else:
            draw.text((ans_x1 + 20, cur_y), line, fill="#e2e8f0", font=get_font(12))
        cur_y += 24

    # Citation Cards at bottom of answer box
    draw.rectangle([ans_x1, ans_y2 - 130, ans_x2, ans_y2], fill="#131d31")
    draw.text((ans_x1 + 20, ans_y2 - 118), "VERIFIABLE CITATION SOURCES CITED:", fill="#94a3b8", font=get_font(11, bold=True))

    c1_x1, c1_y1, c1_x2, c1_y2 = ans_x1 + 20, ans_y2 - 95, ans_x1 + 360, ans_y2 - 18
    draw.rounded_rectangle([c1_x1, c1_y1, c1_x2, c1_y2], radius=6, fill="#1e293b", outline="#3b82f6", width=1)
    draw.text((c1_x1 + 10, c1_y1 + 8), "📄 architecture_specification.pdf", fill="#f8fafc", font=get_font(11, bold=True))
    draw.text((c1_x1 + 10, c1_y1 + 26), "Section 4.3: Safe Proposal Engine", fill="#38bdf8", font=get_font(10))
    draw.text((c1_x1 + 10, c1_y1 + 44), "Page: 28  |  Relevance: 97.4%", fill="#10b981", font=get_font(10, bold=True))

    c2_x1, c2_y1, c2_x2, c2_y2 = ans_x1 + 380, ans_y2 - 95, ans_x2 - 20, ans_y2 - 18
    draw.rounded_rectangle([c2_x1, c2_y1, c2_x2, c2_y2], radius=6, fill="#1e293b", outline="#334155", width=1)
    draw.text((c2_x1 + 10, c2_y1 + 8), "📄 security_governance_policy.md", fill="#f8fafc", font=get_font(11, bold=True))
    draw.text((c2_x1 + 10, c2_y1 + 26), "Section 2.1: Human Approval Protocol", fill="#38bdf8", font=get_font(10))
    draw.text((c2_x1 + 10, c2_y1 + 44), "Line: 142  |  Relevance: 92.1%", fill="#10b981", font=get_font(10, bold=True))

    # Right Panel: Retrieved Ranked Document Chunks (width: 440)
    rx1, ry1, rx2, ry2 = 825, 195, w - 40, h - 35
    draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=8, fill="#0f172a", outline="#334155", width=1)
    draw.rectangle([rx1, ry1, rx2, ry1 + 45], fill="#1e293b")
    draw.text((rx1 + 20, ry1 + 14), "TOP RANKED DENSE CHUNKS", fill="#f8fafc", font=get_font(12, bold=True))

    chunks = [
        {"title": "Chunk #104 [architecture_specification.pdf]", "sim": "Score: 0.962 (Dense)", "snippet": "...mutating tools must return ProposalPayload objects. FastAPIs router /api/proposals registers the diff for manager authorization before committing changes to tasks table..."},
        {"title": "Chunk #082 [security_governance_policy.md]", "sim": "Score: 0.918 (Hybrid)", "snippet": "...Human-in-the-loop review prevents unintended cascading slips in the project DAG. All rejected proposals are logged with auditor timestamps..."},
        {"title": "Chunk #215 [cpm_simulator_design.pdf]", "sim": "Score: 0.841 (BM25 Lexical)", "snippet": "...When deadlines shift, Kahn's algorithm recomputes Early Finish (EF) and Late Finish (LF) to assess if total slack drops to zero on critical path..."}
    ]

    cy = ry1 + 55
    for chk in chunks:
        ch_box_y2 = cy + 150
        draw.rounded_rectangle([rx1 + 15, cy, rx2 - 15, ch_box_y2], radius=6, fill="#131d31", outline="#334155", width=1)
        draw.text((rx1 + 25, cy + 10), chk["title"], fill="#38bdf8", font=get_font(11, bold=True))
        draw.text((rx2 - 170, cy + 10), chk["sim"], fill="#10b981", font=get_font(10, bold=True))
        # snippet text wrapped
        draw.text((rx1 + 25, cy + 34), chk["snippet"][:55], fill="#cbd5e1", font=get_font(10))
        draw.text((rx1 + 25, cy + 52), chk["snippet"][55:110], fill="#cbd5e1", font=get_font(10))
        draw.text((rx1 + 25, cy + 70), chk["snippet"][110:], fill="#cbd5e1", font=get_font(10))

        # View chunk button
        draw.rounded_rectangle([rx1 + 25, cy + 112, rx1 + 140, cy + 138], radius=4, fill="#1e293b", outline="#64748b", width=1)
        draw.text((rx1 + 35, cy + 118), "Inspect Chunk Vector", fill="#94a3b8", font=get_font(9, bold=True))

        cy += 165

    img.save(os.path.join(OUT_DIR, "search_engine_output.png"))
    print("Saved search_engine_output.png")

# =============================================================================
# 6. COPILOT MULTI-AGENT WAR ROOM CHAT TERMINAL
# =============================================================================
def generate_copilot_output():
    w, h = 1300, 780
    img = Image.new("RGB", (w, h), color="#090d16")
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Autonomous Multi-Agent AI War Room Copilot", "5 Specialized Personas, Step-by-Step Decision Trace Pipeline & Tool Call Approval", w, "Copilot Terminal")

    # Left Agent Persona Selector Sidebar (width: 280)
    sx1, sy1, sx2, sy2 = 30, 95, 300, h - 35
    draw.rounded_rectangle([sx1, sy1, sx2, sy2], radius=8, fill="#0f172a", outline="#334155", width=1)
    draw.rectangle([sx1, sy1, sx2, sy1 + 45], fill="#1e293b")
    draw.text((sx1 + 18, sy1 + 14), "SWARM PERSONAS (5 ACTIVE)", fill="#94a3b8", font=get_font(11, bold=True))

    agents = [
        {"name": "🤖 Project Manager Agent", "role": "Sprint Milestones & SLA Risks", "active": True},
        {"name": "💻 Developer Co-Pilot", "role": "Code Spikes & Task Decomp", "active": False},
        {"name": "🛡️ Security & Compliance", "role": "MFA, TOTP & Policy Audits", "active": False},
        {"name": "📚 Grounded RAG Agent", "role": "Verifiable Citation Retrieval", "active": False},
        {"name": "⚖️ Analytics & Workforce", "role": "Hungarian Skill Allocation", "active": False},
    ]
    ay = sy1 + 60
    for ag in agents:
        ab_bg = "#1e293b" if ag["active"] else "#0f172a"
        ab_border = "#3b82f6" if ag["active"] else "#1e293b"
        draw.rounded_rectangle([sx1 + 10, ay, sx2 - 10, ay + 65], radius=6, fill=ab_bg, outline=ab_border, width=1)
        draw.text((sx1 + 20, ay + 12), ag["name"], fill="#ffffff" if ag["active"] else "#cbd5e1", font=get_font(11, bold=True))
        draw.text((sx1 + 20, ay + 34), ag["role"], fill="#38bdf8" if ag["active"] else "#64748b", font=get_font(9))
        ay += 75

    # Health status in sidebar bottom
    draw.rounded_rectangle([sx1 + 10, sy2 - 110, sx2 - 10, sy2 - 15], radius=6, fill="#131d31", outline="#334155", width=1)
    draw.text((sx1 + 20, sy2 - 95), "SYSTEM AUDIT STATE", fill="#10b981", font=get_font(10, bold=True))
    draw.text((sx1 + 20, sy2 - 75), "• Permission Guard: ENFORCED", fill="#cbd5e1", font=get_font(9))
    draw.text((sx1 + 20, sy2 - 58), "• Role Scope: MANAGER", fill="#cbd5e1", font=get_font(9))
    draw.text((sx1 + 20, sy2 - 40), "• Decision Tracing: ENABLED", fill="#cbd5e1", font=get_font(9))

    # Right Main Chat & Decision Trace Area (width: 930)
    cx1, cy1, cx2, cy2 = 320, 95, w - 30, h - 35
    draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=8, fill="#0f172a", outline="#334155", width=1)

    # Message 1: User Prompt
    ux1, uy1, ux2, uy2 = cx1 + 25, cy1 + 20, cx2 - 25, cy1 + 75
    draw.rounded_rectangle([ux1, uy1, ux2, uy2], radius=6, fill="#1e293b", outline="#475569", width=1)
    draw.text((ux1 + 15, uy1 + 12), "👤 Engineering Manager (Dev Lead):", fill="#38bdf8", font=get_font(11, bold=True))
    draw.text((ux1 + 15, uy1 + 34), "\"Task #104 (Kahn's CPM Simulator Engine) is showing 88% delivery risk. Can you diagnose the blocker and propose a fix?\"", fill="#ffffff", font=get_font(12))

    # Message 2: Agent Response with Decision Trace
    ax1, ay1, ax2, ay2 = cx1 + 25, cy1 + 95, cx2 - 25, cy1 + 450
    draw.rounded_rectangle([ax1, ay1, ax2, ay2], radius=6, fill="#0b1329", outline="#3b82f6", width=1)
    draw.text((ax1 + 18, ay1 + 14), "🤖 Project Manager Agent (Autonomous Swarm Response):", fill="#10b981", font=get_font(12, bold=True))

    # Step-by-Step Decision Trace Pipeline Box
    tx1, ty1, tx2, ty2 = ax1 + 18, ay1 + 40, ax2 - 18, ay1 + 125
    draw.rounded_rectangle([tx1, ty1, tx2, ty2], radius=6, fill="#080e1e", outline="#334155", width=1)
    draw.text((tx1 + 15, ty1 + 10), "AI DECISION TRACE PIPELINE (EXECUTION AUDIT):", fill="#f59e0b", font=get_font(10, bold=True))

    traces = [
        "1. Intent Analysis: Task Blocker Diagnosis & Risk Remediation (Confidence: 0.98)",
        "2. Permission Check: Role 'MANAGER' has permission 'TASK_REASSIGN' & 'PROPOSAL_CREATE' (Pass)",
        "3. Read Tool Call: inspect_task_topology(task_id='104') -> In-degree: 2, Blocked by: T2, Assignee Load: 94%",
        "4. Simulation Tool: cpm_simulate_reassignment(candidate='Sarah L.') -> Slack improves from 0 to +1.5 weeks"
    ]
    t_y = ty1 + 28
    for tr in traces:
        draw.text((tx1 + 15, t_y), tr, fill="#cbd5e1", font=get_font(9))
        t_y += 18

    # Explanation text
    exp_text = [
        "Diagnosis: Task #104 is blocked because Vikram S. is currently saturated at 94% capacity across three tasks.",
        "Furthermore, Task #104 lies directly on the Critical Path (Zero Slack). Any further delay will cascade to Milestone 2.",
        "Remediation Recommendation: Reassign Task #104 to Sarah L., who currently operates at 42% workload."
    ]
    ey = ay1 + 140
    for el in exp_text:
        draw.text((ax1 + 18, ey), el, fill="#f8fafc", font=get_font(11))
        ey += 20

    # Diff Proposal Card (Safe Tool Calling Protocol)
    px1, py1, px2, py2 = ax1 + 18, ay1 + 215, ax2 - 18, ay1 + 340
    draw.rounded_rectangle([px1, py1, px2, py2], radius=6, fill="#1e293b", outline="#f59e0b", width=2)
    # Badge
    draw.rounded_rectangle([px1 + 12, py1 + 10, px1 + 220, py1 + 30], radius=4, fill="#0f172a")
    draw.text((px1 + 20, py1 + 14), "PROPOSAL DIFF #P-2026-04 (PENDING APPROVAL)", fill="#f59e0b", font=get_font(9, bold=True))

    # Diff content
    draw.text((px1 + 18, py1 + 42), "Entity: Task #104 (Kahn's CPM Simulator Engine)", fill="#f8fafc", font=get_font(11, bold=True))
    draw.text((px1 + 18, py1 + 65), "- Assignee: Vikram S. (Workload: 94% [OVERLOADED])", fill="#f87171", font=get_font(11, bold=True))
    draw.text((px1 + 18, py1 + 85), "+ Assignee: Sarah L.  (Workload: 42% [OPTIMAL CAPACITY])", fill="#34d399", font=get_font(11, bold=True))

    # Action buttons on Proposal
    draw.rounded_rectangle([px2 - 270, py1 + 55, px2 - 150, py1 + 95], radius=5, fill="#10b981")
    draw.text((px2 - 255, py1 + 68), "✔ Approve & Apply", fill="#ffffff", font=get_font(11, bold=True))

    draw.rounded_rectangle([px2 - 135, py1 + 55, px2 - 20, py1 + 95], radius=5, fill="#ef4444")
    draw.text((px2 - 118, py1 + 68), "✖ Reject Diff", fill="#ffffff", font=get_font(11, bold=True))

    # Chat Input Box at bottom
    ix1, iy1, ix2, iy2 = cx1 + 25, cy2 - 65, cx2 - 25, cy2 - 15
    draw.rounded_rectangle([ix1, iy1, ix2, iy2], radius=6, fill="#1e293b", outline="#3b82f6", width=1)
    draw.text((ix1 + 15, iy1 + 16), "Ask Copilot or issue swarm command (e.g., /simulate-cpm, /audit-mfa, /rag-search)...", fill="#64748b", font=get_font(11))
    draw.rounded_rectangle([ix2 - 90, iy1 + 8, ix2 - 10, iy2 - 8], radius=5, fill="#3b82f6")
    draw.text((ix2 - 75, iy1 + 16), "Send ✈", fill="#ffffff", font=get_font(11, bold=True))

    img.save(os.path.join(OUT_DIR, "copilot_war_room.png"))
    print("Saved copilot_war_room.png")

if __name__ == "__main__":
    generate_search_engine_output()
    generate_copilot_output()
    print("Both Search Engine and Copilot demo images successfully generated!")

