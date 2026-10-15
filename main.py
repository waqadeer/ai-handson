import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from app import analyze_pdf_file, analyze_requirements, extract_pdf_text, generate_response, get_documents_dir, list_pdfs_in_documents_dir

app = FastAPI(title="AI Chat App")


tickets = [
    {
        "id": 1,
        "title": "Delayed shipment for customer #1042",
        "customer": "Northwind Logistics",
        "priority": "High",
        "status": "Open",
        "category": "Logistics",
        "assigned_to": "Aisha",
        "sla_hours": 6,
        "description": "Customer reported missing delivery ETA update for a priority shipment.",
    },
    {
        "id": 2,
        "title": "SMS not reaching driver in the field",
        "customer": "Metro Freight",
        "priority": "Medium",
        "status": "In Progress",
        "category": "Communication",
        "assigned_to": "Daniel",
        "sla_hours": 12,
        "description": "Driver teams are not receiving outbound SMS notifications consistently.",
    },
    {
        "id": 3,
        "title": "Need support dashboard summary",
        "customer": "CargoBridge",
        "priority": "Low",
        "status": "Resolved",
        "category": "Reporting",
        "assigned_to": "Sara",
        "sla_hours": 24,
        "description": "Business wants to see response times and backlogs in a summary widget.",
    },
]


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class AnalysisResponse(BaseModel):
    analysis: str


class TicketCreateRequest(BaseModel):
    title: str
    customer: str
    priority: str
    category: str
    description: str
    assigned_to: str | None = None


class TicketUpdateRequest(BaseModel):
    status: str | None = None
    assigned_to: str | None = None
    priority: str | None = None


