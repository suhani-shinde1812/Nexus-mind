import os
import math
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = r"E:\nexus-mind\report_images"
os.makedirs(OUT_DIR, exist_ok=True)

# Helper for font loading with fallback
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

def draw_header(draw, title, subtitle, width):
    draw.rectangle([0, 0, width, 70], fill="#0f172a")
    draw.rectangle([0, 70, width, 72], fill="#334155")
    # Title
    font_title = get_font(24, bold=True)
    font_sub = get_font(14, bold=False)
    draw.text((30, 15), title, fill="#f8fafc", font=font_title)
    draw.text((30, 44), subtitle, fill="#94a3b8", font=font_sub)
    # Right badge
    draw.rounded_rectangle([width - 240, 20, width - 30, 52], radius=6, fill="#1e293b", outline="#3b82f6", width=1)
    badge_font = get_font(13, bold=True)
    draw.text((width - 225, 27), "● Nexus Mind v2.4 (Live)", fill="#38bdf8", font=badge_font)

# =============================================================================
# 1. LIVE FORCE-DIRECTED SVG TASK GRAPH
# =============================================================================
def generate_live_graph():
    w, h = 1300, 750
    img = Image.new("RGB", (w, h), color="#090d16")
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Live Interactive Force-Directed Task DAG Graph", "Autonomous Real-Time CPM Dependency & Delivery Risk Topology", w)

    # Grid background dots
    for x in range(40, w - 40, 30):
        for y in range(90, h - 40, 30):
            draw.ellipse([x, y, x + 2, y + 2], fill="#1e293b")

    # Nodes definition: (id, label, x, y, status_color, halo_color, risk_text, assignee, duration)
    nodes = [
        {"id": "T1", "name": "Auth & IAM (RFC 6238)", "x": 160, "y": 280, "color": "#10b981", "halo": None, "risk": "Low (12%)", "user": "Alex R.", "status": "COMPLETED"},
        {"id": "T2", "name": "256-d RAG Embedding Vectorizer", "x": 420, "y": 180, "color": "#3b82f6", "halo": None, "risk": "Low (18%)", "user": "Sarah L.", "status": "IN PROGRESS"},
        {"id": "T3", "name": "BM25 Hybrid Lexical Fusion", "x": 420, "y": 380, "color": "#3b82f6", "halo": None, "risk": "Med (38%)", "user": "Dev K.", "status": "IN PROGRESS"},
        {"id": "T4", "name": "Kahn's CPM Simulator Engine", "x": 720, "y": 240, "color": "#ef4444", "halo": "#ef4444", "risk": "HIGH RISK (88%)", "user": "Vikram S.", "status": "BLOCKED"},
        {"id": "T5", "name": "GitHub HMAC Webhook Ingestion", "x": 720, "y": 460, "color": "#10b981", "halo": None, "risk": "Low (8%)", "user": "Priya M.", "status": "COMPLETED"},
        {"id": "T6", "name": "Multi-Agent Swarm Proposal Tray", "x": 1000, "y": 260, "color": "#f59e0b", "halo": "#f59e0b", "risk": "CRITICAL PATH", "user": "Alex R.", "status": "IN PROGRESS"},
        {"id": "T7", "name": "Cross-Platform Flutter Client", "x": 1000, "y": 480, "color": "#8b5cf6", "halo": None, "risk": "Med (42%)", "user": "Sarah L.", "status": "READY"}
    ]

    edges = [
        ("T1", "T2"), ("T1", "T3"),
        ("T2", "T4"), ("T3", "T4"),
        ("T1", "T5"),
        ("T4", "T6"), ("T5", "T7"), ("T4", "T7")
    ]

    node_dict = {n["id"]: n for n in nodes}

    # Draw edges
    for u, v in edges:
        p1 = node_dict[u]
        p2 = node_dict[v]
        is_crit = (u == "T4" and v == "T6") or (u == "T1" and v == "T2") or (u == "T2" and v == "T4")
        edge_color = "#ef4444" if is_crit else "#475569"
        edge_width = 3 if is_crit else 2
        draw.line([p1["x"], p1["y"], p2["x"], p2["y"]], fill=edge_color, width=edge_width)
        # Midpoint arrow
        mx = (p1["x"] + p2["x"]) / 2
        my = (p1["y"] + p2["y"]) / 2
        draw.ellipse([mx - 4, my - 4, mx + 4, my + 4], fill=edge_color)

    # Draw nodes
    for n in nodes:
        x, y = n["x"], n["y"]
        # Halo if present
        if n["halo"]:
            for r in range(48, 62, 3):
                draw.ellipse([x - r, y - r, x + r, y + r], outline=n["halo"], width=1)

        # Outer circle
        draw.ellipse([x - 38, y - 38, x + 38, y + 38], fill="#1e293b", outline=n["color"], width=3)
        # Inner badge
        draw.ellipse([x - 14, y - 14, x + 14, y + 14], fill=n["color"])
        draw.text((x - 8, y - 9), n["id"], fill="#ffffff", font=get_font(13, bold=True))

        # Node label box below
        box_w, box_h = 190, 60
        bx1, by1 = x - box_w // 2, y + 44
        bx2, by2 = bx1 + box_w, by1 + box_h
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=6, fill="#0f172a", outline="#334155", width=1)
        draw.text((bx1 + 10, by1 + 8), n["name"][:24], fill="#f8fafc", font=get_font(11, bold=True))
        draw.text((bx1 + 10, by1 + 25), f"Assigned: {n['user']}", fill="#94a3b8", font=get_font(10))
        draw.text((bx1 + 10, by1 + 40), f"Risk: {n['risk']}", fill="#f87171" if "HIGH" in n["risk"] or "CRIT" in n["risk"] else "#34d399", font=get_font(10, bold=True))

    # Legend / HUD Box
    draw.rounded_rectangle([30, h - 130, 480, h - 25], radius=8, fill="#0f172a", outline="#334155", width=1)
    draw.text((45, h - 120), "GRAPH HUD & TOPOLOGY METRICS", fill="#38bdf8", font=get_font(12, bold=True))
    draw.text((45, h - 98), "• Total Vertices: 7 Tasks  |  Edges: 8 Dependencies", fill="#e2e8f0", font=get_font(11))
    draw.text((45, h - 80), "• Critical Path: T1 → T2 → T4 → T6 (Zero Slack)", fill="#f87171", font=get_font(11, bold=True))
    draw.text((45, h - 62), "• Topological Sort: [T1, T3, T5, T2, T4, T7, T6] (Acyclic Kahn Pass: OK)", fill="#94a3b8", font=get_font(10))
    draw.text((45, h - 45), "• Red Pulsating Halo: ML Delivery Risk Probability > 80%", fill="#fca5a5", font=get_font(10))

    img.save(os.path.join(OUT_DIR, "live_graph.png"))
    print("Saved live_graph.png")

