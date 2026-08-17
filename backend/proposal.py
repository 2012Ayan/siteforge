import os
import re
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PROPOSALS_DIR = os.path.join(
    BASE_DIR,
    "reports"
)


# ============================================================
# GENERATE PROPOSAL
# ============================================================

def generate_proposal(data):

    os.makedirs(
        PROPOSALS_DIR,
        exist_ok=True
    )

    audit = data.get("audit", {})
    ai = data.get("ai", {})

    if not isinstance(audit, dict):
        audit = {}

    if not isinstance(ai, dict):
        ai = {}

    domain = audit.get(
        "domain",
        "Website"
    )

    safe_domain = re.sub(
        r"[^a-zA-Z0-9.-]",
        "_",
        str(domain)
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"SiteForge_Proposal_"
        f"{safe_domain}_"
        f"{timestamp}.pdf"
    )

    filepath = os.path.join(
        PROPOSALS_DIR,
        filename
    )

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = create_styles()

    story = []

    scores = audit.get(
        "scores",
        {}
    )

    if not isinstance(scores, dict):
        scores = {}

    overall = safe_score(
        scores.get("overall", 0)
    )

    # ========================================================
    # COVER
    # ========================================================

    story.append(
        Spacer(1, 25 * mm)
    )

    story.append(
        Paragraph(
            "SITEFORGE AI",
            styles["SFBrand"]
        )
    )

    story.append(
        Spacer(1, 10 * mm)
    )

    story.append(
        Paragraph(
            "WEBSITE OPTIMIZATION",
            styles["SFTitle"]
        )
    )

    story.append(
        Paragraph(
            "CLIENT PROPOSAL",
            styles["SFProposalTitle"]
        )
    )

    story.append(
        Spacer(1, 12 * mm)
    )

    story.append(
        Paragraph(
            escape(domain),
            styles["SFDomain"]
        )
    )

    story.append(
        Spacer(1, 18 * mm)
    )

    story.append(
        Paragraph(
            f"Current Website Score: {overall}/100",
            styles["SFScore"]
        )
    )

    story.append(
        Spacer(1, 8 * mm)
    )

    story.append(
        Paragraph(
            "Prepared using SiteForge AI website intelligence.",
            styles["SFSubtitle"]
        )
    )

    story.append(
        Spacer(1, 25 * mm)
    )

    story.append(
        Paragraph(
            datetime.now().strftime(
                "%B %d, %Y"
            ),
            styles["SFSmall"]
        )
    )

    story.append(
        PageBreak()
    )

    # ========================================================
    # OPPORTUNITY
    # ========================================================

    story.append(
        Paragraph(
            "1. The Opportunity",
            styles["SFSection"]
        )
    )

    summary = ai.get(
        "executive_summary",
        ""
    )

    if not summary:
        summary = (
            "Our analysis identified several opportunities "
            "to improve the website's search visibility, "
            "performance, accessibility and conversion potential."
        )

    story.append(
        Paragraph(
            escape(summary),
            styles["SFBody"]
        )
    )

    story.append(
        Spacer(1, 8 * mm)
    )

    story.append(
        Paragraph(
            "Why this matters",
            styles["SFSubheading"]
        )
    )

    story.append(
        Paragraph(
            "A website is more than an online presence. "
            "Technical problems, weak search visibility, "
            "slow loading and conversion friction can reduce "
            "the number of visitors who become customers. "
            "The recommended improvements below are designed "
            "to address the highest-impact opportunities first.",
            styles["SFBody"]
        )
    )

    # ========================================================
    # CURRENT PERFORMANCE
    # ========================================================

    story.append(
        Paragraph(
            "2. Current Website Performance",
            styles["SFSection"]
        )
    )

    rows = [
        ["Area", "Score", "Status"],

        [
            "SEO",
            f"{safe_score(scores.get('seo', 0))}/100",
            assessment(
                safe_score(scores.get("seo", 0))
            )
        ],

        [
            "Performance",
            f"{safe_score(scores.get('performance', 0))}/100",
            assessment(
                safe_score(scores.get("performance", 0))
            )
        ],

        [
            "Accessibility",
            f"{safe_score(scores.get('accessibility', 0))}/100",
            assessment(
                safe_score(scores.get("accessibility", 0))
            )
        ],

        [
            "Technical",
            f"{safe_score(scores.get('technical', 0))}/100",
            assessment(
                safe_score(scores.get("technical", 0))
            )
        ],

        [
            "UX / Conversion",
            f"{safe_score(scores.get('ux', 0))}/100",
            assessment(
                safe_score(scores.get("ux", 0))
            )
        ]
    ]

    story.append(
        make_table(
            rows,
            [65 * mm, 35 * mm, 55 * mm]
        )
    )

    # ========================================================
    # RECOMMENDED WORK
    # ========================================================

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "3. Recommended Optimization Work",
            styles["SFSection"]
        )
    )

    opportunities = ai.get(
        "top_opportunities",
        []
    )

    if not isinstance(opportunities, list):
        opportunities = []

    if not opportunities:

        opportunities = [
            {
                "category": "Website Optimization",
                "issue": "General optimization opportunities detected.",
                "recommendation": (
                    "Review the website and implement "
                    "improvements based on the audit."
                ),
                "priority": "Medium"
            }
        ]

    for index, opportunity in enumerate(
        opportunities[:8],
        start=1
    ):

        if not isinstance(opportunity, dict):
            continue

        category = opportunity.get(
            "category",
            "Optimization"
        )

        issue = opportunity.get(
            "issue",
            "Opportunity identified."
        )

        recommendation = opportunity.get(
            "recommendation",
            "Review and address this issue."
        )

        priority = opportunity.get(
            "priority",
            "Medium"
        )

        block = [

            Paragraph(
                f"{index}. {escape(category)}",
                styles["SFSubheading"]
            ),

            Paragraph(
                f"<b>Current Issue:</b> "
                f"{escape(issue)}",
                styles["SFBody"]
            ),

            Paragraph(
                f"<b>Recommended Work:</b> "
                f"{escape(recommendation)}",
                styles["SFBody"]
            ),

            Paragraph(
                f"<b>Priority:</b> "
                f"{escape(priority)}",
                styles["SFSmall"]
            ),

            Spacer(1, 5 * mm)
        ]

        story.append(
            KeepTogether(block)
        )

    # ========================================================
    # BUSINESS OUTCOMES
    # ========================================================

    story.append(
        Paragraph(
            "4. Expected Business Outcomes",
            styles["SFSection"]
        )
    )

    outcomes = [
        "Improve organic search visibility.",
        "Reduce technical and performance friction.",
        "Improve the experience for mobile and accessibility users.",
        "Create a clearer path from visitor to customer.",
        "Strengthen the technical foundation for future growth."
    ]

    for outcome in outcomes:

        story.append(
            Paragraph(
                f"• {escape(outcome)}",
                styles["SFBody"]
            )
        )

    # ========================================================
    # PROPOSED SCOPE
    # ========================================================

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "5. Proposed Scope",
            styles["SFSection"]
        )
    )

    scope_rows = [
        ["Service", "Included"],

        [
            "Website SEO Optimization",
            "Yes"
        ],

        [
            "Performance Optimization",
            "Yes"
        ],

        [
            "Accessibility Improvements",
            "Yes"
        ],

        [
            "Technical Website Improvements",
            "Yes"
        ],

        [
            "Conversion / UX Review",
            "Yes"
        ],

        [
            "Post-implementation Review",
            "Yes"
        ]
    ]

    story.append(
        make_table(
            scope_rows,
            [85 * mm, 70 * mm]
        )
    )

    story.append(
        Spacer(1, 12 * mm)
    )

    story.append(
        Paragraph(
            "Project Approach",
            styles["SFSubheading"]
        )
    )

    story.append(
        Paragraph(
            "The project should begin with the highest-priority "
            "issues identified in the SiteForge audit. Improvements "
            "will then be implemented and reviewed to ensure that "
            "the website's technical quality and user experience "
            "continue to improve.",
            styles["SFBody"]
        )
    )

    # ========================================================
    # NEXT STEPS
    # ========================================================

    story.append(
        Paragraph(
            "6. Next Steps",
            styles["SFSection"]
        )
    )

    steps = [
        "Review this proposal and the accompanying website audit.",
        "Confirm the optimization scope.",
        "Begin implementation of the highest-priority improvements.",
        "Perform a post-optimization website review."
    ]

    for index, step in enumerate(
        steps,
        start=1
    ):

        story.append(
            Paragraph(
                f"<b>{index}.</b> {escape(step)}",
                styles["SFBody"]
            )
        )

    story.append(
        Spacer(1, 15 * mm)
    )

    story.append(
        Paragraph(
            "Ready to improve your website?",
            styles["SFClosing"]
        )
    )

    story.append(
        Paragraph(
            "SiteForge AI",
            styles["SFBrand"]
        )
    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    doc.build(
        story,
        onFirstPage=add_footer,
        onLaterPages=add_footer
    )

    return filepath


# ============================================================
# STYLES
# ============================================================

def create_styles():

    styles = getSampleStyleSheet()

    # IMPORTANT:
    # All custom names begin with SF so they cannot collide
    # with ReportLab's built-in styles.

    styles.add(
        ParagraphStyle(
            name="SFBrand",
            parent=styles["Normal"],
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#6C63FF")
        )
    )

    styles.add(
        ParagraphStyle(
            name="SFTitle",
            parent=styles["Title"],
            fontSize=29,
            leading=34,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111827")
        )
    )

    styles.add(
        ParagraphStyle(
            name="SFProposalTitle",
            parent=styles["Title"],
            fontSize=23,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#6C63FF")
        )
    )

    styles.add(
        ParagraphStyle(
            name="SFDomain",
            parent=styles["Heading2"],
            fontSize=20,
            leading=25,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111827")
        )
    )

    styles.add(
        ParagraphStyle(
            name="SFScore",
            parent=styles["Normal"],
            fontSize=17,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111827")
        )
    )

    styles.add(
        ParagraphStyle(
            name="SFSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#6B7280")
        )
    )

    styles.add(
        ParagraphStyle(
            name="SFSection",
            parent=styles["Heading1"],
            fontSize=17,
            leading=22,
            textColor=colors.HexColor("#111827"),
            spaceBefore=5,
            spaceAfter=9
        )
    )

    styles.add(
        ParagraphStyle(
            name="SFSubheading",
            parent=styles["Heading3"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#111827"),
            spaceBefore=4,
            spaceAfter=4
        )
    )

    styles.add(
        ParagraphStyle(
            name="SFBody",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#374151"),
            spaceAfter=5
        )
    )

    styles.add(
        ParagraphStyle(
            name="SFSmall",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#6B7280")
        )
    )

    styles.add(
        ParagraphStyle(
            name="SFClosing",
            parent=styles["Heading2"],
            fontSize=18,
            leading=23,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111827"),
            spaceAfter=8
        )
    )

    return styles


# ============================================================
# TABLE
# ============================================================

def make_table(rows, widths):

    table = Table(
        rows,
        colWidths=widths,
        repeatRows=1
    )

    table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#111827")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8.5
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.35,
                colors.HexColor("#D1D5DB")
            ),

            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F9FAFB")
                ]
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    return table


# ============================================================
# HELPERS
# ============================================================

def safe_score(value):

    try:
        return int(value)

    except Exception:
        return 0


def assessment(score):

    if score >= 90:
        return "Excellent"

    if score >= 80:
        return "Good"

    if score >= 70:
        return "Needs Improvement"

    if score >= 50:
        return "Weak"

    return "Critical"


def escape(value):

    value = str(value)

    return (
        value
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


# ============================================================
# FOOTER
# ============================================================

def add_footer(canvas, doc):

    canvas.saveState()

    canvas.setFont(
        "Helvetica",
        7
    )

    canvas.setFillColor(
        colors.HexColor("#9CA3AF")
    )

    canvas.drawString(
        18 * mm,
        10 * mm,
        "Generated by SiteForge AI"
    )

    canvas.drawRightString(
        A4[0] - 18 * mm,
        10 * mm,
        f"Page {doc.page}"
    )

    canvas.restoreState()