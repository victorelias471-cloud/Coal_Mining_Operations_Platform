from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from password_security import analyze_password
# MineCore Policy Knowledge Base
POLICY_KNOWLEDGE = [
    {
        "topic": "PPE",
        "content": "All personnel working in mining operations must use appropriate personal protective equipment (PPE). PPE helps protect workers from hazards associated with mining activities.",
        "source": "Worker Safety Manual — PPE Safety"
    },
    {
        "topic": "Equipment Inspection",
        "content": "Mining equipment should be inspected before operation to identify defects or unsafe conditions. Equipment with safety concerns should not be operated until the issue is addressed.",
        "source": "Equipment Safety Guidelines — Inspection"
    },
    {
        "topic": "Heavy Equipment",
        "content": "Personnel should maintain a safe distance from operating heavy equipment and remain aware of equipment movement and designated safety zones.",
        "source": "Worker Safety Manual — Heavy Equipment Safety"
    },
    {
        "topic": "Training",
        "content": "Only trained and authorized personnel should operate mining equipment. Workers should receive appropriate safety training before performing hazardous mining activities.",
        "source": "Company Mining Procedures — Personnel Training"
    },
    {
        "topic": "Environmental Monitoring",
        "content": "Mining operations should include environmental monitoring and appropriate measures to reduce environmental impacts during mining and reclamation activities.",
        "source": "Environmental Policy — Monitoring and Reclamation"
    }
]
app = FastAPI(
    title="MineCore",
    description="Mining Operations Management Platform",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


class Equipment(BaseModel):
    name: str = Field(..., example="Excavator")
    status: str = Field(..., example="Operational")


class MiningStage(BaseModel):
    id: int
    name: str
    status: str
    description: str
    safety_requirements: List[str]
    equipment: Optional[List[Equipment]] = None


class MiningSite(BaseModel):
    id: int
    name: str
    location: str
    current_stage_id: int
    production_status: str
    safety_status: str
    production_today: int


class Alert(BaseModel):
    id: int
    site_id: int
    severity: str
    message: str
    status: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
class PasswordRequest(BaseModel):
    password: str = Field(..., min_length=1)

mining_stages = [
    {
        "id": 1,
        "name": "Exploration",
        "status": "Completed",
        "description": "Survey and assessment of the proposed mining area.",
        "safety_requirements": [
            "Conduct geological assessment",
            "Identify potential hazards",
            "Assess environmental risks"
        ]
    },
    {
        "id": 2,
        "name": "Site Planning",
        "status": "Completed",
        "description": "Planning of access routes, work areas and equipment.",
        "safety_requirements": [
            "Assess access routes",
            "Plan emergency access",
            "Identify operational hazards"
        ]
    },
    {
        "id": 3,
        "name": "Mine Development",
        "status": "Completed",
        "description": "Preparation and development of the mining site.",
        "safety_requirements": [
            "Inspect work areas",
            "Verify safety equipment",
            "Confirm emergency procedures",
            "Ensure workers are trained"
        ]
    },
    {
        "id": 4,
        "name": "Extraction",
        "status": "Active",
        "description": "Extraction of coal from the mining area.",
        "equipment": [
            {
                "name": "Excavator",
                "status": "Operational"
            },
            {
                "name": "Haul Truck",
                "status": "Operational"
            }
        ],
        "safety_requirements": [
            "Complete site inspection",
            "Inspect equipment before operation",
            "Use required PPE",
            "Allow only trained personnel",
            "Maintain safe distance from heavy equipment"
        ]
    },
    {
        "id": 5,
        "name": "Coal Processing",
        "status": "Pending",
        "description": "Processing and preparation of extracted coal.",
        "safety_requirements": [
            "Follow equipment operating procedures",
            "Report equipment faults",
            "Follow safety instructions"
        ]
    },
    {
        "id": 6,
        "name": "Transportation",
        "status": "Pending",
        "description": "Transportation of coal using approved routes and vehicles.",
        "safety_requirements": [
            "Complete vehicle inspection",
            "Follow site speed limits",
            "Use approved transportation routes",
            "Report vehicle defects"
        ]
    },
    {
        "id": 7,
        "name": "Storage / Distribution",
        "status": "Pending",
        "description": "Storage and distribution of coal.",
        "safety_requirements": [
            "Control access to storage areas",
            "Monitor storage conditions",
            "Maintain emergency arrangements"
        ]
    },
    {
        "id": 8,
        "name": "Environmental Monitoring & Reclamation",
        "status": "Pending",
        "description": "Monitoring environmental impact and restoring affected areas.",
        "safety_requirements": [
            "Monitor air quality",
            "Monitor water quality",
            "Monitor dust and noise",
            "Manage waste appropriately",
            "Assess land disturbance"
        ]
    }
]


mining_sites = [
    {
        "id": 1,
        "name": "Site A",
        "location": "Mining Zone A",
        "current_stage_id": 4,
        "production_status": "Active",
        "safety_status": "Good",
        "production_today": 1250
    },
    {
        "id": 2,
        "name": "Site B",
        "location": "Mining Zone B",
        "current_stage_id": 4,
        "production_status": "Active",
        "safety_status": "Warning",
        "production_today": 980
    },
    {
        "id": 3,
        "name": "Site C",
        "location": "Mining Zone C",
        "current_stage_id": 5,
        "production_status": "Processing",
        "safety_status": "Good",
        "production_today": 760
    },
    {
        "id": 4,
        "name": "Site D",
        "location": "Mining Zone D",
        "current_stage_id": 6,
        "production_status": "Transportation",
        "safety_status": "Good",
        "production_today": 1120
    }
]


alerts = [
    {
        "id": 1,
        "site_id": 1,
        "severity": "Medium",
        "message": "Excavator inspection is due.",
        "status": "Open"
    },
    {
        "id": 2,
        "site_id": 1,
        "severity": "Low",
        "message": "PPE compliance review is scheduled.",
        "status": "Open"
    }
]


def find_site(site_id: int):
    return next(
        (site for site in mining_sites if site["id"] == site_id),
        None
    )


def find_stage(stage_id: int):
    return next(
        (stage for stage in mining_stages if stage["id"] == stage_id),
        None
    )


@app.get("/", response_class=HTMLResponse)
def home_page():
    total_production = sum(
        site["production_today"]
        for site in mining_sites
    )

    active_sites = sum(
        1
        for site in mining_sites
        if site["production_status"] == "Active"
    )

    open_alerts = sum(
        1
        for alert in alerts
        if alert["status"] == "Open"
    )

    total_equipment = sum(
        len(stage.get("equipment", []))
        for stage in mining_stages
    )

    operational_equipment = sum(
        1
        for stage in mining_stages
        for equipment in stage.get("equipment", [])
        if equipment["status"].lower() == "operational"
    )

    equipment_percentage = (
        round(operational_equipment / total_equipment * 100)
        if total_equipment
        else 0
    )

    site_cards = ""

    for site in mining_sites:
        stage = find_stage(site["current_stage_id"])

        safety_class = (
            "good"
            if site["safety_status"].lower() == "good"
            else "warning"
        )

        status_class = (
            "active"
            if site["production_status"].lower() == "active"
            else "processing"
        )

        progress = {
            "Active": 82,
            "Processing": 58,
            "Transportation": 72
        }.get(site["production_status"], 50)

        site_cards += f"""
        <article class="site-card">
            <div class="site-card-header">
                <div>
                    <div class="site-name">{site["name"]}</div>
                    <div class="site-location">{site["location"]}</div>
                </div>

                <span class="status-badge {safety_class}">
                    {site["safety_status"]}
                </span>
            </div>

            <div class="site-stage">
                <span class="stage-dot {status_class}"></span>
                {stage["name"] if stage else "Unknown Stage"}
            </div>

            <div class="production-row">
                <div>
                    <span class="muted">Production today</span>
                    <strong>{site["production_today"]:,} tons</strong>
                </div>

                <div class="production-status">
                    {site["production_status"]}
                </div>
            </div>

            <div class="progress-track">
                <div
                    class="progress-fill"
                    style="width:{progress}%"
                ></div>
            </div>

            <div class="progress-label">
                <span>Operational progress</span>
                <span>{progress}%</span>
            </div>

            <a
                class="site-link"
                href="/api/dashboard/{site["id"]}"
            >
                View site data →
            </a>
        </article>
        """

    stage_rows = ""

    for stage in mining_stages:
        if stage["status"] == "Active":
            stage_class = "active"
        elif stage["status"] == "Completed":
            stage_class = "completed"
        else:
            stage_class = "pending"

        stage_rows += f"""
        <div class="lifecycle-item">
            <div class="lifecycle-number {stage_class}">
                {stage["id"]:02d}
            </div>

            <div class="lifecycle-content">
                <div class="lifecycle-name">
                    {stage["name"]}
                </div>

                <div class="lifecycle-status">
                    {stage["status"]}
                </div>
            </div>
        </div>
        """

    alert_rows = ""

    for alert in alerts:
        severity_class = alert["severity"].lower()

        site = find_site(alert["site_id"])
        site_name = site["name"] if site else "Unknown Site"

        alert_rows += f"""
        <div class="alert-card">
            <div class="alert-symbol {severity_class}">
                !
            </div>

            <div class="alert-content">
                <div class="alert-message">
                    {alert["message"]}
                </div>

                <div class="alert-meta">
                    {alert["severity"]} · {site_name} · {alert["status"]}
                </div>
            </div>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta
    name="description"
    content="MineCore Mining Operations Management Platform"
>
<title>MineCore | Mining Operations</title>

<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html {{
    scroll-behavior: smooth;
}}

body {{
    font-family: Inter, ui-sans-serif, system-ui, -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #06100c;
    color: #ffffff;
    line-height: 1.5;
}}

a {{
    color: inherit;
}}

.hero {{
    min-height: 720px;
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(
            90deg,
            rgba(3, 12, 9, .97) 0%,
            rgba(3, 12, 9, .90) 40%,
            rgba(3, 12, 9, .45) 100%
        ),
        linear-gradient(
            180deg,
            rgba(0, 0, 0, .05),
            rgba(0, 0, 0, .75)
        ),
        url("https://images.unsplash.com/photo-1578604667557-6b7b9c4e8b91?auto=format&fit=crop&w=2200&q=85");
    background-size: cover;
    background-position: center;
}}

.navbar {{
    height: 86px;
    padding: 0 6%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    z-index: 5;
    border-bottom: 1px solid rgba(255,255,255,.08);
    background: rgba(3,12,9,.18);
    backdrop-filter: blur(12px);
}}

.logo {{
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -.5px;
    text-decoration: none;
}}

.logo-mark {{
    width: 40px;
    height: 40px;
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1766ff, #0a4cd1);
    box-shadow: 0 8px 30px rgba(13,91,255,.3);
}}

.logo-name span {{
    color: #6197ff;
}}

.nav-links {{
    display: flex;
    align-items: center;
    gap: 32px;
}}

.nav-links a {{
    color: rgba(255,255,255,.72);
    text-decoration: none;
    font-size: 13px;
    transition: .2s;
}}

.nav-links a:hover {{
    color: white;
}}

.nav-cta {{
    text-decoration: none;
    border: 1px solid rgba(255,255,255,.25);
    background: rgba(255,255,255,.06);
    padding: 10px 18px;
    border-radius: 24px;
    font-size: 13px;
    transition: .2s;
}}

.nav-cta:hover {{
    background: white;
    color: #07110d;
}}

.hero-content {{
    max-width: 1240px;
    margin: auto;
    padding: 115px 6% 150px;
    position: relative;
    z-index: 2;
}}

.eyebrow {{
    display: flex;
    align-items: center;
    gap: 9px;
    color: #72a4ff;
    text-transform: uppercase;
    letter-spacing: 1.7px;
    font-size: 11px;
    font-weight: 800;
    margin-bottom: 22px;
}}

.eyebrow-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #4388ff;
    box-shadow: 0 0 14px #4388ff;
}}

.hero h1 {{
    max-width: 820px;
    font-size: clamp(50px, 7vw, 88px);
    line-height: .97;
    letter-spacing: -4px;
    font-weight: 780;
    margin-bottom: 28px;
}}

.hero h1 span {{
    color: #4d8cff;
}}

.hero-text {{
    max-width: 620px;
    color: rgba(255,255,255,.68);
    font-size: 17px;
    line-height: 1.75;
    margin-bottom: 36px;
}}

.hero-buttons {{
    display: flex;
    gap: 13px;
    flex-wrap: wrap;
}}

.button-primary {{
    text-decoration: none;
    background: #0c5cff;
    padding: 15px 23px;
    border-radius: 30px;
    font-size: 14px;
    font-weight: 700;
    box-shadow: 0 15px 35px rgba(12,92,255,.25);
    transition: .25s;
}}

.button-primary:hover {{
    background: #2872ff;
    transform: translateY(-2px);
}}

.button-secondary {{
    text-decoration: none;
    border: 1px solid rgba(255,255,255,.27);
    background: rgba(255,255,255,.06);
    padding: 14px 23px;
    border-radius: 30px;
    font-size: 14px;
    font-weight: 600;
    transition: .25s;
}}

.button-secondary:hover {{
    background: rgba(255,255,255,.13);
}}

.stats-wrapper {{
    padding: 0 6%;
    position: relative;
    margin-top: -72px;
    z-index: 10;
}}

.stats {{
    max-width: 1200px;
    margin: auto;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    overflow: hidden;
    border-radius: 20px;
    background: rgba(11,29,22,.92);
    border: 1px solid rgba(255,255,255,.09);
    box-shadow: 0 30px 80px rgba(0,0,0,.3);
    backdrop-filter: blur(20px);
}}

.stat {{
    padding: 28px;
    border-right: 1px solid rgba(255,255,255,.07);
}}

.stat:last-child {{
    border-right: none;
}}

.stat-label {{
    color: #70837a;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    font-weight: 700;
    margin-bottom: 9px;
}}

.stat-value {{
    font-size: 29px;
    font-weight: 760;
    letter-spacing: -1px;
}}

.blue {{
    color: #6098ff;
}}

.green {{
    color: #4fd99b;
}}

.orange {{
    color: #ffb653;
}}

.section {{
    max-width: 1200px;
    margin: auto;
    padding: 105px 6%;
}}

.section-header {{
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 35px;
    margin-bottom: 38px;
}}

.section-label {{
    color: #5b96ff;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 10px;
}}

.section-title {{
    font-size: 40px;
    line-height: 1.1;
    letter-spacing: -1.8px;
}}

.section-description {{
    max-width: 430px;
    color: #71837b;
    font-size: 13px;
    line-height: 1.7;
}}

.site-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 17px;
}}

.site-card {{
    padding: 27px;
    border-radius: 19px;
    background: linear-gradient(145deg, #10201a, #0a1511);
    border: 1px solid rgba(255,255,255,.07);
    transition: .25s;
}}

.site-card:hover {{
    transform: translateY(-4px);
    border-color: rgba(68,133,255,.35);
    box-shadow: 0 20px 50px rgba(0,0,0,.22);
}}

.site-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 15px;
}}

.site-name {{
    font-size: 19px;
    font-weight: 730;
}}

.site-location {{
    color: #657770;
    font-size: 12px;
    margin-top: 4px;
}}

.status-badge {{
    padding: 5px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    font-size: 9px;
    letter-spacing: .7px;
    font-weight: 800;
}}

.status-badge.good {{
    color: #4fdfa0;
    background: rgba(79,223,160,.09);
}}

.status-badge.warning {{
    color: #ffbd59;
    background: rgba(255,189,89,.09);
}}

.site-stage {{
    margin-top: 23px;
    display: flex;
    align-items: center;
    gap: 8px;
    color: #9aaba4;
    font-size: 12px;
}}

.stage-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
}}

.stage-dot.active {{
    background: #4d8dff;
    box-shadow: 0 0 10px #4d8dff;
}}

.stage-dot.processing {{
    background: #b18aff;
}}

.production-row {{
    margin-top: 24px;
    display: flex;
    align-items: end;
    justify-content: space-between;
}}

.muted {{
    display: block;
    color: #63746e;
    font-size: 10px;
    margin-bottom: 4px;
}}

.production-row strong {{
    font-size: 18px;
}}

.production-status {{
    color: #5e9aff;
    font-size: 11px;
    font-weight: 650;
}}

.progress-track {{
    height: 5px;
    background: #1b2a24;
    border-radius: 10px;
    margin-top: 18px;
    overflow: hidden;
}}

.progress-fill {{
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #145cff, #66a1ff);
}}

.progress-label {{
    display: flex;
    justify-content: space-between;
    margin-top: 7px;
    color: #5f7069;
    font-size: 10px;
}}

.site-link {{
    display: block;
    color: #659aff;
    font-size: 11px;
    text-decoration: none;
    margin-top: 20px;
}}

.operations {{
    background: #091510;
    border-top: 1px solid rgba(255,255,255,.05);
    border-bottom: 1px solid rgba(255,255,255,.05);
}}

.operation-grid {{
    display: grid;
    grid-template-columns: 1.25fr .75fr;
    gap: 18px;
}}

.panel {{
    padding: 27px;
    border-radius: 19px;
    background: #0e1c16;
    border: 1px solid rgba(255,255,255,.07);
}}

.panel-heading {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
}}

.panel-heading h3 {{
    font-size: 16px;
}}

.panel-heading a {{
    color: #6198ff;
    text-decoration: none;
    font-size: 11px;
}}

.lifecycle-item {{
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,.045);
}}

.lifecycle-item:last-child {{
    border-bottom: none;
}}

.lifecycle-number {{
    width: 34px;
    height: 34px;
    flex-shrink: 0;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #16261f;
    color: #75867f;
    font-size: 10px;
    font-weight: 700;
}}

.lifecycle-number.active {{
    background: #0d5cff;
    color: white;
    box-shadow: 0 0 20px rgba(13,92,255,.3);
}}

.lifecycle-number.completed {{
    color: #54d99a;
    background: rgba(84,217,154,.08);
}}

.lifecycle-content {{
    flex: 1;
}}

.lifecycle-name {{
    font-size: 13px;
    font-weight: 650;
}}

.lifecycle-status {{
    color: #63756e;
    font-size: 10px;
    margin-top: 2px;
}}

.alert-card {{
    display: flex;
    gap: 12px;
    padding: 14px;
    border-radius: 12px;
    background: rgba(255,255,255,.025);
    margin-bottom: 9px;
}}

.alert-symbol {{
    width: 33px;
    height: 33px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    font-weight: 800;
}}

.alert-symbol.medium {{
    color: #ffbd59;
    background: rgba(255,189,89,.1);
}}

.alert-symbol.low {{
    color: #61a0ff;
    background: rgba(97,160,255,.1);
}}

.alert-message {{
    color: #dbe5e0;
    font-size: 12px;
    line-height: 1.4;
}}

.alert-meta {{
    color: #61736b;
    font-size: 9px;
    margin-top: 5px;
}}

.monitor-box {{
    padding: 17px;
    margin-top: 18px;
    border-radius: 13px;
    background: rgba(72,215,151,.045);
    border: 1px solid rgba(72,215,151,.1);
}}

.monitor-title {{
    color: #50d995;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 6px;
}}

.monitor-text {{
    color: #72847c;
    font-size: 11px;
    line-height: 1.6;
}}

.equipment-section {{
    background: #06100c;
}}

.equipment-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 17px;
}}

.equipment-card {{
    padding: 24px;
    border-radius: 17px;
    background: #0c1914;
    border: 1px solid rgba(255,255,255,.06);
}}

.equipment-icon {{
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: rgba(66,136,255,.1);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #609aff;
    margin-bottom: 18px;
    font-size: 18px;
}}

.equipment-name {{
    font-size: 14px;
    font-weight: 700;
}}

.equipment-status {{
    color: #4fdda0;
    font-size: 10px;
    margin-top: 5px;
}}

footer {{
    background: #030907;
    padding: 40px 6%;
    border-top: 1px solid rgba(255,255,255,.05);
}}

.footer {{
    max-width: 1200px;
    margin: auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
}}

.footer-brand {{
    font-weight: 750;
    font-size: 16px;
}}

.footer-text {{
    color: #5c6e67;
    font-size: 10px;
}}

.footer-health {{
    color: #4fd99b;
    font-size: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}}

.health-dot {{
    width: 6px;
    height: 6px;
    background: #4fd99b;
    border-radius: 50%;
    box-shadow: 0 0 10px #4fd99b;
}}

@media (max-width: 900px) {{
    .nav-links {{
        display: none;
    }}

    .stats {{
        grid-template-columns: repeat(2, 1fr);
    }}

    .stat:nth-child(2) {{
        border-right: none;
    }}

    .stat:nth-child(-n+2) {{
        border-bottom: 1px solid rgba(255,255,255,.07);
    }}

    .operation-grid {{
        grid-template-columns: 1fr;
    }}

    .equipment-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

@media (max-width: 650px) {{
    .hero {{
        min-height: 680px;
    }}

    .hero-content {{
        padding: 90px 5% 130px;
    }}

    .hero h1 {{
        font-size: 50px;
        letter-spacing: -2.5px;
    }}

    .hero-text {{
        font-size: 14px;
    }}

    .section {{
        padding: 80px 5%;
    }}

    .section-header {{
        display: block;
    }}

    .section-description {{
        margin-top: 15px;
    }}

    .site-grid {{
        grid-template-columns: 1fr;
    }}

    .equipment-grid {{
        grid-template-columns: 1fr;
    }}

    .stats-wrapper {{
        padding: 0 5%;
    }}

    .stat {{
        padding: 22px;
    }}

    .footer {{
        flex-direction: column;
        align-items: flex-start;
    }}
}}

@media (max-width: 450px) {{
    .stats {{
        grid-template-columns: 1fr;
    }}

    .stat {{
        border-right: none;
        border-bottom: 1px solid rgba(255,255,255,.07);
    }}

    .stat:last-child {{
        border-bottom: none;
    }}

    .hero h1 {{
        font-size: 42px;
    }}

    .hero-buttons {{
        flex-direction: column;
        align-items: stretch;
    }}

    .button-primary,
    .button-secondary {{
        text-align: center;
    }}
}}
</style>
</head>

<body>

<section class="hero">
    <nav class="navbar">
        <a href="/" class="logo">
            <div class="logo-mark">⛏</div>
            <div class="logo-name">MINE<span>CORE</span></div>
        </a>

        <div class="nav-links">
            <a href="#sites">Mining Sites</a>
            <a href="#operations">Operations</a>
            <a href="#equipment">Equipment</a>
            <a href="#safety">Safety</a>
        </div>

        <a class="nav-cta" href="#dashboard">
            Dashboard
        </a>
    </nav>

    <div class="hero-content">
        <div class="eyebrow">
            <span class="eyebrow-dot"></span>
            Mining Operations Platform
        </div>

        <h1>
            Smarter software for
            <span>mining operations.</span>
        </h1>

        <p class="hero-text">
            Monitor production, manage mining stages,
            track equipment and maintain operational
            safety across your mining sites from one
            intelligent platform.
        </p>

        <div class="hero-buttons">
            <a class="button-primary" href="#dashboard">
                Explore Operations →
            </a>

            <a class="button-secondary" href="#sites">
                View Mining Sites
            </a>
        </div>
    </div>
</section>

<div class="stats-wrapper" id="dashboard">
    <div class="stats">

        <div class="stat">
            <div class="stat-label">Today's Production</div>

            <div class="stat-value blue">
                {total_production:,}
                <span style="font-size:11px;color:#60736b;">
                    TONS
                </span>
            </div>
        </div>

        <div class="stat">
            <div class="stat-label">Active Sites</div>
            <div class="stat-value green">
                {active_sites}
            </div>
        </div>

        <div class="stat">
            <div class="stat-label">Open Alerts</div>
            <div class="stat-value orange">
                {open_alerts}
            </div>
        </div>

        <div class="stat">
            <div class="stat-label">Equipment Operational</div>
            <div class="stat-value blue">
                {operational_equipment}/{total_equipment}
            </div>
        </div>

    </div>
</div>

<section class="section" id="sites">
    <div class="section-header">
        <div>
            <div class="section-label">Live Operations</div>
            <h2 class="section-title">Mining Sites</h2>
        </div>

        <p class="section-description">
            Monitor production, operational status
            and safety conditions across every
            mining location.
        </p>
    </div>

    <div class="site-grid">
        {site_cards}
    </div>
</section>
<section class="section" id="security">
<section class="section" id="policy">
    <div class="section-header">
        <div>
            <div class="section-label">AI Policy Explainer</div>
            <h2 class="section-title">Mining Policy Assistant</h2>
        </div>

        <p class="section-description">
            Ask questions about mining safety and operational policies.
        </p>
    </div>

    <div class="panel">
        <h3>Ask a Policy Question</h3>

        <input
            type="text"
            id="policy-question"
            placeholder="e.g. What PPE is required?"
        >

        <button onclick="askPolicy()">
            Explain Policy
        </button>

        <div id="policy-result"></div>
    </div>
</section>
    <div class="section-header">
        <div>
            <div class="section-label">Security Center</div>
            <h2 class="section-title">Password Security</h2>
        </div>

        <p class="section-description">
            Check password strength and security policy compliance.
        </p>
    </div>

    <div class="panel">
        <h3>Password Security Analyzer</h3>

        <input
            type="password"
            id="security-password"
            placeholder="Enter a test password"
        >

        <button onclick="analyzePassword()">
            Analyze Password
        </button>

        <div id="security-result"></div>
    </div>
</section>
<section class="operations" id="operations">
    <div class="section">

        <div class="section-header">
            <div>
                <div class="section-label">Control Center</div>
                <h2 class="section-title">Operations Overview</h2>
            </div>

            <p class="section-description">
                Follow the mining lifecycle from
                exploration and development through
                extraction and transportation.
            </p>
        </div>

        <div class="operation-grid">

            <div class="panel">
                <div class="panel-heading">
                    <h3>Mining Lifecycle</h3>

                    <a href="/api/mining/stages">
                        View data →
                    </a>
                </div>

                {stage_rows}
            </div>

            <div class="panel" id="safety">
                <div class="panel-heading">
                    <h3>Safety Alerts</h3>

                    <a href="/api/sites/1/alerts">
                        View alerts →
                    </a>
                </div>

                {alert_rows}

                <div class="monitor-box">
                    <div class="monitor-title">
                        SAFETY MONITORING
                    </div>

                    <div class="monitor-text">
                        Operational safety requirements
                        and alerts are being monitored
                        across active mining sites.
                    </div>
                </div>
            </div>

        </div>
    </div>
</section>

<section class="section equipment-section" id="equipment">

    <div class="section-header">
        <div>
            <div class="section-label">Fleet Monitoring</div>
            <h2 class="section-title">Equipment</h2>
        </div>

        <p class="section-description">
            Monitor equipment assigned to active
            mining operations and track operational
            status.
        </p>
    </div>

    <div class="equipment-grid">

        <div class="equipment-card">
            <div class="equipment-icon">⚙</div>

            <div class="equipment-name">
                Excavator
            </div>

            <div class="equipment-status">
                ● Operational
            </div>
        </div>

        <div class="equipment-card">
            <div class="equipment-icon">🚚</div>

            <div class="equipment-name">
                Haul Truck
            </div>

            <div class="equipment-status">
                ● Operational
            </div>
        </div>

        <div class="equipment-card">
            <div class="equipment-icon">◉</div>

            <div class="equipment-name">
                Fleet Monitoring
            </div>

            <div class="equipment-status">
                {equipment_percentage}% Operational
            </div>
        </div>

    </div>
</section>

<footer>
    <div class="footer">

        <div class="footer-brand">
            ⛏ MINECORE
        </div>

        <div class="footer-text">
            Mining Operations Management Platform
            · Version 2.0.0
        </div>

        <div class="footer-health">
            <span class="health-dot"></span>
            System Operational
        </div>

    </div>
</footer>

<script>
async function analyzePassword() {{
    const password = document.getElementById("security-password").value;
    const result = document.getElementById("security-result");

    if (!password) {{
        result.innerHTML = "<p>Please enter a password to analyze.</p>";
        return;
    }}

    result.innerHTML = "<p>Analyzing...</p>";

    try {{
        const response = await fetch("/api/security/password", {{
            method: "POST",
            headers: {{
                "Content-Type": "application/json"
            }},
            body: JSON.stringify({{
                password: password
            }})
        }});

        const data = await response.json();

        result.innerHTML = `
            <p><strong>Strength:</strong> ${{data.strength}}</p>
            <p><strong>Score:</strong> ${{data.score}}/100</p>
            <p><strong>Policy compliant:</strong> ${{data.policy_compliant ? "Yes" : "No"}}</p>
            <h4>Password Checks</h4>
            <ul>
                <li>Minimum 12 characters: ${{data.checks.minimum_length ? "✅" : "❌"}}</li>
                <li>Uppercase: ${{data.checks.uppercase ? "✅" : "❌"}}</li>
                <li>Lowercase: ${{data.checks.lowercase ? "✅" : "❌"}}</li>
                <li>Number: ${{data.checks.number ? "✅" : "❌"}}</li>
                <li>Special character: ${{data.checks.special_character ? "✅" : "❌"}}</li>
            </ul>
        `;
    }} catch (error) {{
        result.innerHTML = "<p>Unable to analyze password.</p>";
    }}
}}


async function askPolicy() {{
    const question = document.getElementById("policy-question").value;
    const result = document.getElementById("policy-result");

    if (!question) {{
        result.innerHTML = "<p>Please enter a policy question.</p>";
        return;
    }}

    result.innerHTML = "<p>Searching policy...</p>";

    try {{
        const response = await fetch("/api/policy/explain", {{
            method: "POST",
            headers: {{
                "Content-Type": "application/json"
            }},
            body: JSON.stringify({{
                question: question
            }})
        }});

        const data = await response.json();

        result.innerHTML = `
            <h4>Policy Explanation</h4>
            <p>${{data.answer}}</p>
            <p><strong>Source:</strong> ${{data.source}}</p>
            ${{data.topic ? `<p><strong>Topic:</strong> ${{data.topic}}</p>` : ""}}
        `;
    }} catch (error) {{
        result.innerHTML = "<p>Unable to retrieve policy information.</p>";
    }}
}}
</script>
</body>
</html>
"""


@app.get(
    "/health",
    response_model=HealthResponse,
    include_in_schema=False
)
def health_check():
    return {
        "status": "healthy",
        "service": "minecore",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get(
    "/api/mining/stages",
    response_model=List[MiningStage]
)
def get_all_stages(
    status: Optional[str] = Query(
        None,
        description="Filter stages by status"
    )
):
    stages = mining_stages

    if status:
        stages = [
            stage
            for stage in stages
            if stage["status"].lower() == status.lower()
        ]

    return stages


@app.get(
    "/api/mining/stages/{stage_id}",
    response_model=MiningStage
)
def get_stage(stage_id: int):
    stage = find_stage(stage_id)

    if not stage:
        raise HTTPException(
            status_code=404,
            detail=f"Mining stage {stage_id} not found"
        )

    return stage


@app.get("/api/mining/stages/{stage_id}/safety")
def get_safety_requirements(stage_id: int):
    stage = find_stage(stage_id)

    if not stage:
        raise HTTPException(
            status_code=404,
            detail=f"Mining stage {stage_id} not found"
        )

    return {
        "stage_id": stage["id"],
        "stage": stage["name"],
        "status": stage["status"],
        "requirement_count": len(stage["safety_requirements"]),
        "safety_requirements": stage["safety_requirements"]
    }
@app.post("/api/security/password")
class PolicyQuestion(BaseModel):
    question: str = Field(..., min_length=2)


@app.post("/api/policy/explain")
def explain_policy(request: PolicyQuestion):
    question = request.question.lower()

    # Simple retrieval: find the policy entries most related to the question
    matches = []

    for policy in POLICY_KNOWLEDGE:
        keywords = policy["topic"].lower().split()

        if any(keyword in question for keyword in keywords):
            matches.append(policy)

    if not matches:
        return {
            "answer": "No matching policy was found for this question.",
            "source": "MineCore Policy Knowledge Base",
            "matches": []
        }

    best_match = matches[0]

    return {
        "answer": best_match["content"],
        "source": best_match["source"],
        "topic": best_match["topic"]
    }
def check_password_security(request: PasswordRequest):
    return analyze_password(request.password)

@app.get(
    "/api/sites",
    response_model=List[MiningSite]
)
def get_sites():
    return mining_sites


@app.get("/api/sites/{site_id}")
def get_site(site_id: int):
    site = find_site(site_id)

    if not site:
        raise HTTPException(
            status_code=404,
            detail=f"Mining site {site_id} not found"
        )

    current_stage = find_stage(site["current_stage_id"])

    return {
        "site": site,
        "current_stage": current_stage
    }


@app.get("/api/dashboard/{site_id}")
def get_dashboard(site_id: int):
    site = find_site(site_id)

    if not site:
        raise HTTPException(
            status_code=404,
            detail=f"Mining site {site_id} not found"
        )

    current_stage = find_stage(site["current_stage_id"])

    site_alerts = [
        alert
        for alert in alerts
        if alert["site_id"] == site_id
        and alert["status"] == "Open"
    ]

    equipment = (
        current_stage.get("equipment", [])
        if current_stage
        else []
    )

    operational_equipment = sum(
        1
        for item in equipment
        if item["status"].lower() == "operational"
    )

    return {
        "site": {
            "id": site["id"],
            "name": site["name"],
            "location": site["location"]
        },
        "operation": {
            "current_stage": current_stage["name"],
            "stage_id": current_stage["id"],
            "stage_status": current_stage["status"]
        },
        "production": {
            "status": site["production_status"],
            "production_today": site["production_today"],
            "unit": "tons"
        },
        "safety": {
            "status": site["safety_status"],
            "open_alerts": len(site_alerts)
        },
        "equipment": {
            "total": len(equipment),
            "operational": operational_equipment,
            "items": equipment
        },
        "alerts": site_alerts
    }


@app.get("/api/sites/{site_id}/equipment")
def get_equipment(site_id: int):
    site = find_site(site_id)

    if not site:
        raise HTTPException(
            status_code=404,
            detail=f"Mining site {site_id} not found"
        )

    stage = find_stage(site["current_stage_id"])

    equipment = (
        stage.get("equipment", [])
        if stage
        else []
    )

    return {
        "site_id": site_id,
        "site": site["name"],
        "current_stage": stage["name"] if stage else None,
        "equipment_count": len(equipment),
        "equipment": equipment
    }


@app.get("/api/sites/{site_id}/alerts")
def get_alerts(
    site_id: int,
    severity: Optional[str] = Query(
        None,
        description="Filter alerts by severity"
    ),
    status: Optional[str] = Query(
        None,
        description="Filter alerts by status"
    )
):
    site = find_site(site_id)

    if not site:
        raise HTTPException(
            status_code=404,
            detail=f"Mining site {site_id} not found"
        )

    site_alerts = [
        alert
        for alert in alerts
        if alert["site_id"] == site_id
    ]

    if severity:
        site_alerts = [
            alert
            for alert in site_alerts
            if alert["severity"].lower() == severity.lower()
        ]

    if status:
        site_alerts = [
            alert
            for alert in site_alerts
            if alert["status"].lower() == status.lower()
        ]

    return {
        "site_id": site_id,
        "total": len(site_alerts),
        "alerts": site_alerts
    }


@app.get("/api/mining/stages/{stage_id}/policy-context")
def get_policy_context(stage_id: int):
    stage = find_stage(stage_id)

    if not stage:
        raise HTTPException(
            status_code=404,
            detail=f"Mining stage {stage_id} not found"
        )

    return {
        "stage_id": stage["id"],
        "stage": stage["name"],
        "policy_query": (
            f"What safety policies and requirements "
            f"apply to the {stage['name']} stage?"
        ),
        "safety_requirements": stage["safety_requirements"],
        "rag_ready": True
    }