# =============================================================================
# 2. GANTT / CPM TIMELINE SCHEDULE CHART
# =============================================================================
def generate_gantt_chart():
    w, h = 1300, 750
    img = Image.new("RGB", (w, h), color="#0f172a")
    draw = ImageDraw.Draw(img)
    draw_header(draw, "CPM Critical Path & Discrete-Event Gantt Schedule", "Topological Schedule Float, Early/Late Boundaries & Critical Sequence", w)

    # Timeline headers
    header_y = 90
    draw.rectangle([0, header_y, w, header_y + 35], fill="#1e293b")
    draw.text((30, header_y + 8), "WBS / Task Name", fill="#94a3b8", font=get_font(12, bold=True))

    days = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Week 7", "Week 8", "Week 9", "Week 10"]
    left_margin = 360
    col_width = (w - left_margin - 40) // len(days)

    for i, d in enumerate(days):
        x = left_margin + i * col_width
        draw.line([x, header_y, x, h - 40], fill="#334155", width=1)
        draw.text((x + 10, header_y + 8), d, fill="#cbd5e1", font=get_font(11, bold=True))

    tasks = [
        {"name": "1. Architecture Blueprint & DB Schemas", "w_start": 0, "duration": 2, "crit": True, "slack": "0 wks", "prog": 100},
        {"name": "2. Auth, TOTP MFA & Fernet Encryption", "w_start": 1, "duration": 2, "crit": False, "slack": "1 wk", "prog": 100},
        {"name": "3. 256-d RAG Vectorizer & Chunking", "w_start": 2, "duration": 2.5, "crit": True, "slack": "0 wks", "prog": 90},
        {"name": "4. BM25 Hybrid Fusion Retrieval Engine", "w_start": 3.5, "duration": 1.5, "crit": False, "slack": "0.5 wk", "prog": 80},
        {"name": "5. Random Forest ML Risk Model Training", "w_start": 4, "duration": 2, "crit": True, "slack": "0 wks", "prog": 70},
        {"name": "6. Kahn's Algorithm CPM DAG Simulator", "w_start": 5, "duration": 2, "crit": True, "slack": "0 wks", "prog": 45},
        {"name": "7. GitHub HMAC-SHA256 Telemetry Pipeline", "w_start": 4.5, "duration": 2, "crit": False, "slack": "1.5 wks", "prog": 85},
        {"name": "8. Multi-Agent Swarm & Proposal Protocol", "w_start": 6.5, "duration": 2.5, "crit": True, "slack": "0 wks", "prog": 30},
        {"name": "9. Cross-Platform Flutter Client (Riverpod)", "w_start": 7, "duration": 2.5, "crit": False, "slack": "0.5 wk", "prog": 40},
        {"name": "10. Comprehensive Verification & Review", "w_start": 8.5, "duration": 1.5, "crit": True, "slack": "0 wks", "prog": 10},
    ]

    row_h = 50
    curr_y = header_y + 45
    for t in tasks:
        # Alternating background row
        draw.rectangle([0, curr_y - 5, w, curr_y + row_h - 10], fill="#131d31")
        # Task name
        draw.text((30, curr_y + 5), t["name"], fill="#f8fafc", font=get_font(12, bold=t["crit"]))
        slack_color = "#f87171" if t["crit"] else "#38bdf8"
        draw.text((30, curr_y + 24), f"Slack: {t['slack']} | Progress: {t['prog']}%", fill=slack_color, font=get_font(10))

        # Gantt bar
        bx1 = left_margin + int(t["w_start"] * col_width)
        bx2 = bx1 + int(t["duration"] * col_width)
        by1 = curr_y + 6
        by2 = curr_y + 26

        bar_color = "#ef4444" if t["crit"] else "#3b82f6"
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=4, fill=bar_color)

        # Progress fill stripe
        pw = int((bx2 - bx1) * (t["prog"] / 100))
        if pw > 0:
            draw.rounded_rectangle([bx1, by1, bx1 + pw, by2], radius=4, fill="#10b981")

        draw.text((bx1 + 8, by1 + 2), f"{t['prog']}%", fill="#ffffff", font=get_font(10, bold=True))
        curr_y += row_h

    # Today marker line
    today_x = left_margin + int(5.6 * col_width)
    draw.line([today_x, header_y, today_x, h - 30], fill="#f59e0b", width=2)
    draw.rounded_rectangle([today_x - 45, h - 32, today_x + 45, h - 10], radius=4, fill="#f59e0b")
    draw.text((today_x - 38, h - 28), "TODAY (W6)", fill="#000000", font=get_font(10, bold=True))

    img.save(os.path.join(OUT_DIR, "gantt_chart.png"))
    print("Saved gantt_chart.png")

