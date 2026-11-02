import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = r"E:\nexus-mind\report_images"
os.makedirs(OUT_DIR, exist_ok=True)

def get_font(size, bold=False):
    font_paths = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
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
    # Premium Clean White Header
    draw.rectangle([0, 0, width, 130], fill="#FFFFFF")
    draw.rectangle([0, 130, width, 136], fill="#2563EB")
    draw.text((60, 24), title, fill="#0F172A", font=get_font(42, bold=True))
    draw.text((60, 80), subtitle, fill="#475569", font=get_font(24, bold=False))
    
    badge_w = 460
    bx1 = width - badge_w - 60
    draw.rounded_rectangle([bx1, 32, width - 60, 98], radius=12, fill="#F1F5F9", outline="#0284C7", width=2)
    draw.text((bx1 + 25, 48), f"● Nexus Mind :: {tag}", fill="#0284C7", font=get_font(24, bold=True))

# =============================================================================
# 8. HOME PAGE / MAIN COCKPIT DASHBOARD (White Academic Theme)
# =============================================================================
def generate_light_home_page():
    w, h = 2400, 1400
    img = Image.new("RGB", (w, h), color="#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_light_header(draw, "Nexus Mind — Unified Operations Cockpit (Home)",
                      "Executive Team Lead Portal, Single Source of Truth & Live Force-Directed Task Matrix", w, "Workspace Home")

    # Top Navigation Breadcrumb / Control Strip
    nav_y1, nav_y2 = 145, 215
    draw.rectangle([0, nav_y1, w, nav_y2], fill="#FFFFFF")
    draw.line([0, nav_y2, w, nav_y2], fill="#E2E8F0", width=2)
    
    # Left View-as selector
    draw.rounded_rectangle([60, nav_y1 + 12, 380, nav_y2 - 12], radius=8, fill="#F1F5F9", outline="#CBD5E1", width=1)
    draw.text((80, nav_y1 + 20), "VIEW AS: Team Lead Portal", fill="#0F172A", font=get_font(18, bold=True))
    
    # Middle Search pill
    draw.rounded_rectangle([420, nav_y1 + 12, 1100, nav_y2 - 12], radius=8, fill="#F8FAFC", outline="#CBD5E1", width=1)
    draw.text((440, nav_y1 + 20), "🔍 Search tasks (TASK-109), docs, policies... (Press '/')", fill="#64748B", font=get_font(17))

    # Right Action Buttons
    draw.rounded_rectangle([w - 680, nav_y1 + 12, w - 460, nav_y2 - 12], radius=8, fill="#2563EB")
    draw.text((w - 655, nav_y1 + 20), "⚡ Run AI Risk Scan", fill="#FFFFFF", font=get_font(17, bold=True))

    draw.rounded_rectangle([w - 440, nav_y1 + 12, w - 240, nav_y2 - 12], radius=8, fill="#059669")
    draw.text((w - 415, nav_y1 + 20), "➕ New Task", fill="#FFFFFF", font=get_font(17, bold=True))

    draw.rounded_rectangle([w - 220, nav_y1 + 12, w - 60, nav_y2 - 12], radius=8, fill="#F1F5F9", outline="#CBD5E1", width=1)
    draw.text((w - 195, nav_y1 + 20), "👤 suhani s.", fill="#0F172A", font=get_font(17, bold=True))

    # Main Grid Layout: Left Panel (Portal Tabs & Feed), Right Panel (Live Graph Preview)
    # Left Panel: width 1100 (60 -> 1160)
    lx1, ly1, lx2, ly2 = 60, 235, 1160, h - 45
    draw.rounded_rectangle([lx1, ly1, lx2, ly2], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=2)
    
    # Portal Tabs Header
    tabs = ["Dashboard", "Tasks", "War Room", "Simulator", "Analytics", "Meetings", "Knowledge", "Audit"]
    tw = (lx2 - lx1 - 40) // len(tabs)
    for i, tb in enumerate(tabs):
        tx1 = lx1 + 20 + i * tw
        tx2 = tx1 + tw - 6
        is_active = (i == 0)
        t_bg = "#2563EB" if is_active else "#F1F5F9"
        t_fg = "#FFFFFF" if is_active else "#475569"
        draw.rounded_rectangle([tx1, ly1 + 18, tx2, ly1 + 62], radius=8, fill=t_bg)
        draw.text((tx1 + 12, ly1 + 28), tb, fill=t_fg, font=get_font(16, bold=True))

    # 3 Stat Cards on Left
    stats = [
        {"title": "ACTIVE HEADCOUNT", "val": "8 Engineers", "sub": "100% Verified Accounts", "color": "#2563EB"},
        {"title": "SPRINT VELOCITY", "val": "92.4% On-Track", "sub": "+4.2% vs Last Sprint", "color": "#059669"},
        {"title": "CRITICAL BOTTLENECKS", "val": "1 Blocker", "sub": "TASK-104 Requires Swarm", "color": "#DC2626"}
    ]
    sw = (lx2 - lx1 - 60) // 3
    for i, st in enumerate(stats):
        sx1 = lx1 + 20 + i * (sw + 10)
        sx2 = sx1 + sw
        draw.rounded_rectangle([sx1, ly1 + 80, sx2, ly1 + 210], radius=10, fill="#F8FAFC", outline="#E2E8F0", width=1)
        draw.text((sx1 + 16, ly1 + 95), st["title"], fill="#64748B", font=get_font(14, bold=True))
        draw.text((sx1 + 16, ly1 + 125), st["val"], fill=st["color"], font=get_font(28, bold=True))
        draw.text((sx1 + 16, ly1 + 175), st["sub"], fill="#475569", font=get_font(14))

    # Tasks Feed on Left
    draw.text((lx1 + 25, ly1 + 235), "📌 ACTIVE WORK QUEUE & SPRINT DELIVERABLES", fill="#0F172A", font=get_font(18, bold=True))
    
    feed_tasks = [
        {"id": "TASK-109", "title": "Platform Management & Enterprise Access", "user": "suhani shinde", "status": "IN PROGRESS", "due": "2026-11-15", "col": "#2563EB"},
        {"id": "TASK-104", "title": "React Dashboard UI & Role Authorization Views", "user": "suhani shinde", "status": "BLOCKED", "due": "2026-11-10", "col": "#DC2626"},
        {"id": "TASK-102", "title": "PostgreSQL Schema Partitioning & Migrations", "user": "suhani shinde", "status": "IN REVIEW", "due": "2026-11-08", "col": "#D97706"},
        {"id": "TASK-101", "title": "Cloud Infrastructure Provisioning (Terraform)", "user": "suhani shinde", "status": "COMPLETED", "due": "2026-11-02", "col": "#059669"},
    ]
    f_y = ly1 + 270
    for ft in feed_tasks:
        draw.rounded_rectangle([lx1 + 20, f_y, lx2 - 20, f_y + 90], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
        draw.rounded_rectangle([lx1 + 35, f_y + 16, lx1 + 165, f_y + 44], radius=6, fill="#F1F5F9")
        draw.text((lx1 + 45, f_y + 22), ft["status"], fill=ft["col"], font=get_font(13, bold=True))
        
        draw.text((lx1 + 185, f_y + 18), f"{ft['id']}: {ft['title']}", fill="#0F172A", font=get_font(18, bold=True))
        draw.text((lx1 + 185, f_y + 52), f"Assignee: {ft['user']}   |   Due: {ft['due']}   |   Priority: High", fill="#64748B", font=get_font(14))
        
        draw.rounded_rectangle([lx2 - 130, f_y + 25, lx2 - 35, f_y + 65], radius=6, fill="#2563EB")
        draw.text((lx2 - 110, f_y + 35), "Inspect", fill="#FFFFFF", font=get_font(14, bold=True))
        f_y += 105

    # Right Panel: Live Task Graph Workspace (1200 -> 2340)
    rx1, ry1, rx2, ry2 = 1200, 235, w - 60, h - 45
    draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=2)
    
    # Right panel header
    draw.rectangle([rx1, ry1, rx2, ry1 + 65], fill="#F1F5F9")
    draw.text((rx1 + 30, ry1 + 20), "⚡ LIVE TASK GRAPH MATRIX (SINGLE SOURCE OF TRUTH)", fill="#0F172A", font=get_font(20, bold=True))
    draw.text((rx2 - 280, ry1 + 22), "View: Graph | Kanban | Gantt", fill="#2563EB", font=get_font(16, bold=True))

    # Dot grid inside workspace
    for x in range(rx1 + 30, rx2 - 30, 45):
        for y in range(ry1 + 90, ry2 - 30, 45):
            draw.ellipse([x, y, x + 2, y + 2], fill="#CBD5E1")

    # Mini graph nodes inside workspace
    gnodes = [
        {"name": "Auth Core", "x": rx1 + 160, "y": ry1 + 280, "col": "#059669"},
        {"name": "Database Schema", "x": rx1 + 420, "y": ry1 + 200, "col": "#2563EB"},
        {"name": "API Gateway", "x": rx1 + 420, "y": ry1 + 420, "col": "#2563EB"},
        {"name": "React UI (Blocked)", "x": rx1 + 720, "y": ry1 + 300, "col": "#DC2626"},
        {"name": "Platform Deploy", "x": rx1 + 980, "y": ry1 + 300, "col": "#D97706"},
    ]
    # Connectors
    draw.line([rx1 + 160, ry1 + 280, rx1 + 420, ry1 + 200], fill="#94A3B8", width=3)
    draw.line([rx1 + 160, ry1 + 280, rx1 + 420, ry1 + 420], fill="#94A3B8", width=3)
    draw.line([rx1 + 420, ry1 + 200, rx1 + 720, ry1 + 300], fill="#DC2626", width=4)
    draw.line([rx1 + 420, ry1 + 420, rx1 + 720, ry1 + 300], fill="#94A3B8", width=3)
    draw.line([rx1 + 720, ry1 + 300, rx1 + 980, ry1 + 300], fill="#DC2626", width=4)

    for gn in gnodes:
        gx, gy = gn["x"], gn["y"]
        draw.ellipse([gx - 45, gy - 45, gx + 45, gy + 45], fill="#FFFFFF", outline=gn["col"], width=4)
        draw.ellipse([gx - 18, gy - 18, gx + 18, gy + 18], fill=gn["col"])
        draw.text((gx - 55, gy + 55), gn["name"], fill="#0F172A", font=get_font(15, bold=True))

    # Bottom Legend in Right Box
    draw.rounded_rectangle([rx1 + 30, ry2 - 80, rx2 - 30, ry2 - 20], radius=8, fill="#F8FAFC", outline="#E2E8F0", width=1)
    draw.text((rx1 + 50, ry2 - 58), "Legend:  🟢 Completed    🔵 In Progress    🔴 High Risk / Blocked    🟠 Critical Path Sequence", fill="#475569", font=get_font(16, bold=True))

    path = os.path.join(OUT_DIR, "home_page.png")
    if os.path.exists(path): os.remove(path)
    img.save(path)
    print("Saved White home_page.png")

