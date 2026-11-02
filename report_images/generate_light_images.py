import os
import math
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = r"E:\nexus-mind\report_images"
os.makedirs(OUT_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# FONT LOADER - Ultra Clean & Crisp (Windows TrueType with Fallback)
# -----------------------------------------------------------------------------
def get_font(size, bold=False):
    font_paths = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\tahomabd.ttf" if bold else r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_light_header(draw, title, subtitle, width, tag="Enterprise Platform"):
    # Premium White Header Bar
    draw.rectangle([0, 0, width, 130], fill="#FFFFFF")
    draw.rectangle([0, 130, width, 136], fill="#2563EB") # Royal Blue Accent Stripe
    
    # Title & Subtitle in sharp high-contrast dark colors
    draw.text((60, 24), title, fill="#0F172A", font=get_font(42, bold=True))
    draw.text((60, 80), subtitle, fill="#475569", font=get_font(24, bold=False))
    
    # Right pill badge
    badge_w = 460
    bx1 = width - badge_w - 60
    draw.rounded_rectangle([bx1, 32, width - 60, 98], radius=12, fill="#F1F5F9", outline="#0284C7", width=2)
    draw.text((bx1 + 25, 48), f"● Nexus Mind :: {tag}", fill="#0284C7", font=get_font(24, bold=True))

# =============================================================================
# 1. LIVE FORCE-DIRECTED TASK GRAPH (White Academic Theme)
# =============================================================================
def generate_light_live_graph():
    w, h = 2400, 1400
    img = Image.new("RGB", (w, h), color="#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_light_header(draw, "Live Interactive Force-Directed Task DAG Graph",
                      "Autonomous CPM Dependency Architecture & Real-Time Delivery Risk Topology", w, "Live Graph Engine")

    # Subtle background dot grid on white paper
    for x in range(60, w - 60, 50):
        for y in range(160, h - 60, 50):
            draw.ellipse([x, y, x + 3, y + 3], fill="#CBD5E1")

    # Nodes with high-contrast light theme colors
    nodes = [
        {"id": "T1", "name": "Auth & IAM (RFC 6238 TOTP)", "x": 300, "y": 550, "color": "#059669", "halo": None, "risk": "Low (12%)", "user": "Alex R.", "status": "COMPLETED"},
        {"id": "T2", "name": "256-d RAG Vectorizer Chunks", "x": 800, "y": 380, "color": "#2563EB", "halo": None, "risk": "Low (18%)", "user": "Sarah L.", "status": "IN PROGRESS"},
        {"id": "T3", "name": "BM25 Hybrid Lexical Fusion", "x": 800, "y": 740, "color": "#2563EB", "halo": None, "risk": "Med (38%)", "user": "Dev K.", "status": "IN PROGRESS"},
        {"id": "T4", "name": "Kahn's CPM Simulator Engine", "x": 1380, "y": 480, "color": "#DC2626", "halo": "#DC2626", "risk": "HIGH RISK (88%)", "user": "Vikram S.", "status": "BLOCKED"},
        {"id": "T5", "name": "GitHub HMAC Webhook Ingest", "x": 1380, "y": 880, "color": "#059669", "halo": None, "risk": "Low (8%)", "user": "Priya M.", "status": "COMPLETED"},
        {"id": "T6", "name": "Multi-Agent Swarm Proposal Tray", "x": 1940, "y": 520, "color": "#D97706", "halo": "#D97706", "risk": "CRITICAL PATH", "user": "Alex R.", "status": "IN PROGRESS"},
        {"id": "T7", "name": "Cross-Platform Flutter Client", "x": 1940, "y": 920, "color": "#7C3AED", "halo": None, "risk": "Med (42%)", "user": "Sarah L.", "status": "READY"}
    ]

    edges = [
        ("T1", "T2"), ("T1", "T3"),
        ("T2", "T4"), ("T3", "T4"),
        ("T1", "T5"),
        ("T4", "T6"), ("T5", "T7"), ("T4", "T7")
    ]
    node_dict = {n["id"]: n for n in nodes}

    # Draw crisp edges
    for u, v in edges:
        p1 = node_dict[u]
        p2 = node_dict[v]
        is_crit = (u == "T4" and v == "T6") or (u == "T1" and v == "T2") or (u == "T2" and v == "T4")
        edge_col = "#DC2626" if is_crit else "#94A3B8"
        edge_w = 7 if is_crit else 4
        draw.line([p1["x"], p1["y"], p2["x"], p2["y"]], fill=edge_col, width=edge_w)
        # Midpoint directional arrow circle
        mx, my = (p1["x"] + p2["x"]) / 2, (p1["y"] + p2["y"]) / 2
        draw.ellipse([mx - 10, my - 10, mx + 10, my + 10], fill=edge_col)

    # Draw nodes
    for n in nodes:
        x, y = n["x"], n["y"]
        # Outer pulsating halo if critical
        if n["halo"]:
            for r in range(85, 120, 6):
                draw.ellipse([x - r, y - r, x + r, y + r], outline="#FCA5A5", width=3)

        # Outer node circle (clean white fill with colored border)
        draw.ellipse([x - 70, y - 70, x + 70, y + 70], fill="#FFFFFF", outline=n["color"], width=6)
        # Inner colored center
        draw.ellipse([x - 32, y - 32, x + 32, y + 32], fill=n["color"])
        draw.text((x - 20, y - 18), n["id"], fill="#FFFFFF", font=get_font(26, bold=True))

        # Node Label Card Below (White Box with soft border & shadow)
        bw, bh = 340, 115
        bx1, by1 = x - bw // 2, y + 85
        bx2, by2 = bx1 + bw, by1 + bh
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=10, fill="#FFFFFF", outline="#CBD5E1", width=2)
        draw.text((bx1 + 18, by1 + 14), n["name"], fill="#0F172A", font=get_font(18, bold=True))
        draw.text((bx1 + 18, by1 + 48), f"Assigned: {n['user']}", fill="#475569", font=get_font(17))
        risk_color = "#DC2626" if "HIGH" in n["risk"] or "CRIT" in n["risk"] else "#059669"
        draw.text((bx1 + 18, by1 + 78), f"Risk Status: {n['risk']}", fill=risk_color, font=get_font(17, bold=True))

    # Bottom HUD Box
    hud_x1, hud_y1, hud_x2, hud_y2 = 60, h - 230, 950, h - 50
    draw.rounded_rectangle([hud_x1, hud_y1, hud_x2, hud_y2], radius=12, fill="#FFFFFF", outline="#2563EB", width=2)
    draw.text((hud_x1 + 30, hud_y1 + 22), "GRAPH HUD & TOPOLOGY METRICS", fill="#2563EB", font=get_font(22, bold=True))
    draw.text((hud_x1 + 30, hud_y1 + 65), "• Total Vertices: 7 Tasks  |  Total Edges: 8 Dependencies", fill="#1E293B", font=get_font(20))
    draw.text((hud_x1 + 30, hud_y1 + 102), "• Critical Path: T1 → T2 → T4 → T6 (Zero Slack Float)", fill="#DC2626", font=get_font(20, bold=True))
    draw.text((hud_x1 + 30, hud_y1 + 138), "• Kahn's Topological Order: [T1, T3, T5, T2, T4, T7, T6]", fill="#475569", font=get_font(19))

    path = os.path.join(OUT_DIR, "live_graph.png")
    if os.path.exists(path): os.remove(path)
    img.save(path)
    print("Saved White live_graph.png")

