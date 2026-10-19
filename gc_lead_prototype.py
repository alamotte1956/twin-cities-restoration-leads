from flask import Flask, render_template_string, request, redirect, url_for
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "restoration-leads-prototype-2026"

leads = []

PRIMARY_CONTRACTOR = {
    "name": "Diamond Restoration Services LLC",
    "phone": "(612) 306-1043",
    "email": "leads@tc-restoration.example",
    "service_area": "Minneapolis–St. Paul metro and select suburbs",
    "specialties": [
        "water damage restoration",
        "dry out",
        "mold mitigation",
        "mold inspection",
        "mold remediation",
        "indoor air quality testing"
    ]
}

# Twin Cities priority ZIPs (higher scoring)
PRIORITY_ZIPS = {
    "55406", "55408", "55410", "55416", "55418", "55419",
    "55104", "55105", "55116",
    "55424", "55435",
    "55311", "55347"
}

STATUS_OPTIONS = ["New", "Contacted", "Appointment Set", "Proposal Sent", "Won", "Lost"]

HTML_BASE = """
<!DOCTYPE html>
<html>
<head>
    <title>Twin Cities Restoration Leads — Exclusive</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; max-width: 980px; margin: 40px auto; padding: 20px; background: #f1f5f9; color: #1e293b; }
        .card { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }
        h1 { color: #0f172a; }
        h2 { color: #334155; margin-top: 0; }
        label { display: block; margin: 12px 0 4px; font-weight: 500; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        button, .btn { background: #0ea5e9; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; cursor: pointer; text-decoration: none; display: inline-block; margin-right: 8px; }
        button:hover, .btn:hover { background: #0284c7; }
        .score-high { color: #16a34a; font-weight: bold; }
        .score-med { color: #ca8a04; font-weight: bold; }
        .score-low { color: #dc2626; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 8px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }
        .badge { background: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
        .priority { background: #fef3c7; color: #92400e; }
        .urgent { background: #fee2e2; color: #991b1b; }
        select.status { width: auto; padding: 4px 8px; font-size: 14px; }
    </style>
</head>
<body>
    <h1>Twin Cities Restoration Leads</h1>
    <p>Exclusive water damage, mold, and indoor air quality leads delivered to one primary restoration contractor.</p>
    <nav>
        <a class="btn" href="/">Homeowner / Property Form</a>
        <a class="btn" href="/dashboard" style="background:#059669">Contractor Dashboard</a>
    </nav>
    <hr>
    {{ content|safe }}
</body>
</html>
"""