@app.get("/")
def home() -> HTMLResponse:
    return HTMLResponse(content=r"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Requirements to MVP</title>
        <style>
            :root {
                --bg: #f3f7ff;
                --panel: #ffffff;
                --ink: #0f172a;
                --muted: #475569;
                --primary: #2563eb;
                --primary-dark: #1d4ed8;
                --accent: #0ea5e9;
                --success: #10b981;
                --line: #e2e8f0;
                --shadow: 0 20px 60px rgba(15, 23, 42, 0.12);
            }
            * { box-sizing: border-box; }
            body {
                margin: 0; font-family: Inter, 'Segoe UI', sans-serif; background: linear-gradient(135deg, #eef6ff 0%, #f9fbff 100%);
                color: var(--ink);
            }
            a { text-decoration: none; color: inherit; }
            .nav {
                position: sticky; top: 0; background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(12px); z-index: 20;
                border-bottom: 1px solid rgba(148, 163, 184, 0.2);
            }
            .nav-inner, .container, .section, .pricing {
                max-width: 1180px; margin: 0 auto; padding: 0 24px;
            }
            .nav-inner {
                display: flex; align-items: center; justify-content: space-between; min-height: 76px;
                color: white;
            }
            .brand { font-weight: 800; letter-spacing: 0.04em; }
            .nav-links { display: flex; gap: 18px; align-items: center; color: #dbeafe; }
            .nav-links a { font-size: 0.96rem; }
            .nav-btn, .primary-btn, .secondary-btn {
                display: inline-flex; align-items: center; justify-content: center; border-radius: 12px; padding: 12px 18px; font-weight: 700; cursor: pointer; border: 0;
            }
            .nav-btn, .primary-btn { background: linear-gradient(135deg, var(--primary), var(--accent)); color: white; }
            .secondary-btn { background: white; color: var(--ink); border: 1px solid var(--line); }
            .hero {
                padding: 72px 0 48px;
            }
            .hero-grid {
                display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 32px; align-items: center;
            }
            .eyebrow {
                display: inline-block; background: rgba(37, 99, 235, 0.1); color: var(--primary); border-radius: 999px; padding: 8px 12px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;
            }
            h1 {
                font-size: clamp(2.5rem, 5vw, 4.3rem); line-height: 1.04; margin: 18px 0 18px;
            }
            .lead {
                font-size: 1.12rem; line-height: 1.7; max-width: 620px; color: var(--muted);
            }
            .cta-row { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 28px; }
            .highlight-card {
                background: var(--panel); border-radius: 22px; box-shadow: var(--shadow); padding: 26px; border: 1px solid rgba(148, 163, 184, 0.2);
            }
            .mini-stats { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 12px; margin-top: 18px; }
            .mini-stat { background: #f8fafc; border: 1px solid var(--line); border-radius: 14px; padding: 16px; }
            .mini-stat strong { display: block; font-size: 1.4rem; }
            .section { padding: 50px 0; }
            .section-title { font-size: clamp(1.8rem, 3vw, 2.7rem); margin-bottom: 14px; }
            .grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 20px; }
            .feature-box, .step-box, .price-card {
                background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 24px; box-shadow: 0 12px 24px rgba(15,23,42,0.03);
            }
            .feature-box h3, .step-box h3, .price-card h3 { margin-top: 0; }
            .feature-box p, .step-box p, .price-card p { color: var(--muted); line-height: 1.6; }
            .badge-row { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
            .badge { display: inline-block; background: #eef2ff; color: #3730a3; border-radius: 999px; padding: 7px 10px; font-size: 0.74rem; font-weight: 700; }
            .demo-panel {
                background: linear-gradient(135deg, #111827 0%, #1f2937 100%); color: white; border-radius: 24px; padding: 28px; box-shadow: var(--shadow);
            }
            .upload-box {
                display: flex; flex-wrap: wrap; gap: 12px; margin: 20px 0 14px;
            }
            input[type="file"] { flex: 1; min-width: 220px; padding: 12px 14px; border: 1px solid rgba(148,163,184,0.5); border-radius: 12px; background: rgba(255,255,255,0.05); color: white; }
            .result-box {
                margin-top: 20px; background: rgba(15,23,42,0.48); border: 1px solid rgba(148,163,184,0.25); border-radius: 16px; padding: 18px; min-height: 120px; white-space: pre-wrap; word-break: break-word; color: #e2e8f0;
            }
            .status { margin-top: 8px; color: #cbd5e1; font-size: 0.95rem; }
            .pricing { padding-bottom: 80px; }
            .pricing-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 22px; }
            .price-card.featured { border: 1px solid rgba(37,99,235,0.5); background: linear-gradient(180deg, #eff6ff, #ffffff); }
            .price-card .price { font-size: 2.1rem; font-weight: 800; margin: 12px 0 0; }
            .price-card ul { padding-left: 18px; color: var(--muted); line-height: 1.9; }
            .footer { text-align: center; color: var(--muted); padding: 24px 0 48px; }
            @media (max-width: 900px) {
                .hero-grid, .grid-3, .pricing-grid { grid-template-columns: 1fr; }
                .nav-links { display: none; }
            }
        </style>
    </head>
    <body>
        <div class="nav">
            <div class="nav-inner">
                <div class="brand">AI HANDSON</div>
                <div class="nav-links">
                    <a href="#process">Process</a>
                    <a href="#features">Features</a>
                    <a href="#pricing">Pricing</a>
                    <a href="/mvp">Demo</a>
                </div>
                <a class="nav-btn" href="/proposal">View Proposal</a>
            </div>
        </div>

        <main>
            <section class="hero">
                <div class="container hero-grid">
                    <div>
                        <span class="eyebrow">Requirements → Product</span>
                        <h1>Turn a document into a working MVP in minutes.</h1>
                        <p class="lead">Upload a requirement document and turn it into an actionable business app plan, feature breakdown, and a demo-ready MVP dashboard for stakeholder review.</p>
                        <div class="cta-row">
                            <a class="primary-btn" href="/proposal">See client proposal</a>
                            <a class="secondary-btn" href="/mvp">Open demo</a>
                        </div>
                        <div class="mini-stats">
                            <div class="mini-stat"><strong>3x</strong> faster discovery</div>
                            <div class="mini-stat"><strong>1</strong> workflow</div>
                            <div class="mini-stat"><strong>24/7</strong> analysis</div>
                        </div>
                    </div>
                    <div class="highlight-card">
                        <h3>What this product does</h3>
                        <p>Reads PDFs, identifies the business problem, extracts core requirements, and maps them into an app skeleton, ticketing flow, and deployment plan.</p>
                        <div class="badge-row">
                            <span class="badge">PDF Analysis</span>
                            <span class="badge">App Blueprint</span>
                            <span class="badge">MVP Demo</span>
                            <span class="badge">Ops Dashboard</span>
                        </div>
                    </div>
                </div>
            </section>

            <section id="process" class="section">
                <div class="container">
                    <h2 class="section-title">The AI workflow</h2>
                    <div class="grid-3">
                        <div class="step-box">
                            <h3>1. Upload</h3>
                            <p>Drop in a business requirements PDF, spec, or rough document from a client.</p>
                        </div>
                        <div class="step-box">
                            <h3>2. Analyze</h3>
                            <p>The AI identifies the problem, app type, features, and technology stack.</p>
                        </div>
                        <div class="step-box">
                            <h3>3. Deliver</h3>
                            <p>Present a working MVP, proposal, and next-step roadmap for stakeholders.</p>
                        </div>
                    </div>
                </div>
            </section>

            <section id="features" class="section">
                <div class="container">
                    <h2 class="section-title">Built for real client work</h2>
                    <div class="grid-3">
                        <div class="feature-box">
                            <h3>Business-ready intelligence</h3>
                            <p>Reads raw requirement language and packages it into a deliverable that business users can understand.</p>
                        </div>
                        <div class="feature-box">
                            <h3>Operational workflow</h3>
                            <p>Turns requirements into dashboards, tickets, and dashboards used by operations teams.</p>
                        </div>
                        <div class="feature-box">
                            <h3>Faster sales cycle</h3>
                            <p>Replaces long document review loops with an instant proposal and product preview.</p>
                        </div>
                    </div>
                </div>
            </section>

            <section class="section">
                <div class="container demo-panel">
                    <h2 style="margin-top:0;">Upload your requirement document</h2>
                    <p>Works with any PDF requirement document, from logistics, healthcare, fintech, or operations workflows.</p>
                    <div class="upload-box">
                        <input type="file" id="pdfFile" accept="application/pdf" />
                        <button class="primary-btn" id="analyzeBtn" style="border:0;">Analyze document</button>
                    </div>
                    <div class="status" id="status">No file selected yet.</div>
                    <pre class="result-box" id="result">Waiting for analysis...</pre>
                </div>
            </section>

            <section id="pricing" class="pricing">
                <div class="container">
                    <h2 class="section-title">Simple pricing model</h2>
                    <div class="pricing-grid">
                        <div class="price-card">
                            <h3>Starter</h3>
                            <p>For founders validating concepts.</p>
                            <div class="price">$299</div>
                            <ul>
                                <li>1 project discovery flow</li>
                                <li>AI requirement review</li>
                                <li>Basic MVP dashboard</li>
                            </ul>
                        </div>
                        <div class="price-card featured">
                            <h3>Growth</h3>
                            <p>For teams building client demos.</p>
                            <div class="price">$799</div>
                            <ul>
                                <li>Unlimited analysis runs</li>
                                <li>Proposal generation</li>
                                <li>Ops workflow dashboard</li>
                            </ul>
                        </div>
                        <div class="price-card">
                            <h3>Retainer</h3>
                            <p>For ongoing product iteration.</p>
                            <div class="price">Custom</div>
                            <ul>
                                <li>Monthly optimization</li>
                                <li>Feature roadmap</li>
                                <li>Priority deploy support</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>
        </main>

        <footer class="footer">Requirements-to-MVP AI workflow · Built to impress clients and accelerate product thinking</footer>

        <script>
            const analyzeBtn = document.getElementById('analyzeBtn');
            const pdfFile = document.getElementById('pdfFile');
            const result = document.getElementById('result');
            const status = document.getElementById('status');

            function parseAnalysisText(raw) {
                let cleaned = raw.trim();
                if (cleaned.startsWith('```')) {
                    cleaned = cleaned.replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/, '');
                }
                return JSON.parse(cleaned);
            }

            analyzeBtn.addEventListener('click', async () => {
                const file = pdfFile.files[0];
                if (!file) {
                    status.textContent = 'Please select a PDF file first.';
                    return;
                }

                status.textContent = 'Analyzing document...';
                result.textContent = 'Working...';

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        body: formData,
                    });

                    const data = await response.json();
                    if (!response.ok) {
                        throw new Error(data.detail || 'Request failed');
                    }

                    status.textContent = 'Analysis complete.';
                    const analysis = parseAnalysisText(data.analysis);
                    result.textContent = JSON.stringify(analysis, null, 2);
                } catch (error) {
                    status.textContent = 'Something went wrong.';
                    result.textContent = error.message;
                }
            });
        </script>
    </body>
    </html>
    """)


@app.get("/proposal")
def proposal_page() -> HTMLResponse:
    return HTMLResponse(content=r"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Client Proposal</title>
        <style>
            body { margin: 0; font-family: Inter, 'Segoe UI', sans-serif; background: #f8fafc; color: #0f172a; }
            .container { max-width: 1100px; margin: 0 auto; padding: 32px 24px 80px; }
            .topbar { display: flex; justify-content: space-between; align-items: center; padding: 18px 24px; background: #0f172a; color: white; }
            .topbar a { color: white; text-decoration: none; font-weight: 700; }
            .hero { background: linear-gradient(135deg, #dbeafe, #eff6ff); border-radius: 20px; padding: 28px; margin-bottom: 24px; border: 1px solid #cfe0ff; }
            .grid { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 24px; }
            .card { background: white; border: 1px solid #e2e8f0; border-radius: 18px; padding: 22px; box-shadow: 0 8px 24px rgba(15,23,42,0.04); }
            .summary { font-size: 1.04rem; line-height: 1.8; color: #334155; }
            .pill { display: inline-block; background: #dbeafe; color: #1d4ed8; border-radius: 999px; padding: 7px 10px; font-size: 0.74rem; font-weight: 800; letter-spacing: 0.05em; text-transform: uppercase; }
            h1 { margin: 12px 0 10px; font-size: clamp(2.2rem, 4vw, 3.2rem); }
            .list { margin: 0; padding-left: 18px; color: #334155; line-height: 1.8; }
            .status { color: #0f766e; font-weight: 700; }
            .spinner { font-size: 0.9rem; color: #475569; }
            .section-title { margin: 0 0 12px; font-size: 1.4rem; }
            @media (max-width: 820px) { .grid { grid-template-columns: 1fr; } }
        </style>
    </head>
    <body>
        <div class="topbar">
            <div><strong>AI Requirements Proposal</strong></div>
            <a href="/">Back to home</a>
        </div>

        <div class="container">
            <div class="hero">
                <span class="pill">Client-ready blueprint</span>
                <h1>Business transformation proposal</h1>
                <p class="summary">This proposal summarizes the requirements captured from the uploaded document, converts them into an MVP direction, and frames the recommended product architecture for stakeholder review.</p>
            </div>

            <div class="grid">
                <div class="card">
                    <div class="section-title">AI-generated summary</div>
                    <div id="summary" class="summary">Loading summary...</div>
                </div>
                <div class="card">
                    <div class="section-title">Project status</div>
                    <p class="status">Requirements validated</p>
                    <p class="spinner" id="statusText">Analyzing the latest document...</p>
                </div>
            </div>

            <div style="height: 20px;"></div>

            <div class="card">
                <div class="section-title">Detailed proposal</div>
                <div id="proposalContent" class="summary">Loading proposal details...</div>
            </div>
        </div>

        <script>
            function parseAnalysisObject(raw) {
                if (!raw) return {};
                if (typeof raw === 'object') return raw;

                const cleaned = String(raw).trim();
                if (!cleaned) return {};

                try {
                    return JSON.parse(cleaned.replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/, ''));
                } catch (error) {
                    return {};
                }
            }

            function normalizeList(value) {
                if (Array.isArray(value)) {
                    return value.map(item => String(item).trim()).filter(Boolean);
                }
                if (typeof value === 'string') {
                    return value.split(/\n|\||•|,\s*/).map(item => item.trim()).filter(Boolean);
                }
                if (value && typeof value === 'object') {
                    return Object.values(value).map(item => String(item).trim()).filter(Boolean);
                }
                return [];
            }

            async function loadProposal() {
                const statusText = document.getElementById('statusText');
                const summaryEl = document.getElementById('summary');
                const contentEl = document.getElementById('proposalContent');

                try {
                    const response = await fetch('/analyze-docs', { method: 'POST' });
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || 'Failed to load analysis');

                    const analysis = parseAnalysisObject(data.analysis);
                    const inferredType = analysis.inferred_app_type || analysis.infected_app_type || analysis.app_type || 'Not specified';
                    const features = normalizeList(analysis.key_features);
                    const stack = normalizeList(analysis.recommended_stack || analysis.stack || []);
                    const integrations = normalizeList(analysis.integrations);
                    const deployment = normalizeList(analysis.deployment_plan || []);

                    statusText.textContent = 'Requirements mapped to app strategy';
                    summaryEl.innerHTML = `<strong>App type:</strong> ${inferredType}<br><br>${analysis.summary || 'Summary unavailable'}`;

                    contentEl.innerHTML = `
                        <h3>Recommended feature set</h3>
                        <ul class="list">${features.length ? features.map(item => `<li>${item}</li>`).join('') : '<li>Feature list not available</li>'}</ul>
                        <h3>Technology stack</h3>
                        <ul class="list">${stack.length ? stack.map(item => `<li>${item}</li>`).join('') : '<li>Stack not available</li>'}</ul>
                        <h3>Integrations</h3>
                        <ul class="list">${integrations.length ? integrations.map(item => `<li>${item}</li>`).join('') : '<li>No extra integrations specified</li>'}</ul>
                        <h3>Deployment plan</h3>
                        <ul class="list">${deployment.length ? deployment.map(item => `<li>${item}</li>`).join('') : '<li>Deployment plan not available</li>'}</ul>
                    `;
                } catch (error) {
                    statusText.textContent = 'No PDF was found yet';
                    summaryEl.textContent = 'Upload a PDF into ~/Documents/AI Handson or use the analyzer above to generate a proposal.';
                    contentEl.textContent = error.message;
                }
            }

            loadProposal();
        </script>
    </body>
    </html>
    """)


@app.get("/mvp")
def mvp_page() -> HTMLResponse:
    return HTMLResponse(content=r"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Logistics Support MVP</title>
        <style>
            body { font-family: Arial, sans-serif; background: #eef6ff; margin: 0; color: #111827; }
            .topbar { display: flex; justify-content: space-between; align-items: center; background: #0f172a; color: white; padding: 14px 24px; gap: 16px; }
            .topbar-actions { display: flex; align-items: center; gap: 12px; }
            .topbar-btn, .home-link {
                display: inline-flex; align-items: center; justify-content: center; border-radius: 10px; padding: 9px 14px; font-weight: 700; text-decoration: none; cursor: pointer; border: 1px solid rgba(148,163,184,0.4);
            }
            .topbar-btn { background: #1e293b; color: white; }
            .home-link { background: #e0f2fe; color: #0f172a; border-color: #bae6fd; }
            .hidden { display: none !important; }
            .wrap { max-width: 1200px; margin: 0 auto; padding: 24px; }
            .login-panel { max-width: 420px; margin: 40px auto; background: white; border-radius: 18px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); }
            .field { display: flex; flex-direction: column; margin-bottom: 16px; }
            input, select { padding: 10px 12px; border-radius: 10px; border: 1px solid #cbd5e1; }
            button { background: #2563eb; color: white; border: none; border-radius: 10px; padding: 11px 16px; cursor: pointer; }
            .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin: 20px 0; }
            .card { background: white; border-radius: 12px; padding: 18px; box-shadow: 0 8px 20px rgba(0,0,0,0.05); }
            .ticket-list { margin-top: 24px; background: white; border-radius: 12px; padding: 18px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: left; }
            .badge { display: inline-block; padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: bold; }
            .high { background: #fee2e2; color: #991b1b; }
            .medium { background: #fef3c7; color: #92400e; }
            .low { background: #dcfce7; color: #166534; }
            .hidden { display: none; }
        </style>
    </head>
    <body>
        <div class="topbar">
            <div><strong>Logistics Support Hub</strong></div>
            <div class="topbar-actions">
                <div id="userBadge">Demo Mode</div>
                <a class="home-link" href="/">Home</a>
                <button id="logoutBtn" class="topbar-btn hidden" type="button">Log out</button>
            </div>
        </div>

        <div class="wrap">
            <div id="loginView" class="login-panel">
                <h2>Operations Login</h2>
                <div class="field">
                    <label>Email</label>
                    <input id="email" type="email" value="ops@demo.com" />
                </div>
                <div class="field">
                    <label>Password</label>
                    <input id="password" type="password" value="demo123" />
                </div>
                <button id="loginBtn">Sign In</button>
            </div>

            <div id="dashboardView" class="hidden">
                <div class="cards">
                    <div class="card">
                        <div>Total Tickets</div>
                        <h2 id="totalTickets">0</h2>
                    </div>
                    <div class="card">
                        <div>Open</div>
                        <h2 id="openTickets">0</h2>
                    </div>
                    <div class="card">
                        <div>In Progress</div>
                        <h2 id="inProgressTickets">0</h2>
                    </div>
                    <div class="card">
                        <div>Resolved</div>
                        <h2 id="resolvedTickets">0</h2>
                    </div>
                </div>

                <div class="ticket-list">
                    <h3>Customer Support Tickets</h3>
                    <form id="ticketForm" style="margin-bottom:20px; display:flex; gap:10px; flex-wrap:wrap;">
                        <input name="title" placeholder="Ticket title" required />
                        <input name="customer" placeholder="Customer" required />
                        <select name="priority">
                            <option>High</option>
                            <option selected>Medium</option>
                            <option>Low</option>
                        </select>
                        <select name="category">
                            <option>Logistics</option>
                            <option>Communication</option>
                            <option>Reporting</option>
                        </select>
                        <input name="assigned_to" placeholder="Assigned to" />
                        <button type="submit">Add Ticket</button>
                    </form>

                    <table>
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Customer</th>
                                <th>Priority</th>
                                <th>Status</th>
                                <th>Assigned To</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="ticketTableBody"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            const loginView = document.getElementById('loginView');
            const dashboardView = document.getElementById('dashboardView');
            const userBadge = document.getElementById('userBadge');
            const ticketTableBody = document.getElementById('ticketTableBody');
            const logoutBtn = document.getElementById('logoutBtn');

            function setAuthenticated(isAuthenticated) {
                loginView.classList.toggle('hidden', isAuthenticated);
                dashboardView.classList.toggle('hidden', !isAuthenticated);
                userBadge.textContent = isAuthenticated ? 'Logged in as Ops' : 'Demo Mode';
                logoutBtn.classList.toggle('hidden', !isAuthenticated);
            }

            async function loadTickets() {
                const response = await fetch('/api/tickets');
                const tickets = await response.json();

                ticketTableBody.innerHTML = tickets.map(ticket => `
                    <tr>
                        <td>${ticket.title}</td>
                        <td>${ticket.customer}</td>
                        <td><span class="badge ${ticket.priority.toLowerCase()}">${ticket.priority}</span></td>
                        <td>${ticket.status}</td>
                        <td>${ticket.assigned_to || 'Unassigned'}</td>
                        <td>
                            <select data-id="${ticket.id}" class="statusSelect">
                                <option ${ticket.status === 'Open' ? 'selected' : ''}>Open</option>
                                <option ${ticket.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                                <option ${ticket.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
                            </select>
                        </td>
                    </tr>
                `).join('');

                document.getElementById('totalTickets').textContent = tickets.length;
                document.getElementById('openTickets').textContent = tickets.filter(t => t.status === 'Open').length;
                document.getElementById('inProgressTickets').textContent = tickets.filter(t => t.status === 'In Progress').length;
                document.getElementById('resolvedTickets').textContent = tickets.filter(t => t.status === 'Resolved').length;

                document.querySelectorAll('.statusSelect').forEach(select => {
                    select.addEventListener('change', async (event) => {
                        const id = event.target.dataset.id;
                        await fetch(`/api/tickets/${id}`, {
                            method: 'PATCH',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ status: event.target.value })
                        });
                        loadTickets();
                    });
                });
            }

            document.getElementById('loginBtn').addEventListener('click', () => {
                setAuthenticated(true);
                loadTickets();
            });

            document.getElementById('logoutBtn').addEventListener('click', () => {
                setAuthenticated(false);
                window.location.href = '/';
            });

            setAuthenticated(false);

            document.getElementById('ticketForm').addEventListener('submit', async (event) => {
                event.preventDefault();
                const form = new FormData(event.target);
                const payload = {
                    title: form.get('title'),
                    customer: form.get('customer'),
                    priority: form.get('priority'),
                    category: form.get('category'),
                    assigned_to: form.get('assigned_to') || 'Unassigned',
                    description: 'Created from operations dashboard'
                };

                await fetch('/api/tickets', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                event.target.reset();
                loadTickets();
            });
        </script>
    </body>
    </html>
    """)


@app.get("/documents")
def documents() -> dict[str, object]:
    docs_dir = get_documents_dir()
    return {
        "documents_dir": str(docs_dir),
        "files": list_pdfs_in_documents_dir(),
    }


@app.get("/api/tickets")
def get_all_tickets() -> list[dict]:
    return tickets


@app.post("/api/tickets")
def create_ticket(payload: TicketCreateRequest) -> dict:
    new_ticket = {
        "id": max((t["id"] for t in tickets), default=0) + 1,
        "title": payload.title,
        "customer": payload.customer,
        "priority": payload.priority,
        "status": "Open",
        "category": payload.category,
        "assigned_to": payload.assigned_to or "Unassigned",
        "sla_hours": 12,
        "description": payload.description,
    }
    tickets.append(new_ticket)
    return new_ticket


@app.patch("/api/tickets/{ticket_id}")
def update_ticket(ticket_id: int, payload: TicketUpdateRequest) -> dict:
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            if payload.status is not None:
                ticket["status"] = payload.status
            if payload.assigned_to is not None:
                ticket["assigned_to"] = payload.assigned_to
            if payload.priority is not None:
                ticket["priority"] = payload.priority
            return ticket
    raise HTTPException(status_code=404, detail="Ticket not found")


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    reply = generate_response(request.message)
    return ChatResponse(reply=reply)


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(file: UploadFile = File(...)) -> AnalysisResponse:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        temp_path = tmp_file.name

    try:
        analysis = analyze_pdf_file(temp_path)
        return AnalysisResponse(analysis=analysis)
    finally:
        os.unlink(temp_path)


@app.post("/analyze-docs", response_model=AnalysisResponse)
def analyze_from_documents_folder() -> AnalysisResponse:
    pdf_files = list_pdfs_in_documents_dir()
    if not pdf_files:
        raise HTTPException(status_code=404, detail="No PDF files found in ~/Documents/AI Handson")

    pdf_path = str(get_documents_dir() / pdf_files[0])
    analysis = analyze_pdf_file(pdf_path)
    return AnalysisResponse(analysis=analysis)