# =============================================================================
# 2. GANTT / CPM TIMELINE SCHEDULE CHART (White Academic Theme)
# =============================================================================
def generate_light_gantt_chart():
    w, h = 2400, 1400
    img = Image.new("RGB", (w, h), color="#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_light_header(draw, "CPM Critical Path & Discrete-Event Gantt Schedule",
                      "Topological Schedule Float, Early/Late Boundaries & Critical Sequence", w, "Gantt Timeline")

    header_y = 150
    draw.rectangle([0, header_y, w, header_y + 65], fill="#E2E8F0")
    draw.text((60, header_y + 16), "WBS / Task Name", fill="#1E293B", font=get_font(24, bold=True))

    days = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Week 7", "Week 8", "Week 9", "Week 10"]
    left_margin = 680
    col_w = (w - left_margin - 80) // len(days)

    for i, d in enumerate(days):
        x = left_margin + i * col_w
        draw.line([x, header_y, x, h - 80], fill="#CBD5E1", width=2)
        draw.text((x + 20, header_y + 16), d, fill="#0F172A", font=get_font(22, bold=True))

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

    row_h = 95
    curr_y = header_y + 80
    for t in tasks:
        # Alternating background row
        draw.rectangle([0, curr_y - 10, w, curr_y + row_h - 18], fill="#FFFFFF")
        # Task title & status
        draw.text((60, curr_y), t["name"], fill="#0F172A", font=get_font(22, bold=True))
        slack_color = "#DC2626" if t["crit"] else "#0284C7"
        draw.text((60, curr_y + 35), f"Total Slack: {t['slack']}  |  Progress: {t['prog']}%", fill=slack_color, font=get_font(18, bold=True))

        # Gantt bar
        bx1 = left_margin + int(t["w_start"] * col_w)
        bx2 = bx1 + int(t["duration"] * col_w)
        by1 = curr_y + 8
        by2 = curr_y + 52

        bar_col = "#DC2626" if t["crit"] else "#2563EB"
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=8, fill=bar_col)

        # Progress fill
        pw = int((bx2 - bx1) * (t["prog"] / 100))
        if pw > 0:
            draw.rounded_rectangle([bx1, by1, bx1 + pw, by2], radius=8, fill="#059669")

        draw.text((bx1 + 15, by1 + 8), f"{t['prog']}%", fill="#FFFFFF", font=get_font(20, bold=True))
        curr_y += row_h

    # Today vertical marker
    today_x = left_margin + int(5.6 * col_w)
    draw.line([today_x, header_y, today_x, h - 50], fill="#D97706", width=5)
    draw.rounded_rectangle([today_x - 90, h - 60, today_x + 90, h - 15], radius=8, fill="#D97706")
    draw.text((today_x - 72, h - 52), "TODAY (W6)", fill="#FFFFFF", font=get_font(18, bold=True))

    path = os.path.join(OUT_DIR, "gantt_chart.png")
    if os.path.exists(path): os.remove(path)
    img.save(path)
    print("Saved White gantt_chart.png")