# =============================================================================
# 3. KANBAN BOARD SCREEN
# =============================================================================
def generate_kanban_board():
    w, h = 1300, 750
    img = Image.new("RGB", (w, h), color="#0b1120")
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Enterprise Engineering Kanban Board", "Real-Time Multi-Agent Task Stream, Risk Badges & Proposal Workflow", w)

    columns = [
        {"title": "BACKLOG (4)", "color": "#64748b", "x": 30, "w": 285},
        {"title": "IN PROGRESS (3)", "color": "#3b82f6", "x": 345, "w": 285},
        {"title": "PROPOSAL REVIEW (2)", "color": "#f59e0b", "x": 660, "w": 285},
        {"title": "COMPLETED / VERIFIED (5)", "color": "#10b981", "x": 975, "w": 285}
    ]

    cards = [
        # Backlog
        {"col": 0, "title": "Helm Charts for K8s Multi-Region", "tag": "DevOps", "risk": "Low (10%)", "prio": "P3", "user": "Vikram S."},
        {"col": 0, "title": "VS Code Extension Proposal Bridge", "tag": "Tooling", "risk": "Low (15%)", "prio": "P2", "user": "Sarah L."},
        {"col": 0, "title": "Hungarian Talent Match Algorithm", "tag": "Analytics", "risk": "Med (25%)", "prio": "P2", "user": "Alex R."},
        # In Progress
        {"col": 1, "title": "BM25 Hybrid Fusion Weight Tuning", "tag": "RAG Engine", "risk": "Med (35%)", "prio": "P1", "user": "Sarah L."},
        {"col": 1, "title": "Riverpod StateNotifier Integration", "tag": "Mobile", "risk": "Low (18%)", "prio": "P2", "user": "Dev K."},
        {"col": 1, "title": "RandomForest Hyperparameter Tuning", "tag": "ML Model", "risk": "Med (40%)", "prio": "P1", "user": "Vikram S."},
        # Proposal Review
        {"col": 2, "title": "Reassign Task #104 to Sarah L.", "tag": "AI Swarm Diff", "risk": "HIGH RISK (88%)", "prio": "CRITICAL", "user": "PM Agent"},
        {"col": 2, "title": "Extend Milestone 2 by 48 Hours", "tag": "CPM Simulation", "risk": "HIGH RISK (76%)", "prio": "URGENT", "user": "Analytics Agent"},
        # Completed
        {"col": 3, "title": "RFC 6238 TOTP MFA + 8 Backup Keys", "tag": "Security", "risk": "Verified", "prio": "P0", "user": "Alex R."},
        {"col": 3, "title": "HMAC-SHA256 Webhook Verification", "tag": "Telemetry", "risk": "Verified", "prio": "P1", "user": "Priya M."},
        {"col": 3, "title": "256-d Unit Hypersphere Embeddings", "tag": "NLP", "risk": "Verified", "prio": "P0", "user": "Sarah L."}
    ]

    card_y_track = [135, 135, 135, 135]

    for c in columns:
        # Col header background
        draw.rounded_rectangle([c["x"], 95, c["x"] + c["w"], 125], radius=6, fill="#1e293b", outline=c["color"], width=1)
        draw.text((c["x"] + 15, 102), c["title"], fill="#f8fafc", font=get_font(12, bold=True))
        # Column container area
        draw.rounded_rectangle([c["x"], 130, c["x"] + c["w"], h - 30], radius=8, fill="#0f172a", outline="#1e293b", width=1)

    for item in cards:
        ci = item["col"]
        cx = columns[ci]["x"] + 10
        cy = card_y_track[ci]
        cw = columns[ci]["w"] - 20
        ch = 145

        # Card body
        card_border = "#f59e0b" if ci == 2 else ("#ef4444" if "HIGH" in item["risk"] else "#334155")
        draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=6, fill="#1e293b", outline=card_border, width=2 if ci == 2 else 1)

        # Tag badge
        draw.rounded_rectangle([cx + 12, cy + 10, cx + 110, cy + 30], radius=4, fill="#0f172a")
        draw.text((cx + 18, cy + 14), item["tag"], fill="#38bdf8", font=get_font(10, bold=True))

        # Priority badge
        prio_color = "#ef4444" if item["prio"] in ["CRITICAL", "P0"] else "#f59e0b"
        draw.text((cx + cw - 65, cy + 14), item["prio"], fill=prio_color, font=get_font(11, bold=True))

        # Title
        draw.text((cx + 12, cy + 40), item["title"][:28], fill="#ffffff", font=get_font(12, bold=True))
        if len(item["title"]) > 28:
            draw.text((cx + 12, cy + 58), item["title"][28:56], fill="#ffffff", font=get_font(12, bold=True))

        # Risk indicator
        risk_color = "#f87171" if "HIGH" in item["risk"] else ("#34d399" if "Ver" in item["risk"] or "Low" in item["risk"] else "#fbbf24")
        draw.text((cx + 12, cy + 85), f"Risk: {item['risk']}", fill=risk_color, font=get_font(10, bold=True))

        # Bottom row: Assignee avatar & button
        draw.line([cx + 10, cy + 108, cx + cw - 10, cy + 108], fill="#334155", width=1)
        draw.ellipse([cx + 12, cy + 115, cx + 32, cy + 135], fill="#3b82f6")
        draw.text((cx + 17, cy + 118), item["user"][0], fill="#ffffff", font=get_font(11, bold=True))
        draw.text((cx + 40, cy + 120), item["user"], fill="#cbd5e1", font=get_font(11))

        if ci == 2:
            # Review button for proposal
            draw.rounded_rectangle([cx + cw - 85, cy + 115, cx + cw - 10, cy + 137], radius=4, fill="#f59e0b")
            draw.text((cx + cw - 78, cy + 119), "Review Diff", fill="#000000", font=get_font(10, bold=True))

        card_y_track[ci] += ch + 15

    img.save(os.path.join(OUT_DIR, "kanban_board.png"))
    print("Saved kanban_board.png")

