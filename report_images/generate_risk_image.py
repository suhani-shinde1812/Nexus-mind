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

def draw_header(draw, title, subtitle, width, tag="ML Risk Engine"):
    draw.rectangle([0, 0, width, 70], fill="#0f172a")
    draw.rectangle([0, 70, width, 72], fill="#334155")
    draw.text((30, 15), title, fill="#f8fafc", font=get_font(24, bold=True))
    draw.text((30, 44), subtitle, fill="#94a3b8", font=get_font(13))
    draw.rounded_rectangle([width - 270, 18, width - 30, 52], radius=6, fill="#1e293b", outline="#ef4444", width=1)
    draw.text((width - 255, 26), f"● Nexus Mind :: {tag}", fill="#f87171", font=get_font(12, bold=True))

def generate_risk_prediction_image():
    w, h = 1300, 800
    img = Image.new("RGB", (w, h), color="#090d16")
    draw = ImageDraw.Draw(img)
    draw_header(draw, "ML Predictive Risk Classification & Topological Delay Radar", 
                "Random Forest (n=50, depth=6) Evaluates In-Degree, Assignee Load & Blocker Hazards in Real-Time", w, "Risk Prediction")

    # Top KPI Banner (4 cards across width)
    kpis = [
        {"title": "ACTIVE AT-RISK TASKS", "val": "3 of 18", "sub": "2 Critical Path Blockers", "color": "#ef4444"},
        {"title": "MODEL ACCURACY / ROC-AUC", "val": "96.67% / 0.991", "sub": "Train/Val/Test (70/15/15)", "color": "#10b981"},
        {"title": "PROJECTED SCHEDULE SLIP", "val": "+4.2 Days", "sub": "Without Autonomous Intervention", "color": "#f59e0b"},
        {"title": "RESOLVABLE BY SWARM", "val": "85.7%", "sub": "Via Diff Proposal Reassignment", "color": "#38bdf8"}
    ]
    kw = (w - 100) // 4
    for i, kp in enumerate(kpis):
        kx1 = 40 + i * (kw + 7)
        ky1, kx2, ky2 = 88, kx1 + kw, 168
        draw.rounded_rectangle([kx1, ky1, kx2, ky2], radius=6, fill="#0f172a", outline="#334155", width=1)
        draw.text((kx1 + 14, ky1 + 10), kp["title"], fill="#94a3b8", font=get_font(10, bold=True))
        draw.text((kx1 + 14, ky1 + 28), kp["val"], fill=kp["color"], font=get_font(20, bold=True))
        draw.text((kx1 + 14, ky1 + 54), kp["sub"], fill="#64748b", font=get_font(10))

    # Left Container: Task Risk Assessment Table / Radar (width: 760)
    tx1, ty1, tx2, ty2 = 40, 185, 800, h - 35
    draw.rounded_rectangle([tx1, ty1, tx2, ty2], radius=8, fill="#0f172a", outline="#334155", width=1)
    draw.rectangle([tx1, ty1, tx2, ty1 + 45], fill="#1e293b")
    draw.text((tx1 + 20, ty1 + 14), "REAL-TIME TASK RISK PREDICTION LEDGER", fill="#f8fafc", font=get_font(12, bold=True))
    draw.text((tx2 - 200, ty1 + 14), "Inference Latency: 18ms", fill="#38bdf8", font=get_font(11))

    # Table Header
    th_y = ty1 + 50
    draw.rectangle([tx1 + 10, th_y, tx2 - 10, th_y + 30], fill="#131d31")
    draw.text((tx1 + 20, th_y + 8), "Task Identifier & Title", fill="#94a3b8", font=get_font(10, bold=True))
    draw.text((tx1 + 320, th_y + 8), "Assignee Load", fill="#94a3b8", font=get_font(10, bold=True))
    draw.text((tx1 + 430, th_y + 8), "Blockers", fill="#94a3b8", font=get_font(10, bold=True))
    draw.text((tx1 + 510, th_y + 8), "Slack", fill="#94a3b8", font=get_font(10, bold=True))
    draw.text((tx1 + 580, th_y + 8), "Risk Probability", fill="#94a3b8", font=get_font(10, bold=True))
    draw.text((tx1 + 700, th_y + 8), "Status", fill="#94a3b8", font=get_font(10, bold=True))

    risk_tasks = [
        {"id": "TASK-104", "title": "Kahn's CPM Simulator Engine", "load": "94% (Vikram S.)", "blockers": "2 Tasks", "slack": "0.0 d", "prob": "88.4%", "level": "CRITICAL", "color": "#ef4444"},
        {"id": "TASK-108", "title": "Multi-Agent Swarm Diff Proposal", "load": "78% (Alex R.)", "blockers": "1 Task", "slack": "0.0 d", "prob": "76.2%", "level": "HIGH", "color": "#f97316"},
        {"id": "TASK-112", "title": "BM25 Hybrid Weight Calibration", "load": "62% (Sarah L.)", "blockers": "0 Tasks", "slack": "2.5 d", "prob": "41.5%", "level": "MEDIUM", "color": "#facc15"},
        {"id": "TASK-115", "title": "Flutter Riverpod Local Offline DB", "load": "45% (Dev K.)", "blockers": "0 Tasks", "slack": "4.0 d", "prob": "18.2%", "level": "LOW", "color": "#10b981"},
        {"id": "TASK-119", "title": "RFC 6238 TOTP Fernet Validation", "load": "38% (Priya M.)", "blockers": "0 Tasks", "slack": "6.0 d", "prob": "08.1%", "level": "SAFE", "color": "#10b981"},
        {"id": "TASK-122", "title": "GitHub Webhook HMAC Signature", "load": "40% (Alex R.)", "blockers": "0 Tasks", "slack": "5.5 d", "prob": "06.4%", "level": "SAFE", "color": "#10b981"},
    ]

    row_y = th_y + 38
    for rt in risk_tasks:
        draw.rectangle([tx1 + 10, row_y - 4, tx2 - 10, row_y + 36], fill="#1e293b" if "CRITICAL" in rt["level"] or "HIGH" in rt["level"] else "#0d1527")
        draw.text((tx1 + 20, row_y + 2), f"{rt['id']}: {rt['title'][:26]}", fill="#ffffff", font=get_font(11, bold=True))
        draw.text((tx1 + 20, row_y + 18), "CPM Path: Primary Pipeline", fill="#64748b", font=get_font(9))

        draw.text((tx1 + 320, row_y + 8), rt["load"], fill="#f87171" if "94%" in rt["load"] else "#cbd5e1", font=get_font(10))
        draw.text((tx1 + 430, row_y + 8), rt["blockers"], fill="#f87171" if rt["blockers"] != "0 Tasks" else "#cbd5e1", font=get_font(10))
        draw.text((tx1 + 510, row_y + 8), rt["slack"], fill="#ef4444" if rt["slack"] == "0.0 d" else "#38bdf8", font=get_font(10, bold=True))
        
        # Risk progress bar
        val_pct = float(rt["prob"].replace("%", ""))
        draw.rounded_rectangle([tx1 + 580, row_y + 8, tx1 + 680, row_y + 22], radius=3, fill="#0f172a")
        draw.rounded_rectangle([tx1 + 580, row_y + 8, tx1 + 580 + int(val_pct), row_y + 22], radius=3, fill=rt["color"])
        draw.text((tx1 + 585, row_y + 9), rt["prob"], fill="#ffffff", font=get_font(9, bold=True))

        # Level badge
        draw.rounded_rectangle([tx1 + 700, row_y + 6, tx2 - 20, row_y + 24], radius=4, fill="#0f172a", outline=rt["color"], width=1)
        draw.text((tx1 + 708, row_y + 9), rt["level"], fill=rt["color"], font=get_font(9, bold=True))

        row_y += 44

    # Bottom Explainable Alert in Left Box
    draw.rounded_rectangle([tx1 + 15, ty2 - 135, tx2 - 15, ty2 - 15], radius=6, fill="#1c1917", outline="#ef4444", width=1)
    draw.text((tx1 + 30, ty2 - 122), "⚠️ PREDICTIVE RISK DIAGNOSIS: CRITICAL BOTTLENECK DETECTED", fill="#f87171", font=get_font(11, bold=True))
    draw.text((tx1 + 30, ty2 - 100), "Task TASK-104 exhibits an 88.4% delay probability because:", fill="#fed7aa", font=get_font(10))
    draw.text((tx1 + 45, ty2 - 82), "1. Assignee Vikram S. is 94% overloaded across 3 concurrent microservice modules.", fill="#cbd5e1", font=get_font(10))
    draw.text((tx1 + 45, ty2 - 64), "2. The task has 2 unresolved prerequisite blockers and ZERO slack on the Critical Path.", fill="#cbd5e1", font=get_font(10))
    draw.text((tx1 + 45, ty2 - 46), "3. Recommended Swarm Action: Reassign to Sarah L. (42% load) to prevent a 4.2-day schedule slip.", fill="#38bdf8", font=get_font(10, bold=True))

    # Right Container: Risk Radar / Gauge & SHAP Feature Contribution (width: 440)
    rx1, ry1, rx2, ry2 = 825, 185, w - 40, h - 35
    draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=8, fill="#0f172a", outline="#334155", width=1)
    draw.rectangle([rx1, ry1, rx2, ry1 + 45], fill="#1e293b")
    draw.text((rx1 + 20, ry1 + 14), "XAI RISK CONTRIBUTIONS (TASK-104)", fill="#f8fafc", font=get_font(12, bold=True))

    # Large Circular Risk Gauge
    gx, gy, gr = rx1 + 215, ry1 + 155, 75
    # Outer circle track
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline="#334155", width=12)
    # Highlight arc representing 88%
    draw.arc([gx - gr, gy - gr, gx + gr, gy + gr], start=-90, end=227, fill="#ef4444", width=12)
    draw.text((gx - 45, gy - 20), "88.4%", fill="#ef4444", font=get_font(28, bold=True))
    draw.text((gx - 35, gy + 15), "RISK SCORE", fill="#94a3b8", font=get_font(10, bold=True))
    draw.text((gx - 48, gy + 32), "HIGH FAILURE SLA", fill="#f87171", font=get_font(9, bold=True))

    # SHAP / Feature Importance Breakdown Bars
    draw.text((rx1 + 20, ry1 + 250), "Local Feature Attributions (SHAP Delta):", fill="#cbd5e1", font=get_font(11, bold=True))
    
    feats = [
        {"label": "In-Degree Topological Blocker Count", "val": "+34.2%", "color": "#ef4444", "len": 180},
        {"label": "Deadline Proximity Delta (< 48 hrs)", "val": "+26.8%", "color": "#f97316", "len": 140},
        {"label": "Assignee Overload Saturation (94%)", "val": "+19.5%", "color": "#f59e0b", "len": 105},
        {"label": "Historical PR Review Turnaround Lag", "val": "+11.4%", "color": "#38bdf8", "len": 60},
        {"label": "Downstream Dependent Out-Degree", "val": "+08.1%", "color": "#a855f7", "len": 45},
    ]

    fy = ry1 + 280
    for ft in feats:
        draw.text((rx1 + 20, fy), ft["label"][:38], fill="#94a3b8", font=get_font(10))
        draw.text((rx2 - 60, fy), ft["val"], fill=ft["color"], font=get_font(10, bold=True))
        
        draw.rounded_rectangle([rx1 + 20, fy + 18, rx2 - 20, fy + 28], radius=3, fill="#1e293b")
        draw.rounded_rectangle([rx1 + 20, fy + 18, rx1 + 20 + ft["len"], fy + 28], radius=3, fill=ft["color"])
        fy += 44

    # Bottom Reassignment Action Button
    draw.rounded_rectangle([rx1 + 20, ry2 - 65, rx2 - 20, ry2 - 15], radius=6, fill="#ef4444")
    draw.text((rx1 + 80, ry2 - 47), "⚡ Trigger Swarm Auto-Remediation", fill="#ffffff", font=get_font(12, bold=True))

    img.save(os.path.join(OUT_DIR, "nexus_risk_prediction.png"))
    print("Saved nexus_risk_prediction.png")

if __name__ == "__main__":
    generate_risk_prediction_image()