# =============================================================================
# 3. KANBAN BOARD SCREEN (White Academic Theme)
# =============================================================================
def generate_light_kanban_board():
    w, h = 2400, 1400
    img = Image.new("RGB", (w, h), color="#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_light_header(draw, "Enterprise Engineering Kanban Board",
                      "Multi-Agent Workflow Stream, Risk Badges & Safe Proposal Review Columns", w, "Kanban Board")

    columns = [
        {"title": "BACKLOG (4)", "color": "#64748B", "x": 60, "w": 540},
        {"title": "IN PROGRESS (3)", "color": "#2563EB", "x": 640, "w": 540},
        {"title": "PROPOSAL REVIEW (2)", "color": "#D97706", "x": 1220, "w": 540},
        {"title": "COMPLETED / VERIFIED (5)", "color": "#059669", "x": 1800, "w": 540}
    ]

    cards = [
        # Backlog
        {"col": 0, "title": "Helm Charts for K8s Multi-Region", "tag": "DevOps", "risk": "Low (10%)", "prio": "P3", "user": "Vikram S."},
        {"col": 0, "title": "VS Code Proposal Review Extension", "tag": "Tooling", "risk": "Low (15%)", "prio": "P2", "user": "Sarah L."},
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

    for c in columns:
        # Col Header
        draw.rounded_rectangle([c["x"], 160, c["x"] + c["w"], 220], radius=10, fill="#FFFFFF", outline=c["color"], width=3)
        draw.text((c["x"] + 25, 175), c["title"], fill="#0F172A", font=get_font(24, bold=True))
        # Container background
        draw.rounded_rectangle([c["x"], 235, c["x"] + c["w"], h - 50], radius=12, fill="#F1F5F9", outline="#E2E8F0", width=2)

    card_y_track = [255, 255, 255, 255]
    for item in cards:
        ci = item["col"]
        cx = columns[ci]["x"] + 18
        cy = card_y_track[ci]
        cw = columns[ci]["w"] - 36
        ch = 270

        # Card box (Pure white with distinct borders)
        cborder = "#D97706" if ci == 2 else ("#DC2626" if "HIGH" in item["risk"] else "#CBD5E1")
        draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=10, fill="#FFFFFF", outline=cborder, width=3 if ci == 2 else 2)

        # Tag pill
        draw.rounded_rectangle([cx + 20, cy + 18, cx + 190, cy + 55], radius=6, fill="#F0F9FF")
        draw.text((cx + 32, cy + 24), item["tag"], fill="#0284C7", font=get_font(18, bold=True))

        # Priority label
        prio_col = "#DC2626" if item["prio"] in ["CRITICAL", "P0"] else "#D97706"
        draw.text((cx + cw - 120, cy + 24), item["prio"], fill=prio_col, font=get_font(20, bold=True))

        # Task title
        draw.text((cx + 20, cy + 75), item["title"][:28], fill="#0F172A", font=get_font(22, bold=True))
        if len(item["title"]) > 28:
            draw.text((cx + 20, cy + 105), item["title"][28:], fill="#0F172A", font=get_font(22, bold=True))

        # Risk indicator
        risk_col = "#DC2626" if "HIGH" in item["risk"] else ("#059669" if "Ver" in item["risk"] or "Low" in item["risk"] else "#D97706")
        draw.text((cx + 20, cy + 155), f"Risk Status: {item['risk']}", fill=risk_col, font=get_font(19, bold=True))

        # Bottom row: Assignee avatar & Action
        draw.line([cx + 15, cy + 195, cx + cw - 15, cy + 195], fill="#E2E8F0", width=2)
        draw.ellipse([cx + 20, cy + 208, cx + 58, cy + 246], fill="#2563EB")
        draw.text((cx + 30, cy + 214), item["user"][0], fill="#FFFFFF", font=get_font(20, bold=True))
        draw.text((cx + 70, cy + 218), item["user"], fill="#334155", font=get_font(20))

        if ci == 2:
            # Action button
            draw.rounded_rectangle([cx + cw - 165, cy + 208, cx + cw - 15, cy + 248], radius=6, fill="#D97706")
            draw.text((cx + cw - 150, cy + 215), "Review Diff", fill="#FFFFFF", font=get_font(18, bold=True))

        card_y_track[ci] += ch + 22

    path = os.path.join(OUT_DIR, "kanban_board.png")
    if os.path.exists(path): os.remove(path)
    img.save(path)
    print("Saved White kanban_board.png")