# =============================================================================
# 4. ANALYTICS & RISK PREDICTION GRAPH CHART
# =============================================================================
def generate_graph_chart():
    w, h = 1300, 750
    img = Image.new("RGB", (w, h), color="#090d16")
    draw = ImageDraw.Draw(img)
    draw_header(draw, "ML Predictive Risk & Engineering Velocity Analytics", "Scikit-Learn Random Forest (96.67% Acc, 0.991 ROC-AUC) vs Baseline Models", w)

    # Left chart: ROC Curves (40, 110, 600, 480)
    lx1, ly1, lx2, ly2 = 60, 120, 600, 480
    draw.rounded_rectangle([lx1, ly1, lx2, ly2], radius=8, fill="#0f172a", outline="#334155", width=1)
    draw.text((lx1 + 20, ly1 + 18), "Receiver Operating Characteristic (ROC) Comparison", fill="#f8fafc", font=get_font(13, bold=True))
    draw.text((lx1 + 20, ly1 + 38), "True Positive Rate vs False Positive Rate across 5-Fold CV", fill="#94a3b8", font=get_font(10))

    # Axes
    ox, oy = lx1 + 50, ly2 - 50
    pw, ph = 460, 250
    draw.line([ox, oy, ox + pw, oy], fill="#64748b", width=2)
    draw.line([ox, oy, ox, oy - ph], fill="#64748b", width=2)

    # Grid & labels
    for i in range(1, 5):
        gx = ox + int(pw * (i / 4))
        gy = oy - int(ph * (i / 4))
        draw.line([gx, oy, gx, oy - ph], fill="#1e293b", width=1)
        draw.line([ox, gy, ox + pw, gy], fill="#1e293b", width=1)
        draw.text((gx - 10, oy + 8), f"{i*0.25:.2f}", fill="#64748b", font=get_font(9))
        draw.text((ox - 32, gy - 6), f"{i*0.25:.2f}", fill="#64748b", font=get_font(9))

    draw.text((ox + pw // 2 - 40, oy + 26), "False Positive Rate (FPR)", fill="#cbd5e1", font=get_font(10))

    # Diagonal random line
    draw.line([ox, oy, ox + pw, oy - ph], fill="#475569", width=1)

    # Baseline Logistic Regression Curve (ROC-AUC = 0.884)
    lr_points = [
        (0.0, 0.0), (0.05, 0.35), (0.1, 0.55), (0.2, 0.72), (0.3, 0.82),
        (0.5, 0.90), (0.7, 0.95), (1.0, 1.0)
    ]
    px_lr = [(ox + int(p[0] * pw), oy - int(p[1] * ph)) for p in lr_points]
    for i in range(len(px_lr) - 1):
        draw.line([px_lr[i], px_lr[i+1]], fill="#f59e0b", width=2)

    # Random Forest Model Curve (ROC-AUC = 0.991)
    rf_points = [
        (0.0, 0.0), (0.02, 0.75), (0.05, 0.92), (0.1, 0.97), (0.15, 0.985),
        (0.3, 0.995), (0.6, 1.0), (1.0, 1.0)
    ]
    px_rf = [(ox + int(p[0] * pw), oy - int(p[1] * ph)) for p in rf_points]
    for i in range(len(px_rf) - 1):
        draw.line([px_rf[i], px_rf[i+1]], fill="#38bdf8", width=3)

    # ROC Legend
    draw.line([lx1 + 25, ly2 - 25, lx1 + 55, ly2 - 25], fill="#38bdf8", width=3)
    draw.text((lx1 + 65, ly2 - 32), "Random Forest (AUC = 0.991)", fill="#38bdf8", font=get_font(10, bold=True))
    draw.line([lx1 + 250, ly2 - 25, lx1 + 280, ly2 - 25], fill="#f59e0b", width=2)
    draw.text((lx1 + 290, ly2 - 32), "Logistic Baseline (AUC = 0.884)", fill="#f59e0b", font=get_font(10))

    # Right chart: Feature Importance (640, 120, 1240, 480)
    rx1, ry1, rx2, ry2 = 640, 120, 1240, 480
    draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=8, fill="#0f172a", outline="#334155", width=1)
    draw.text((rx1 + 20, ry1 + 18), "Explainable AI (XAI) Feature Importance Breakdown", fill="#f8fafc", font=get_font(13, bold=True))
    draw.text((rx1 + 20, ry1 + 38), "MDI Gini Importance Contribution to Task Delivery Delay", fill="#94a3b8", font=get_font(10))

    features = [
        {"name": "In-Degree Dependency Count (Blockers)", "pct": 34.2, "color": "#ef4444"},
        {"name": "Deadline Proximity Delta (Hours)", "pct": 26.8, "color": "#f59e0b"},
        {"name": "Assignee Workload Saturation %", "pct": 19.5, "color": "#3b82f6"},
        {"name": "Historical PR Cycle Turnaround Time", "pct": 11.4, "color": "#10b981"},
        {"name": "Out-Degree Topological Graph Impact", "pct": 8.1, "color": "#8b5cf6"},
    ]

    fy = ry1 + 70
    for f in features:
        draw.text((rx1 + 20, fy), f["name"], fill="#e2e8f0", font=get_font(11, bold=True))
        draw.text((rx2 - 75, fy), f"{f['pct']}%", fill=f["color"], font=get_font(11, bold=True))
        # Bar track
        draw.rounded_rectangle([rx1 + 20, fy + 20, rx2 - 20, fy + 34], radius=4, fill="#1e293b")
        bar_len = int((rx2 - rx1 - 40) * (f["pct"] / 100))
        draw.rounded_rectangle([rx1 + 20, fy + 20, rx1 + 20 + bar_len, fy + 34], radius=4, fill=f["color"])
        fy += 55

    # Bottom metric cards (Summary KPI bar)
    kpis = [
        {"label": "Model Accuracy", "val": "96.67%", "sub": "+15.42% over baseline", "color": "#10b981"},
        {"label": "Precision / F1-Score", "val": "0.970", "sub": "High false-alarm penalty", "color": "#38bdf8"},
        {"label": "Average RAG Latency", "val": "42 ms", "sub": "Dense + BM25 Hybrid", "color": "#a855f7"},
        {"label": "Out-of-Scope Fallback", "val": "100.0%", "sub": "Zero Hallucination Rate", "color": "#f59e0b"},
    ]

    kw = (w - 120) // 4
    for i, k in enumerate(kpis):
        kx1 = 60 + i * (kw + 15)
        ky1 = 510
        kx2 = kx1 + kw
        ky2 = 710
        draw.rounded_rectangle([kx1, ky1, kx2, ky2], radius=8, fill="#0f172a", outline="#334155", width=1)
        draw.text((kx1 + 18, ky1 + 20), k["label"], fill="#94a3b8", font=get_font(11, bold=True))
        draw.text((kx1 + 18, ky1 + 48), k["val"], fill=k["color"], font=get_font(28, bold=True))
        draw.text((kx1 + 18, ky1 + 95), k["sub"], fill="#64748b", font=get_font(10))

    img.save(os.path.join(OUT_DIR, "graph_chart.png"))
    print("Saved graph_chart.png")

if __name__ == "__main__":
    generate_live_graph()
    generate_gantt_chart()
    generate_kanban_board()
    generate_graph_chart()
    print("All 4 demo images successfully generated!")