# =============================================================================
# 9. MEETING PAGE / MEETING INTELLIGENCE AGENT (White Academic Theme)
# =============================================================================
def generate_light_meeting_page():
    w, h = 2400, 1400
    img = Image.new("RGB", (w, h), color="#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_light_header(draw, "Meeting Intelligence & Real-Time NLP Transcription",
                      "WebRTC Video Conferencing, Live Speech-to-Text & Automated Action-Item Task Extraction", w, "Meeting Intelligence")

    # Top Control Strip
    nav_y1, nav_y2 = 145, 215
    draw.rectangle([0, nav_y1, w, nav_y2], fill="#FFFFFF")
    draw.line([0, nav_y2, w, nav_y2], fill="#E2E8F0", width=2)
    
    draw.text((60, nav_y1 + 22), "📅 ACTIVE SESSION: Sprint Alpha Standup & Technical Review (Room: #Nexus-Alpha-01)", fill="#0F172A", font=get_font(19, bold=True))
    
    draw.rounded_rectangle([w - 620, nav_y1 + 12, w - 380, nav_y2 - 12], radius=8, fill="#DC2626")
    draw.text((w - 595, nav_y1 + 20), "⏹ Stop & Extract", fill="#FFFFFF", font=get_font(17, bold=True))

    draw.rounded_rectangle([w - 360, nav_y1 + 12, w - 60, nav_y2 - 12], radius=8, fill="#2563EB")
    draw.text((w - 335, nav_y1 + 20), "➕ Schedule Meeting", fill="#FFFFFF", font=get_font(17, bold=True))

    # Left Container: Live Video Stream & Real-Time Transcript (width: 1300)
    vx1, vy1, vx2, vy2 = 60, 235, 1360, h - 45
    draw.rounded_rectangle([vx1, vy1, vx2, vy2], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=2)
    
    # Video preview placeholder box
    draw.rounded_rectangle([vx1 + 25, vy1 + 25, vx2 - 25, vy1 + 380], radius=10, fill="#1E293B")
    draw.text((vx1 + 55, vy1 + 50), "🎥 WEBRTC SECURE VIDEO STREAM [ACTIVE]", fill="#10B981", font=get_font(16, bold=True))
    
    # 4 participant webcam feeds inside video box
    pw = (vx2 - vx1 - 90) // 4
    for i, p_name in enumerate(["suhani s. (Lead)", "Alex V. (Frontend)", "Devon R. (Backend)", "Elena R. (Admin)"]):
        px1 = vx1 + 35 + i * (pw + 10)
        px2 = px1 + pw
        draw.rounded_rectangle([px1, vy1 + 90, px2, vy1 + 350], radius=8, fill="#0F172A", outline="#475569", width=1)
        # Avatar circle
        draw.ellipse([px1 + pw//2 - 35, vy1 + 150, px1 + pw//2 + 35, vy1 + 220], fill="#3B82F6")
        draw.text((px1 + pw//2 - 15, vy1 + 172), p_name[0], fill="#FFFFFF", font=get_font(24, bold=True))
        draw.text((px1 + 15, vy1 + 300), p_name, fill="#E2E8F0", font=get_font(14, bold=True))

    # Live Transcript Feed Below Video
    draw.text((vx1 + 30, vy1 + 410), "🎙️ LIVE SPEECH-TO-TEXT TRANSCRIPT (AUTO-LISTEN)", fill="#0284C7", font=get_font(19, bold=True))
    draw.rounded_rectangle([vx1 + 25, vy1 + 445, vx2 - 25, vy2 - 25], radius=10, fill="#F8FAFC", outline="#E2E8F0", width=1)

    transcripts = [
        {"time": "10:02:15", "speaker": "suhani s.", "text": "Good morning team. Let's inspect the critical path blocker on TASK-104."},
        {"time": "10:02:48", "speaker": "Alex V.", "text": "I am waiting on the OAuth2 API gateway to finish before deploying React portals."},
        {"time": "10:03:12", "speaker": "suhani s.", "text": "Action Item: Devon will finalize the OAuth2 refresh tokens and endpoint security by tomorrow."},
        {"time": "10:03:40", "speaker": "Devon R.", "text": "Understood. I will push the commit and update the Alembic migration script by 4 PM."},
        {"time": "10:04:05", "speaker": "Elena R.", "text": "We also need to audit the RFC 6238 TOTP backup keys before staging release."}
    ]
    t_y = vy1 + 465
    for tr in transcripts:
        draw.text((vx1 + 45, t_y), f"[{tr['time']}]", fill="#94A3B8", font=get_font(15))
        draw.text((vx1 + 140, t_y), f"{tr['speaker']}:", fill="#0284C7", font=get_font(16, bold=True))
        draw.text((vx1 + 270, t_y), tr["text"], fill="#1E293B", font=get_font(16))
        t_y += 45

    # Right Container: NLP Action Items & One-Click Task Generator (width: 960)
    ax1, ay1, ax2, ay2 = 1400, 235, w - 60, h - 45
    draw.rounded_rectangle([ax1, ay1, ax2, ay2], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=2)
    
    # Right Header
    draw.rectangle([ax1, ay1, ax2, ay1 + 65], fill="#F1F5F9")
    draw.text((ax1 + 30, ay1 + 20), "✨ NLP ACTION ITEMS EXTRACTED (3 DETECTED)", fill="#7C3AED", font=get_font(20, bold=True))
    draw.text((ax2 - 240, ay1 + 22), "Confidence: 96.8%", fill="#059669", font=get_font(16, bold=True))

    actions = [
        {
            "task": "Finalize OAuth2 Refresh Tokens & Endpoint Security",
            "assignee": "Devon R.",
            "due": "Tomorrow, 4:00 PM",
            "conf": "98% NLP Match",
            "context": "Extracted from: 'Devon will finalize the OAuth2 refresh tokens...'"
        },
        {
            "task": "Update Alembic PostgreSQL Migration Script",
            "assignee": "Devon R.",
            "due": "Today, 4:00 PM",
            "conf": "95% NLP Match",
            "context": "Extracted from: 'I will push the commit and update migration...'"
        },
        {
            "task": "Audit RFC 6238 TOTP Backup Keys for Staging",
            "assignee": "Elena R.",
            "due": "Friday, 12:00 PM",
            "conf": "92% NLP Match",
            "context": "Extracted from: 'We need to audit the RFC 6238 TOTP backup keys...'"
        }
    ]

    a_y = ay1 + 90
    for act in actions:
        draw.rounded_rectangle([ax1 + 25, a_y, ax2 - 25, a_y + 195], radius=10, fill="#F8FAFC", outline="#CBD5E1", width=1)
        draw.text((ax1 + 45, a_y + 18), act["task"], fill="#0F172A", font=get_font(20, bold=True))
        draw.text((ax1 + 45, a_y + 55), f"Suggested Assignee: {act['assignee']}   |   Target Deadline: {act['due']}", fill="#2563EB", font=get_font(16, bold=True))
        draw.text((ax1 + 45, a_y + 90), act["context"], fill="#64748B", font=get_font(15))
        
        # NLP Badge
        draw.rounded_rectangle([ax1 + 45, a_y + 130, ax1 + 210, a_y + 168], radius=6, fill="#EDE9FE")
        draw.text((ax1 + 60, a_y + 140), act["conf"], fill="#7C3AED", font=get_font(14, bold=True))

        # 1-Click Insert Button
        draw.rounded_rectangle([ax2 - 280, a_y + 125, ax2 - 45, a_y + 172], radius=8, fill="#059669")
        draw.text((ax2 - 260, a_y + 138), "➕ Add to Live DAG", fill="#FFFFFF", font=get_font(15, bold=True))

        a_y += 225

    # Bottom Automation Summary Box
    draw.rounded_rectangle([ax1 + 25, ay2 - 130, ax2 - 25, ay2 - 25], radius=10, fill="#EFF6FF", outline="#2563EB", width=1)
    draw.text((ax1 + 45, ay2 - 105), "🤖 AI MEETING AGENT SUMMARY AUTOMATION", fill="#2563EB", font=get_font(17, bold=True))
    draw.text((ax1 + 45, ay2 - 68), "Upon meeting conclusion, all verified action items automatically sync to the PostgreSQL Task table,", fill="#334155", font=get_font(15))
    draw.text((ax1 + 45, ay2 - 42), "recompute Kahn's CPM DAG critical path, and dispatch real-time WebSocket notifications.", fill="#334155", font=get_font(15))

    path = os.path.join(OUT_DIR, "meeting_page.png")
    if os.path.exists(path): os.remove(path)
    img.save(path)
    print("Saved White meeting_page.png")

if __name__ == "__main__":
    generate_light_home_page()
    generate_light_meeting_page()
    print("Both Home Page and Meeting Page generated in White Theme!")