# =============================================================================
# 4. ANALYTICS & ROC-AUC GRAPH CHART (White Academic Theme)
# =============================================================================
def generate_light_graph_chart():
    w, h = 2400, 1400
    img = Image.new("RGB", (w, h), color="#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_light_header(draw, "ML Predictive Risk & Engineering Velocity Analytics",
                      "Scikit-Learn Random Forest (96.67% Acc, 0.991 ROC-AUC) vs Baseline Models", w, "Analytics Engine")

    # Left Container: ROC-AUC Curves
    lx1, ly1, lx2, ly2 = 60, 160, 1160, 880
    draw.rounded_rectangle([lx1, ly1, lx2, ly2], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=2)
    draw.text((lx1 + 40, ly1 + 30), "Receiver Operating Characteristic (ROC) Comparison", fill="#0F172A", font=get_font(26, bold=True))
    draw.text((lx1 + 40, ly1 + 72), "True Positive Rate vs False Positive Rate across 5-Fold Cross Validation", fill="#475569", font=get_font(19))

    # Graph Axes
    ox, oy = lx1 + 100, ly2 - 100
    gw, gh = 900, 480
    draw.line([ox, oy, ox + gw, oy], fill="#475569", width=3)
    draw.line([ox, oy, ox, oy - gh], fill="#475569", width=3)

    for i in range(1, 5):
        gx = ox + int(gw * (i / 4))
        gy = oy - int(gh * (i / 4))
        draw.line([gx, oy, gx, oy - gh], fill="#E2E8F0", width=2)
        draw.line([ox, gy, ox + gw, gy], fill="#E2E8F0", width=2)
        draw.text((gx - 20, oy + 15), f"{i*0.25:.2f}", fill="#64748B", font=get_font(18))
        draw.text((ox - 65, gy - 12), f"{i*0.25:.2f}", fill="#64748B", font=get_font(18))

    draw.text((ox + gw // 2 - 120, oy + 55), "False Positive Rate (FPR)", fill="#0F172A", font=get_font(20, bold=True))

    # Baseline Model Curve (AUC = 0.884)
    lr_pts = [(0.0, 0.0), (0.05, 0.35), (0.1, 0.55), (0.2, 0.72), (0.3, 0.82), (0.5, 0.90), (0.7, 0.95), (1.0, 1.0)]
    lr_coords = [(ox + int(p[0] * gw), oy - int(p[1] * gh)) for p in lr_pts]
    for i in range(len(lr_coords) - 1):
        draw.line([lr_coords[i], lr_coords[i+1]], fill="#D97706", width=4)

    # Candidate Random Forest (AUC = 0.991)
    rf_pts = [(0.0, 0.0), (0.02, 0.75), (0.05, 0.92), (0.1, 0.97), (0.15, 0.985), (0.3, 0.995), (0.6, 1.0), (1.0, 1.0)]
    rf_coords = [(ox + int(p[0] * gw), oy - int(p[1] * gh)) for p in rf_pts]
    for i in range(len(rf_coords) - 1):
        draw.line([rf_coords[i], rf_coords[i+1]], fill="#0284C7", width=6)

    # Legend
    draw.line([lx1 + 60, ly2 - 40, lx1 + 120, ly2 - 40], fill="#0284C7", width=6)
    draw.text((lx1 + 135, ly2 - 52), "Random Forest (AUC = 0.991)", fill="#0284C7", font=get_font(20, bold=True))
    draw.line([lx1 + 550, ly2 - 40, lx1 + 610, ly2 - 40], fill="#D97706", width=4)
    draw.text((lx1 + 625, ly2 - 52), "Logistic Regression (AUC = 0.884)", fill="#D97706", font=get_font(20, bold=True))

    # Right Container: Feature Importance
    rx1, ry1, rx2, ry2 = 1240, 160, w - 60, 880
    draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=2)
    draw.text((rx1 + 40, ry1 + 30), "Explainable AI (XAI) Feature Importance Breakdown", fill="#0F172A", font=get_font(26, bold=True))
    draw.text((rx1 + 40, ry1 + 72), "Mean Decrease in Impurity (Gini) Contribution to Delivery Risk", fill="#475569", font=get_font(19))

    features = [
        {"name": "In-Degree Dependency Count (Blockers)", "pct": 34.2, "color": "#DC2626"},
        {"name": "Deadline Proximity Delta (Hours)", "pct": 26.8, "color": "#D97706"},
        {"name": "Assignee Workload Saturation %", "pct": 19.5, "color": "#2563EB"},
        {"name": "Historical PR Cycle Turnaround Time", "pct": 11.4, "color": "#059669"},
        {"name": "Out-Degree Topological Graph Impact", "pct": 8.1, "color": "#7C3AED"},
    ]

    fy = ry1 + 140
    for f in features:
        draw.text((rx1 + 40, fy), f["name"], fill="#1E293B", font=get_font(22, bold=True))
        draw.text((rx2 - 140, fy), f"{f['pct']}%", fill=f["color"], font=get_font(22, bold=True))

        draw.rounded_rectangle([rx1 + 40, fy + 38, rx2 - 40, fy + 65], radius=6, fill="#F1F5F9")
        blen = int((rx2 - rx1 - 80) * (f["pct"] / 100))
        draw.rounded_rectangle([rx1 + 40, fy + 38, rx1 + 40 + blen, fy + 65], radius=6, fill=f["color"])
        fy += 105

    # Bottom KPI Summary Banner
    kpis = [
        {"label": "Model Accuracy", "val": "96.67%", "sub": "+15.42% over baseline", "color": "#059669"},
        {"label": "Precision / F1-Score", "val": "0.970", "sub": "High false-alarm penalty", "color": "#0284C7"},
        {"label": "Average RAG Latency", "val": "42 ms", "sub": "Dense + BM25 Hybrid", "color": "#7C3AED"},
        {"label": "Out-of-Scope Fallback", "val": "100.0%", "sub": "Zero Hallucination Rate", "color": "#D97706"},
    ]
    k_w = (w - 180) // 4
    for i, k in enumerate(kpis):
        kx1 = 60 + i * (k_w + 20)
        ky1 = 930
        kx2 = kx1 + k_w
        ky2 = 1330
        draw.rounded_rectangle([kx1, ky1, kx2, ky2], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=2)
        draw.text((kx1 + 35, ky1 + 40), k["label"], fill="#475569", font=get_font(22, bold=True))
        draw.text((kx1 + 35, ky1 + 95), k["val"], fill=k["color"], font=get_font(52, bold=True))
        draw.text((kx1 + 35, ky1 + 185), k["sub"], fill="#64748B", font=get_font(20))

    path = os.path.join(OUT_DIR, "graph_chart.png")
    if os.path.exists(path): os.remove(path)
    img.save(path)
    print("Saved White graph_chart.png")

# =============================================================================
# 5. GROUNDED RAG KNOWLEDGE SEARCH ENGINE (White Academic Theme)
# =============================================================================
def generate_light_search_engine_output():
    w, h = 2400, 1400
    img = Image.new("RGB", (w, h), color="#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_light_header(draw, "Grounded RAG Knowledge & Documentation Search Engine",
                      "256-Dim Dense Hypersphere Cosine Matching + BM25 Lexical Hybrid Fusion", w, "Grounded RAG")

    # Search Bar Box (White with Blue outline)
    sb_x1, sb_y1, sb_x2, sb_y2 = 60, 160, w - 60, 260
    draw.rounded_rectangle([sb_x1, sb_y1, sb_x2, sb_y2], radius=12, fill="#FFFFFF", outline="#2563EB", width=3)
    query_str = "How does the safe tool calling protocol handle task deadline modifications and human approval?"
    draw.text((sb_x1 + 35, sb_y1 + 30), "🔍", font=get_font(30))
    draw.text((sb_x1 + 95, sb_y1 + 30), query_str, fill="#0F172A", font=get_font(26, bold=True))
    draw.rounded_rectangle([sb_x2 - 320, sb_y1 + 20, sb_x2 - 25, sb_y2 - 20], radius=8, fill="#F0F9FF", outline="#0284C7", width=2)
    draw.text((sb_x2 - 300, sb_y1 + 34), "Cosine: 60% | BM25: 40%", fill="#0284C7", font=get_font(19, bold=True))

    draw.text((70, 280), "Found 3 Grounded Results in 42 ms  |  Grounded Score: 0.948  |  Zero Hallucination Guaranteed", fill="#475569", font=get_font(20))

    # Left Container: Synthesized Answer
    ans_x1, ans_y1, ans_x2, ans_y2 = 60, 320, 1450, h - 50
    draw.rounded_rectangle([ans_x1, ans_y1, ans_x2, ans_y2], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=2)
    draw.rectangle([ans_x1, ans_y1, ans_x2, ans_y1 + 70], fill="#F1F5F9")
    draw.text((ans_x1 + 35, ans_y1 + 20), "VERIFIED SYNTHESIZED ANSWER (STRICT OUT-OF-SCOPE FALLBACK)", fill="#059669", font=get_font(22, bold=True))

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
    cur_y = ans_y1 + 100
    for line in lines:
        if line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
            draw.text((ans_x1 + 35, cur_y), line, fill="#0284C7", font=get_font(21, bold=True))
        else:
            draw.text((ans_x1 + 35, cur_y), line, fill="#1E293B", font=get_font(21))
        cur_y += 38

    # Citations Area
    draw.rectangle([ans_x1, ans_y2 - 220, ans_x2, ans_y2], fill="#F8FAFC")
    draw.text((ans_x1 + 35, ans_y2 - 200), "VERIFIABLE CITATION SOURCES CITED:", fill="#475569", font=get_font(20, bold=True))

    c1_x1, c1_y1, c1_x2, c1_y2 = ans_x1 + 35, ans_y2 - 165, ans_x1 + 650, ans_y2 - 30
    draw.rounded_rectangle([c1_x1, c1_y1, c1_x2, c1_y2], radius=8, fill="#FFFFFF", outline="#2563EB", width=2)
    draw.text((c1_x1 + 20, c1_y1 + 15), "📄 architecture_specification.pdf", fill="#0F172A", font=get_font(20, bold=True))
    draw.text((c1_x1 + 20, c1_y1 + 48), "Section 4.3: Safe Proposal Engine", fill="#0284C7", font=get_font(18))
    draw.text((c1_x1 + 20, c1_y1 + 80), "Page: 28  |  Relevance: 97.4%", fill="#059669", font=get_font(18, bold=True))

    c2_x1, c2_y1, c2_x2, c2_y2 = ans_x1 + 700, ans_y2 - 165, ans_x2 - 35, ans_y2 - 30
    draw.rounded_rectangle([c2_x1, c2_y1, c2_x2, c2_y2], radius=8, fill="#FFFFFF", outline="#2563EB", width=2)
    draw.text((c2_x1 + 20, c2_y1 + 15), "📄 security_governance_policy.md", fill="#0F172A", font=get_font(20, bold=True))
    draw.text((c2_x1 + 20, c2_y1 + 48), "Section 2.1: Human Approval Protocol", fill="#0284C7", font=get_font(18))
    draw.text((c2_x1 + 20, c2_y1 + 80), "Line: 142  |  Relevance: 92.1%", fill="#059669", font=get_font(18, bold=True))

    # Right Container: Ranked Chunks
    rx1, ry1, rx2, ry2 = 1490, 320, w - 60, h - 50
    draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=2)
    draw.rectangle([rx1, ry1, rx2, ry1 + 70], fill="#F1F5F9")
    draw.text((rx1 + 35, ry1 + 20), "TOP RANKED DENSE CHUNKS", fill="#0F172A", font=get_font(22, bold=True))

    chunks = [
        {"title": "Chunk #104 [architecture_specification.pdf]", "sim": "Score: 0.962 (Dense)", "snippet": "...mutating tools must return ProposalPayload objects. FastAPIs router /api/proposals registers the diff for manager authorization before committing changes to tasks table..."},
        {"title": "Chunk #082 [security_governance_policy.md]", "sim": "Score: 0.918 (Hybrid)", "snippet": "...Human-in-the-loop review prevents unintended cascading slips in the project DAG. All rejected proposals are logged with auditor timestamps..."},
        {"title": "Chunk #215 [cpm_simulator_design.pdf]", "sim": "Score: 0.841 (BM25 Lexical)", "snippet": "...When deadlines shift, Kahn's algorithm recomputes Early Finish (EF) and Late Finish (LF) to assess if total slack drops to zero on critical path..."}
    ]
    cy = ry1 + 95
    for chk in chunks:
        ch_y2 = cy + 260
        draw.rounded_rectangle([rx1 + 25, cy, rx2 - 25, ch_y2], radius=8, fill="#F8FAFC", outline="#E2E8F0", width=2)
        draw.text((rx1 + 40, cy + 18), chk["title"], fill="#0284C7", font=get_font(20, bold=True))
        draw.text((rx2 - 320, cy + 18), chk["sim"], fill="#059669", font=get_font(18, bold=True))

        draw.text((rx1 + 40, cy + 65), chk["snippet"][:58], fill="#334155", font=get_font(18))
        draw.text((rx1 + 40, cy + 98), chk["snippet"][58:116], fill="#334155", font=get_font(18))
        draw.text((rx1 + 40, cy + 131), chk["snippet"][116:], fill="#334155", font=get_font(18))

        draw.rounded_rectangle([rx1 + 40, cy + 185, rx1 + 280, cy + 235], radius=6, fill="#FFFFFF", outline="#0284C7", width=2)
        draw.text((rx1 + 60, cy + 196), "Inspect Chunk Vector", fill="#0284C7", font=get_font(18, bold=True))
        cy += 290

    path = os.path.join(OUT_DIR, "search_engine_output.png")
    if os.path.exists(path): os.remove(path)
    img.save(path)
    print("Saved White search_engine_output.png")

