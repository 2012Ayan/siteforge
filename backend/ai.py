import re


def generate_ai_analysis(audit_data):
    scores = audit_data.get("scores", {})
    issues = audit_data.get("issues", {})

    overall = int(scores.get("overall", 0))

    health = get_health(overall)

    all_issues = []

    category_names = {
        "seo": "SEO",
        "performance": "Performance",
        "accessibility": "Accessibility",
        "technical": "Technical",
        "ux": "UX / Conversion"
    }

    for category, name in category_names.items():
        for issue in issues.get(category, []):
            all_issues.append({
                "category": name,
                "issue": str(issue)
            })

    opportunities = []

    for item in all_issues:
        issue = item["issue"]

        if any(
            normalize(issue) == normalize(existing["issue"])
            for existing in opportunities
        ):
            continue

        opportunities.append({
            "category": item["category"],
            "issue": issue,
            "priority": get_priority(
                item["category"],
                issue
            ),
            "impact": get_business_impact(
                item["category"],
                issue
            ),
            "effort": get_effort(issue),
            "recommendation": create_recommendation(
                item["category"],
                issue
            )
        })

    priority_order = {
        "High": 0,
        "Medium": 1,
        "Low": 2
    }

    opportunities.sort(
        key=lambda x: priority_order.get(
            x["priority"],
            3
        )
    )

    opportunities = opportunities[:8]

    return {
        "mode": "expert-analysis",
        "health": health,
        "health_description": get_health_description(
            overall
        ),
        "executive_summary": create_executive_summary(
            audit_data,
            health
        ),
        "top_opportunities": opportunities,
        "business_impacts": create_business_impacts(
            audit_data
        ),
        "next_steps": create_next_steps(
            audit_data
        ),
        "priority_counts": {
            "high": sum(
                1 for x in opportunities
                if x["priority"] == "High"
            ),
            "medium": sum(
                1 for x in opportunities
                if x["priority"] == "Medium"
            ),
            "low": sum(
                1 for x in opportunities
                if x["priority"] == "Low"
            )
        }
    }


# ============================================================
# HEALTH
# ============================================================

def get_health(score):
    if score >= 90:
        return "Excellent"
    if score >= 80:
        return "Good"
    if score >= 70:
        return "Needs Improvement"
    if score >= 50:
        return "Weak"
    return "Critical"


def get_health_description(score):
    if score >= 90:
        return (
            "The website has a strong technical foundation. "
            "The remaining opportunities are primarily optimization "
            "and refinement opportunities."
        )

    if score >= 80:
        return (
            "The website has a solid foundation, but targeted "
            "improvements could strengthen search visibility, "
            "performance, accessibility, and conversion potential."
        )

    if score >= 70:
        return (
            "The website is functional but has several measurable "
            "areas where optimization could improve its overall "
            "quality and business performance."
        )

    if score >= 50:
        return (
            "Several important weaknesses were detected. "
            "Prioritizing the highest-impact findings should be "
            "the first optimization step."
        )

    return (
        "The audit identified significant issues that should be "
        "addressed before focusing on advanced optimization."
    )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(text):
    return re.sub(
        r"\s+",
        " ",
        str(text).lower().strip()
    )


# ============================================================
# PRIORITY
# ============================================================

def get_priority(category, issue):

    text = normalize(issue)

    high_terms = [
        "https",
        "security",
        "server response",
        "slow",
        "broken",
        "error",
        "missing h1",
        "no h1",
        "missing title",
        "missing meta"
    ]

    medium_terms = [
        "canonical",
        "viewport",
        "robots",
        "sitemap",
        "alt",
        "structured data",
        "json-ld",
        "content",
        "heading"
    ]

    if any(term in text for term in high_terms):
        return "High"

    if any(term in text for term in medium_terms):
        return "Medium"

    if category in [
        "SEO",
        "Performance",
        "Technical"
    ]:
        return "Medium"

    return "Low"


# ============================================================
# EFFORT
# ============================================================