@app.route("/")
def home():
    form = """
    <div class="card">
        <h2>Request Water Damage, Mold, or Air Quality Help</h2>
        <p>Your request goes exclusively to our primary Twin Cities restoration contractor. They handle the full job and bring in specialists as needed.</p>
        <form method="POST" action="/submit">
            <label>Service Needed *</label>
            <select name="service_type" required>
                <option value="">Select...</option>
                <option value="water_damage">Water Damage Restoration</option>
                <option value="dry_out">Dry Out Services</option>
                <option value="mold_mitigation">Mold Mitigation</option>
                <option value="mold_inspection">Mold Inspection</option>
                <option value="mold_remediation">Mold Remediation</option>
                <option value="iaq_testing">Indoor Air Quality Testing</option>
            </select>

            <label>How urgent is this? *</label>
            <select name="urgency" required>
                <option value="">Select...</option>
                <option value="emergency">Emergency — water is actively damaging the property</option>
                <option value="asap">Need help within 24–48 hours</option>
                <option value="this_week">Within the next week</option>
                <option value="planning">Planning / non-emergency</option>
            </select>

            <label>Property Type *</label>
            <select name="property_type" required>
                <option value="">Select...</option>
                <option value="single_family">Single-family home</option>
                <option value="condo">Condo / Townhome</option>
                <option value="multi_family">Multi-family</option>
                <option value="commercial">Commercial / Office</option>
            </select>

            <label>ZIP Code *</label>
            <input type="text" name="zip" pattern="[0-9]{5}" required placeholder="55406">

            <label>Full Name *</label>
            <input type="text" name="name" required>

            <label>Phone *</label>
            <input type="tel" name="phone" required placeholder="(612) 555-1234">

            <label>Email *</label>
            <input type="email" name="email" required>

            <label>Are you the property owner or decision maker?</label>
            <select name="decision_maker">
                <option value="yes">Yes</option>
                <option value="no">No / Shared decision</option>
            </select>

            <label>Describe the situation (optional but helpful)</label>
            <textarea name="details" rows="4" placeholder="What happened? Where is the water/mold? How long has it been going on?"></textarea>

            <br><br>
            <button type="submit">Submit Request</button>
        </form>
    </div>
    """
    return render_template_string(HTML_BASE, content=form)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.form.to_dict()
    data["id"] = str(uuid.uuid4())[:8]
    data["created"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data["status"] = "New"

    # Scoring tuned for restoration / mold urgency
    score = 35
    urgency_map = {"emergency": 40, "asap": 30, "this_week": 15, "planning": 5}
    score += urgency_map.get(data.get("urgency"), 0)
    if data.get("decision_maker") == "yes":
        score += 10
    if len(data.get("details", "")) > 25:
        score += 8
    if data.get("zip") in PRIORITY_ZIPS:
        score += 10
        data["priority_zip"] = True
    else:
        data["priority_zip"] = False
    # Boost high-value emergency services
    if data.get("service_type") in ("water_damage", "mold_remediation", "dry_out"):
        score += 7
    data["score"] = min(score, 100)

    data["assigned_to"] = PRIMARY_CONTRACTOR["name"]
    data["exclusivity"] = "Exclusive — One Contractor"

    leads.append(data)

    priority_note = " (Priority ZIP)" if data.get("priority_zip") else ""
    urgent_note = " — Marked high urgency" if data.get("urgency") in ("emergency", "asap") else ""
    result = f"""
    <div class="card">
        <h2>Thank You, {data['name']}!</h2>
        <p>Your restoration request has been received and scored.</p>
        <p><strong>Lead Score:</strong> <span class="score-high">{data['score']}/100</span>{priority_note}{urgent_note}</p>
        <p><strong>Assigned To:</strong> {PRIMARY_CONTRACTOR['name']}</p>
        <p><span class="badge">Exclusive to One Contractor</span> — Only our primary Twin Cities restoration company will receive your information. They will contact you quickly and manage the full job.</p>
        <p>A confirmation was sent to {data['email']}.</p>
        <a class="btn" href="/">Submit Another</a>
        <a class="btn" href="/dashboard">View Dashboard</a>
    </div>
    """
    return render_template_string(HTML_BASE, content=result)

@app.route("/update_status", methods=["POST"])
def update_status():
    lead_id = request.form.get("lead_id")
    new_status = request.form.get("status")
    for lead in leads:
        if lead["id"] == lead_id and new_status in STATUS_OPTIONS:
            lead["status"] = new_status
            break
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    rows = ""
    for lead in reversed(leads):
        score_class = "score-high" if lead["score"] >= 75 else ("score-med" if lead["score"] >= 55 else "score-low")
        zip_badge = '<span class="badge priority">Priority ZIP</span>' if lead.get("priority_zip") else ""
        urgency_badge = '<span class="badge urgent">Urgent</span>' if lead.get("urgency") in ("emergency", "asap") else ""
        status_select = f"""
        <form method="POST" action="/update_status" style="display:inline;">
            <input type="hidden" name="lead_id" value="{lead['id']}">
            <select name="status" class="status" onchange="this.form.submit()">
                {''.join(f'<option value="{s}" {"selected" if s == lead["status"] else ""}>{s}</option>' for s in STATUS_OPTIONS)}
            </select>
        </form>
        """
        service_label = lead["service_type"].replace("_", " ").title()
        rows += f"""
        <tr>
            <td>{lead['created']}</td>
            <td>{service_label} {urgency_badge}</td>
            <td>{lead['urgency'].replace('_', ' ').title()}</td>
            <td>{lead['property_type'].replace('_', ' ').title()}</td>
            <td>{lead['zip']} {zip_badge}</td>
            <td class="{score_class}">{lead['score']}</td>
            <td>{lead['name']}<br><small>{lead['phone']}</small></td>
            <td>{status_select}</td>
        </tr>
        """
    if not rows:
        rows = "<tr><td colspan='8'>No leads yet. Submit one from the form.</td></tr>"

    content = f"""
    <div class="card">
        <h2>Primary Contractor Dashboard — {PRIMARY_CONTRACTOR['name']}</h2>
        <p>All leads are exclusive to this single restoration contractor. They manage the job and bring in specialists as needed.</p>
        <p><strong>Services:</strong> Water damage restoration, Dry out, Mold mitigation, Mold inspection, Mold remediation, Indoor air quality testing<br>
           <strong>Service Area:</strong> {PRIMARY_CONTRACTOR['service_area']}</p>
        <table>
            <thead>
                <tr>
                    <th>Received</th>
                    <th>Service</th>
                    <th>Urgency</th>
                    <th>Property</th>
                    <th>ZIP</th>
                    <th>Score</th>
                    <th>Contact</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        <p style="margin-top:16px; font-size:14px; color:#64748b;">Change status via the dropdown (auto-saves). Flow: New → Contacted → Appointment Set → Proposal Sent → Won / Lost.</p>
    </div>
    """
    return render_template_string(HTML_BASE, content=content)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