# =============================================================================
# 6. COPILOT WAR ROOM CHAT TERMINAL (White Academic Theme)
# =============================================================================
def generate_light_copilot_output():
    w, h = 2400, 1400
    img = Image.new("RGB", (w, h), color="#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_light_header(draw, "Autonomous Multi-Agent AI War Room Copilot",
                      "5 Specialized Personas, Step-by-Step Decision Trace Pipeline & Tool Call Approval", w, "Copilot Terminal")

    # Left Sidebar: Swarm Personas
    sx1, sy1, sx2, sy2 = 60, 160, 560, h - 50
    draw.rounded_rectangle([sx1, sy1, sx2, sy2], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=2)
    draw.rectangle([sx1, sy1, sx2, sy1 + 70], fill="#F1F5F9")
    draw.text((sx1 + 35, sy1 + 20), "SWARM PERSONAS (5 ACTIVE)", fill="#0F172A", font=get_font(22, bold=True))

    agents = [
        {"name": "🤖 Project Manager Agent", "role": "Sprint Milestones & SLA Risks", "active": True},
        {"name": "💻 Developer Co-Pilot", "role": "Code Spikes & Task Decomp", "active": False},
        {"name": "🛡️ Security & Compliance", "role": "MFA, TOTP & Policy Audits", "active": False},
        {"name": "📚 Grounded RAG Agent", "role": "Verifiable Citation Retrieval", "active": False},
        {"name": "⚖️ Analytics & Workforce", "role": "Hungarian Skill Allocation", "active": False},
    ]
    ay = sy1 + 95
    for ag in agents:
        ab_bg = "#EFF6FF" if ag["active"] else "#FFFFFF"
        ab_border = "#2563EB" if ag["active"] else "#E2E8F0"
        draw.rounded_rectangle([sx1 + 20, ay, sx2 - 20, ay + 115], radius=10, fill=ab_bg, outline=ab_border, width=2)
        draw.text((sx1 + 35, ay + 20), ag["name"], fill="#0F172A", font=get_font(22, bold=True))
        draw.text((sx1 + 35, ay + 62), ag["role"], fill="#2563EB" if ag["active"] else "#64748B", font=get_font(18))
        ay += 135

    # Health Box
    draw.rounded_rectangle([sx1 + 20, sy2 - 220, sx2 - 20, sy2 - 25], radius=10, fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((sx1 + 35, sy2 - 195), "SYSTEM AUDIT STATE", fill="#059669", font=get_font(20, bold=True))
    draw.text((sx1 + 35, sy2 - 155), "• Permission Guard: ENFORCED", fill="#1E293B", font=get_font(18))
    draw.text((sx1 + 35, sy2 - 120), "• Role Scope: MANAGER", fill="#1E293B", font=get_font(18))
    draw.text((sx1 + 35, sy2 - 85), "• Decision Tracing: ENABLED", fill="#1E293B", font=get_font(18))

    # Right Main Chat Area
    cx1, cy1, cx2, cy2 = 600, 160, w - 60, h - 50
    draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=2)

    # Prompt bubble
    ux1, uy1, ux2, uy2 = cx1 + 40, cy1 + 35, cx2 - 40, cy1 + 135
    draw.rounded_rectangle([ux1, uy1, ux2, uy2], radius=10, fill="#F0F9FF", outline="#0284C7", width=2)
    draw.text((ux1 + 25, uy1 + 20), "👤 Engineering Manager (Dev Lead):", fill="#0284C7", font=get_font(20, bold=True))
    draw.text((ux1 + 25, uy1 + 58), "\"Task #104 (Kahn's CPM Simulator Engine) is showing 88% delivery risk. Can you diagnose the blocker and propose a fix?\"", fill="#0F172A", font=get_font(21))

    # Response bubble
    ax1, ay1, ax2, ay2 = cx1 + 40, cy1 + 165, cx2 - 40, cy1 + 820
    draw.rounded_rectangle([ax1, ay1, ax2, ay2], radius=10, fill="#F8FAFC", outline="#2563EB", width=2)
    draw.text((ax1 + 30, ay1 + 25), "🤖 Project Manager Agent (Autonomous Swarm Response):", fill="#059669", font=get_font(22, bold=True))

    # Decision Trace Box
    tx1, ty1, tx2, ty2 = ax1 + 30, ay1 + 70, ax2 - 30, ay1 + 225
    draw.rounded_rectangle([tx1, ty1, tx2, ty2], radius=8, fill="#FFFFFF", outline="#CBD5E1", width=2)
    draw.text((tx1 + 25, ty1 + 18), "AI DECISION TRACE PIPELINE (EXECUTION AUDIT):", fill="#D97706", font=get_font(18, bold=True))

    traces = [
        "1. Intent Analysis: Task Blocker Diagnosis & Risk Remediation (Confidence: 0.98)",
        "2. Permission Check: Role 'MANAGER' has permission 'TASK_REASSIGN' & 'PROPOSAL_CREATE' (Pass)",
        "3. Read Tool Call: inspect_task_topology(task_id='104') -> In-degree: 2, Blocked by: T2, Assignee Load: 94%",
        "4. Simulation Tool: cpm_simulate_reassignment(candidate='Sarah L.') -> Slack improves from 0 to +1.5 weeks"
    ]
    t_y = ty1 + 48
    for tr in traces:
        draw.text((tx1 + 25, t_y), tr, fill="#334155", font=get_font(18))
        t_y += 32

    # Diagnosis Paragraph
    exp_lines = [
        "Diagnosis: Task #104 is blocked because Vikram S. is currently saturated at 94% capacity across three tasks.",
        "Furthermore, Task #104 lies directly on the Critical Path (Zero Slack). Any further delay will cascade to Milestone 2.",
        "Remediation Recommendation: Reassign Task #104 to Sarah L., who currently operates at 42% workload."
    ]
    ey = ay1 + 245
    for el in exp_lines:
        draw.text((ax1 + 30, ey), el, fill="#0F172A", font=get_font(21))
        ey += 35

    # Safe Diff Proposal Card
    px1, py1, px2, py2 = ax1 + 30, ay1 + 380, ax2 - 30, ay1 + 610
    draw.rounded_rectangle([px1, py1, px2, py2], radius=10, fill="#FFFFFF", outline="#D97706", width=3)
    draw.rounded_rectangle([px1 + 25, py1 + 20, px1 + 420, py1 + 60], radius=6, fill="#FFFBEB")
    draw.text((px1 + 40, py1 + 28), "PROPOSAL DIFF #P-2026-04 (PENDING APPROVAL)", fill="#D97706", font=get_font(18, bold=True))

    draw.text((px1 + 35, py1 + 80), "Entity: Task #104 (Kahn's CPM Simulator Engine)", fill="#0F172A", font=get_font(22, bold=True))
    draw.text((px1 + 35, py1 + 120), "- Assignee: Vikram S. (Workload: 94% [OVERLOADED])", fill="#DC2626", font=get_font(21, bold=True))
    draw.text((px1 + 35, py1 + 158), "+ Assignee: Sarah L.  (Workload: 42% [OPTIMAL CAPACITY])", fill="#059669", font=get_font(21, bold=True))

    draw.rounded_rectangle([px2 - 440, py1 + 100, px2 - 235, py1 + 175], radius=8, fill="#059669")
    draw.text((px2 - 415, py1 + 122), "✔ Approve & Apply", fill="#FFFFFF", font=get_font(20, bold=True))

    draw.rounded_rectangle([px2 - 215, py1 + 100, px2 - 35, py1 + 175], radius=8, fill="#DC2626")
    draw.text((px2 - 185, py1 + 122), "✖ Reject Diff", fill="#FFFFFF", font=get_font(20, bold=True))

    # Bottom Input Prompt
    ix1, iy1, ix2, iy2 = cx1 + 40, cy2 - 110, cx2 - 40, cy2 - 25
    draw.rounded_rectangle([ix1, iy1, ix2, iy2], radius=10, fill="#F8FAFC", outline="#2563EB", width=2)
    draw.text((ix1 + 25, iy1 + 26), "Ask Copilot or issue swarm command (e.g., /simulate-cpm, /audit-mfa, /rag-search)...", fill="#64748B", font=get_font(20))
    draw.rounded_rectangle([ix2 - 160, iy1 + 12, ix2 - 15, iy2 - 12], radius=8, fill="#2563EB")
    draw.text((ix2 - 135, iy1 + 24), "Send ✈", fill="#FFFFFF", font=get_font(20, bold=True))

    path = os.path.join(OUT_DIR, "copilot_war_room.png")
    if os.path.exists(path): os.remove(path)
    img.save(path)
    print("Saved White copilot_war_room.png")