def get_effort(issue):

    text = normalize(issue)

    low_terms = [
        "meta",
        "title",
        "h1",
        "alt",
        "viewport",
        "canonical",
        "robots",
        "sitemap",
        "structured data",
        "json-ld"
    ]

    high_terms = [
        "server response",
        "slow",
        "page size",
        "performance"
    ]

    if any(term in text for term in low_terms):
        return "Low"

    if any(term in text for term in high_terms):
        return "Medium"

    return "Medium"


# ============================================================
# BUSINESS IMPACT
# ============================================================

def get_business_impact(category, issue):

    text = normalize(issue)

    if "h1" in text or "heading" in text:
        return (
            "A clearer primary heading helps users and search "
            "engines understand the page's main topic."
        )

    if "meta description" in text:
        return (
            "A stronger search snippet can improve relevance "
            "and potentially increase organic click-through."
        )

    if "title" in text:
        return (
            "The page title is an important search and usability "
            "signal and should clearly describe the page."
        )

    if (
        "response" in text
        or "slow" in text
        or "page size" in text
    ):
        return (
            "Slower delivery can create friction before visitors "
            "can interact with the website."
        )

    if "alt" in text:
        return (
            "Better image descriptions improve accessibility and "
            "provide additional context for search engines."
        )

    if "https" in text:
        return (
            "Secure delivery protects visitor trust and prevents "
            "security warnings or insecure connections."
        )

    if (
        "structured data" in text
        or "json-ld" in text
    ):
        return (
            "Relevant structured data can give search engines "
            "additional context about the site's content."
        )

    if "canonical" in text:
        return (
            "Canonicalization can reduce ambiguity when multiple "
            "URLs represent the same content."
        )

    return (
        "Addressing this finding can improve the website's "
        "technical quality and overall user experience."
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

def create_recommendation(category, issue):

    text = normalize(issue)

    if "h1" in text or "heading" in text:
        return (
            "Add one clear, descriptive H1 that communicates the "
            "page's primary topic or value proposition. Keep the "
            "heading aligned with the actual content and search intent."
        )

    if "meta description" in text:
        return (
            "Write a unique meta description that summarizes the "
            "page accurately, communicates its value, and gives "
            "search users a reason to click."
        )

    if "title" in text:
        return (
            "Create a concise page title that describes the page's "
            "primary subject and uses important terminology naturally."
        )

    if "canonical" in text:
        return (
            "Add a canonical URL pointing to the preferred version "
            "of the page and ensure it matches the intended indexable URL."
        )

    if "robots.txt" in text:
        return (
            "Review the robots.txt configuration and ensure important "
            "pages are accessible to legitimate search crawlers."
        )

    if "sitemap" in text:
        return (
            "Create or maintain an XML sitemap containing important "
            "indexable URLs and keep it synchronized with the site."
        )

    if "viewport" in text:
        return (
            "Add a responsive viewport declaration so mobile browsers "
            "render the page at an appropriate scale."
        )

    if "alt" in text:
        return (
            "Add concise, meaningful alternative text to informative "
            "images while leaving purely decorative images appropriately "
            "handled."
        )

    if "https" in text:
        return (
            "Serve the entire website over HTTPS and redirect insecure "
            "HTTP requests to the secure version."
        )

    if (
        "response" in text
        or "slow" in text
    ):
        return (
            "Investigate server-side processing, caching, hosting "
            "configuration, CDN usage, and backend requests to reduce "
            "initial server response time."
        )

    if "page size" in text or "large" in text:
        return (
            "Reduce unnecessary page weight by compressing images, "
            "removing unused resources, and optimizing delivered assets."
        )

    if "structured data" in text or "json-ld" in text:
        return (
            "Evaluate whether relevant Schema.org structured data "
            "would add useful context for this page. Implement only "
            "types that accurately represent visible content."
        )

    if "form" in text:
        return (
            "Review the lead-capture experience and make the primary "
            "conversion action easy to understand and complete."
        )

    if "button" in text:
        return (
            "Review calls-to-action and make the primary visitor "
            "journey toward contact, purchase, booking, or another "
            "business goal immediately clear."
        )

    return (
        "Review this finding, determine its relevance to the site's "
        "business goals, and address it during the next optimization cycle."
    )


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

def create_executive_summary(audit_data, health):

    domain = audit_data.get(
        "domain",
        "this website"
    )

    scores = audit_data.get(
        "scores",
        {}
    )

    categories = [
        ("SEO", scores.get("seo", 0)),
        (
            "Performance",
            scores.get("performance", 0)
        ),
        (
            "Accessibility",
            scores.get("accessibility", 0)
        ),
        (
            "Technical",
            scores.get("technical", 0)
        ),
        (
            "UX / Conversion",
            scores.get("ux", 0)
        )
    ]

    strongest = max(
        categories,
        key=lambda x: x[1]
    )

    weakest = min(
        categories,
        key=lambda x: x[1]
    )

    return (
        f"{domain} received an overall website health score of "
        f"{scores.get('overall', 0)}/100 and is currently classified "
        f"as {health}. The strongest measured area was "
        f"{strongest[0]} at {strongest[1]}/100. "
        f"The largest measurable opportunity is currently "
        f"{weakest[0]} at {weakest[1]}/100. "
        f"The audit findings below have been prioritized according "
        f"to likely business impact and implementation effort."
    )


# ============================================================
# BUSINESS IMPACT SUMMARY
# ============================================================

def create_business_impacts(audit_data):

    scores = audit_data.get(
        "scores",
        {}
    )

    impacts = []

    if scores.get("seo", 100) < 90:
        impacts.append({
            "area": "Search Visibility",
            "impact": (
                "SEO improvements may strengthen how clearly the "
                "website communicates its content to search engines "
                "and potential visitors."
            )
        })

    if scores.get("performance", 100) < 90:
        impacts.append({
            "area": "User Experience",
            "impact": (
                "Performance optimization can reduce loading friction "
                "and help visitors reach useful content faster."
            )
        })

    if scores.get("ux", 100) < 90:
        impacts.append({
            "area": "Conversions",
            "impact": (
                "Clearer conversion paths can make it easier for "
                "visitors to take the actions that matter to the business."
            )
        })

    if scores.get("accessibility", 100) < 90:
        impacts.append({
            "area": "Accessibility",
            "impact": (
                "Accessibility improvements can make the website "
                "more usable across different visitors, devices, "
                "and assistive technologies."
            )
        })

    if scores.get("technical", 100) < 90:
        impacts.append({
            "area": "Technical Quality",
            "impact": (
                "Technical improvements can reduce implementation "
                "risks and provide a stronger foundation for future growth."
            )
        })

    if not impacts:
        impacts.append({
            "area": "Optimization",
            "impact": (
                "The website already has a strong measured foundation. "
                "The next focus should be refinement and conversion growth."
            )
        })

    return impacts


# ============================================================
# NEXT STEPS
# ============================================================

def create_next_steps(audit_data):

    scores = audit_data.get(
        "scores",
        {}
    )

    categories = [
        (
            "SEO",
            scores.get("seo", 100),
            "Resolve the highest-impact SEO findings and improve "
            "metadata, headings, and crawlability."
        ),
        (
            "Performance",
            scores.get("performance", 100),
            "Optimize server response, page weight, caching, "
            "and resource delivery."
        ),
        (
            "Accessibility",
            scores.get("accessibility", 100),
            "Improve semantic structure, responsive behavior, "
            "and accessible content."
        ),
        (
            "Technical",
            scores.get("technical", 100),
            "Review security, crawl configuration, canonicalization, "
            "and other technical foundations."
        ),
        (
            "UX / Conversion",
            scores.get("ux", 100),
            "Strengthen calls-to-action, lead capture, and the "
            "visitor journey toward the primary business goal."
        )
    ]

    categories.sort(
        key=lambda x: x[1]
    )

    return [
        {
            "category": category,
            "score": score,
            "action": action
        }
        for category, score, action
        in categories[:3]
    ]