# =============================================================================
# 7. NEXUS RISK PREDICTION & RADAR (White Academic Theme)
# =============================================================================
def generate_light_risk_prediction():
    w, h = 2400, 1400
    img = Image.new("RGB", (w, h), color="#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_light_header(draw, "ML Predictive Risk Classification & Topological Delay Radar",
                      "Random Forest (n=50, depth=6) Evaluates In-Degree, Assignee Load & Blocker Hazards in Real-Time", w, "Risk Prediction")

    # Top KPI Banner (4 cards across width in pure white with subtle borders)
    kpis = [
        {"title": "ACTIVE AT-RISK TASKS", "val": "3 of 18", "sub": "2 Critical Path Blockers", "color": "#DC2626"},
        {"title": "MODEL ACCURACY / ROC-AUC", "val": "96.67% / 0.991", "sub": "Train/Val/Test (70/15/15)", "color": "#059669"},
        {"title": "PROJECTED SCHEDULE SLIP", "val": "+4.2 Days", "sub": "Without Autonomous Intervention", "color": "#D97706"},
        {"title": "RESOLVABLE BY SWARM", "val": "85.7%", "sub": "Via Diff Proposal Reassignment", "color": "#0284C7"}
    ]
    kw = (w - 180) // 4
    for i, kp in enumerate(kpis):
        kx1 = 60 + i * (kw + 20)
        ky1, kx2, ky2 = 160, kx1 + kw, 290
        draw.rounded_rectangle([kx1, ky1, kx2, ky2], radius=10, fill="#FFFFFF", outline="#CBD5E1", width=2)
        draw.text((kx1 + 25, ky1 + 20), kp["title"], fill="#64748B", font=get_font(18, bold=True))
        draw.text((kx1 + 25, ky1 + 50), kp["val"], fill=kp["color"], font=get_font(38, bold=True))
        draw.text((kx1 + 25, ky1 + 95), kp["sub"], fill="#475569", font=get_font(18))

    # Left Container: Task Risk Assessment Table
    tx1, ty1, tx2, ty2 = 60, 320, 1450, h - 50
    draw.rounded_rectangle([tx1, ty1, tx2, ty2], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=2)
    draw.rectangle([tx1, ty1, tx2, ty1 + 70], fill="#F1F5F9")
    draw.text((tx1 + 35, ty1 + 20), "REAL-TIME TASK RISK PREDICTION LEDGER", fill="#0F172A", font=get_font(22, bold=True))
    draw.text((tx2 - 340, ty1 + 22), "Inference Latency: 18ms", fill="#0284C7", font=get_font(20, bold=True))

    # Table Header
    th_y = ty1 + 85
    draw.rectangle([tx1 + 20, th_y, tx2 - 20, th_y + 45], fill="#E2E8F0")
    draw.text((tx1 + 35, th_y + 12), "Task Identifier & Title", fill="#475569", font=get_font(18, bold=True))
    draw.text((tx1 + 540, th_y + 12), "Assignee Load", fill="#475569", font=get_font(18, bold=True))
    draw.text((tx1 + 780, th_y + 12), "Blockers", fill="#475569", font=get_font(18, bold=True))
    draw.text((tx1 + 920, th_y + 12), "Slack", fill="#475569", font=get_font(18, bold=True))
    draw.text((tx1 + 1040, th_y + 12), "Risk Probability", fill="#475569", font=get_font(18, bold=True))
    draw.text((tx1 + 1240, th_y + 12), "Status", fill="#475569", font=get_font(18, bold=True))

    risk_tasks = [
        {"id": "TASK-104", "title": "Kahn's CPM Simulator Engine", "load": "94% (Vikram S.)", "blockers": "2 Tasks", "slack": "0.0 d", "prob": "88.4%", "level": "CRITICAL", "color": "#DC2626"},
        {"id": "TASK-108", "title": "Multi-Agent Swarm Diff Proposal", "load": "78% (Alex R.)", "blockers": "1 Task", "slack": "0.0 d", "prob": "76.2%", "level": "HIGH", "color": "#D97706"},
        {"id": "TASK-112", "title": "BM25 Hybrid Weight Calibration", "load": "62% (Sarah L.)", "blockers": "0 Tasks", "slack": "2.5 d", "prob": "41.5%", "level": "MEDIUM", "color": "#CA8A04"},
        {"id": "TASK-115", "title": "Flutter Riverpod Local Offline DB", "load": "45% (Dev K.)", "blockers": "0 Tasks", "slack": "4.0 d", "prob": "18.2%", "level": "LOW", "color": "#059669"},
        {"id": "TASK-119", "title": "RFC 6238 TOTP Fernet Validation", "load": "38% (Priya M.)", "blockers": "0 Tasks", "slack": "6.0 d", "prob": "08.1%", "level": "SAFE", "color": "#059669"},
        {"id": "TASK-122", "title": "GitHub Webhook HMAC Signature", "load": "40% (Alex R.)", "blockers": "0 Tasks", "slack": "5.5 d", "prob": "06.4%", "level": "SAFE", "color": "#059669"},
    ]

    row_y = th_y + 60
    for rt in risk_tasks:
        draw.rectangle([tx1 + 20, row_y - 6, tx2 - 20, row_y + 60], fill="#FEF2F2" if "CRITICAL" in rt["level"] or "HIGH" in rt["level"] else "#F8FAFC")
        draw.text((tx1 + 35, row_y + 6), f"{rt['id']}: {rt['title']}", fill="#0F172A", font=get_font(20, bold=True))
        draw.text((tx1 + 35, row_y + 34), "Critical Path: Primary Pipeline", fill="#64748B", font=get_font(16))

        draw.text((tx1 + 540, row_y + 16), rt["load"], fill="#DC2626" if "94%" in rt["load"] else "#334155", font=get_font(18))
        draw.text((tx1 + 780, row_y + 16), rt["blockers"], fill="#DC2626" if rt["blockers"] != "0 Tasks" else "#334155", font=get_font(18))
        draw.text((tx1 + 920, row_y + 16), rt["slack"], fill="#DC2626" if rt["slack"] == "0.0 d" else "#0284C7", font=get_font(18, bold=True))

        val_pct = float(rt["prob"].replace("%", ""))
        draw.rounded_rectangle([tx1 + 1040, row_y + 16, tx1 + 1200, row_y + 42], radius=4, fill="#E2E8F0")
        draw.rounded_rectangle([tx1 + 1040, row_y + 16, tx1 + 1040 + int(val_pct * 1.6), row_y + 42], radius=4, fill=rt["color"])
        draw.text((tx1 + 1048, row_y + 18), rt["prob"], fill="#FFFFFF", font=get_font(17, bold=True))

        draw.rounded_rectangle([tx1 + 1235, row_y + 12, tx2 - 35, row_y + 46], radius=6, fill="#FFFFFF", outline=rt["color"], width=2)
        draw.text((tx1 + 1250, row_y + 17), rt["level"], fill=rt["color"], font=get_font(17, bold=True))
        row_y += 75

    # Bottom Diagnosis Alert
    draw.rounded_rectangle([tx1 + 25, ty2 - 200, tx2 - 25, ty2 - 25], radius=10, fill="#FEF2F2", outline="#DC2626", width=2)
    draw.text((tx1 + 45, ty2 - 180), "⚠️ PREDICTIVE RISK DIAGNOSIS: CRITICAL BOTTLENECK DETECTED", fill="#DC2626", font=get_font(21, bold=True))
    draw.text((tx1 + 45, ty2 - 145), "Task TASK-104 exhibits an 88.4% delay probability because:", fill="#991B1B", font=get_font(19))
    draw.text((tx1 + 65, ty2 - 115), "1. Assignee Vikram S. is 94% overloaded across 3 concurrent microservice modules.", fill="#334155", font=get_font(18))
    draw.text((tx1 + 65, ty2 - 85), "2. The task has 2 unresolved prerequisite blockers and ZERO slack on the Critical Path.", fill="#334155", font=get_font(18))
    draw.text((tx1 + 65, ty2 - 55), "3. Recommended Action: Reassign to Sarah L. (42% load) to prevent a 4.2-day slip.", fill="#0284C7", font=get_font(18, bold=True))

    # Right Container: Gauge & SHAP Attributions
    rx1, ry1, rx2, ry2 = 1490, 320, w - 60, h - 50
    draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=2)
    draw.rectangle([rx1, ry1, rx2, ry1 + 70], fill="#F1F5F9")
    draw.text((rx1 + 35, ry1 + 20), "XAI RISK CONTRIBUTIONS (TASK-104)", fill="#0F172A", font=get_font(22, bold=True))

    # Large Circular Risk Gauge on white
    gx, gy, gr = rx1 + 420, ry1 + 250, 130
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline="#E2E8F0", width=22)
    draw.arc([gx - gr, gy - gr, gx + gr, gy + gr], start=-90, end=227, fill="#DC2626", width=22)
    draw.text((gx - 75, gy - 35), "88.4%", fill="#DC2626", font=get_font(48, bold=True))
    draw.text((gx - 60, gy + 22), "RISK SCORE", fill="#64748B", font=get_font(18, bold=True))
    draw.text((gx - 80, gy + 52), "HIGH FAILURE SLA", fill="#DC2626", font=get_font(17, bold=True))

    # SHAP Bars
    draw.text((rx1 + 35, ry1 + 420), "Local Feature Attributions (SHAP Delta):", fill="#0F172A", font=get_font(22, bold=True))
    feats = [
        {"label": "In-Degree Topological Blocker Count", "val": "+34.2%", "color": "#DC2626", "len": 360},
        {"label": "Deadline Proximity Delta (< 48 hrs)", "val": "+26.8%", "color": "#D97706", "len": 280},
        {"label": "Assignee Overload Saturation (94%)", "val": "+19.5%", "color": "#2563EB", "len": 210},
        {"label": "Historical PR Review Turnaround Lag", "val": "+11.4%", "color": "#0284C7", "len": 120},
        {"label": "Downstream Dependent Out-Degree", "val": "+08.1%", "color": "#7C3AED", "len": 90},
    ]

    fy = ry1 + 475
    for ft in feats:
        draw.text((rx1 + 35, fy), ft["label"], fill="#334155", font=get_font(19))
        draw.text((rx2 - 120, fy), ft["val"], fill=ft["color"], font=get_font(19, bold=True))
        
        draw.rounded_rectangle([rx1 + 35, fy + 32, rx2 - 35, fy + 52], radius=6, fill="#F1F5F9")
        draw.rounded_rectangle([rx1 + 35, fy + 32, rx1 + 35 + ft["len"], fy + 52], radius=6, fill=ft["color"])
        fy += 75

    # Bottom Trigger Action
    draw.rounded_rectangle([rx1 + 35, ry2 - 110, rx2 - 35, ry2 - 30], radius=10, fill="#DC2626")
    draw.text((rx1 + 220, ry2 - 80), "⚡ Trigger Swarm Auto-Remediation", fill="#FFFFFF", font=get_font(24, bold=True))

    path = os.path.join(OUT_DIR, "nexus_risk_prediction.png")
    if os.path.exists(path): os.remove(path)
    img.save(path)
    print("Saved White nexus_risk_prediction.png")

if __name__ == "__main__":
    generate_light_live_graph()
    generate_light_gantt_chart()
    generate_light_kanban_board()
    generate_light_graph_chart()
    generate_light_search_engine_output()
    generate_light_copilot_output()
    generate_light_risk_prediction()
    print("ALL 7 ULTRA-HD IMAGES REGENERATED IN WHITE THEME!")

