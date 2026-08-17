import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def audit_website(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    url = url.rstrip("/")
    start_time = time.time()

    response = requests.get(
        url,
        timeout=20,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
            )
        },
        allow_redirects=True
    )

    response_time = round(time.time() - start_time, 2)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    final_url = response.url
    parsed = urlparse(final_url)

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    description_tag = soup.find("meta", attrs={"name": "description"})
    description = (
        description_tag.get("content", "").strip()
        if description_tag else ""
    )

    canonical_tag = soup.find("link", rel="canonical")
    canonical = canonical_tag.get("href") if canonical_tag else None

    viewport = soup.find("meta", attrs={"name": "viewport"})

    h1 = soup.find_all("h1")
    images = soup.find_all("img")
    links = soup.find_all("a", href=True)
    forms = soup.find_all("form")
    buttons = soup.find_all(["button", "input"])

    missing_alt = [
        img for img in images
        if not img.get("alt")
    ]

    internal_links = []
    external_links = []

    for link in links:
        absolute = urljoin(final_url, link.get("href", "").strip())
        link_host = urlparse(absolute).netloc

        if link_host == parsed.netloc:
            internal_links.append(absolute)
        elif link_host:
            external_links.append(absolute)

    og_title = soup.find("meta", property="og:title")
    og_description = soup.find("meta", property="og:description")
    og_image = soup.find("meta", property="og:image")

    json_ld = soup.find_all(
        "script",
        attrs={"type": "application/ld+json"}
    )

    headers = response.headers

    security_headers = {
        "Content-Security-Policy":
            headers.get("Content-Security-Policy"),
        "Strict-Transport-Security":
            headers.get("Strict-Transport-Security"),
        "X-Content-Type-Options":
            headers.get("X-Content-Type-Options"),
        "X-Frame-Options":
            headers.get("X-Frame-Options"),
        "Referrer-Policy":
            headers.get("Referrer-Policy"),
        "Permissions-Policy":
            headers.get("Permissions-Policy"),
    }

    missing_security_headers = [
        name for name, value in security_headers.items()
        if not value
    ]

    mixed_content = []

    if parsed.scheme == "https":
        for tag in soup.find_all(
            ["script", "img", "iframe", "link", "video", "audio"]
        ):
            resource = tag.get("src") or tag.get("href")

            if resource and resource.startswith("http://"):
                mixed_content.append(resource)

    suspicious_scripts = []

    suspicious_patterns = [
        r"eval\s*\(",
        r"atob\s*\(",
        r"fromCharCode\s*\(",
        r"unescape\s*\(",
    ]

    for script in soup.find_all("script"):
        content = script.string or ""

        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                suspicious_scripts.append(pattern)
                break

    suspicious_extensions = (
        ".exe", ".scr", ".bat", ".cmd",
        ".msi", ".apk", ".jar"
    )

    suspicious_downloads = []

    for link in links:
        href = link.get("href", "").lower()

        if href.split("?")[0].endswith(suspicious_extensions):
            suspicious_downloads.append(link.get("href"))

    def check_resource(path):
        try:
            result = requests.get(
                urljoin(final_url + "/", path),
                timeout=8,
                headers={"User-Agent": "SiteForge/1.0"}
            )
            return result.status_code == 200
        except Exception:
            return False

    robots_detected = check_resource("robots.txt")
    sitemap_detected = check_resource("sitemap.xml")

    page_size_mb = round(
        len(response.content) / 1024 / 1024,
        2
    )

    # --------------------------------------------------------
    # SCORES
    # --------------------------------------------------------

    seo = 100

    if not title:
        seo -= 20
    if not description:
        seo -= 15
    if not h1:
        seo -= 15
    if len(h1) > 1:
        seo -= 5
    if not canonical:
        seo -= 10
    if not robots_detected:
        seo -= 5
    if not sitemap_detected:
        seo -= 5
    if not json_ld:
        seo -= 5

    seo = max(0, min(100, seo))

    performance = 100

    if response_time > 1:
        performance -= 10
    if response_time > 2:
        performance -= 10
    if response_time > 3:
        performance -= 15
    if page_size_mb > 2:
        performance -= 10
    if page_size_mb > 4:
        performance -= 15

    performance = max(0, min(100, performance))

    accessibility = 100

    if not viewport:
        accessibility -= 15

    if missing_alt:
        accessibility -= min(20, len(missing_alt) * 2)

    if not h1:
        accessibility -= 10

    accessibility = max(0, min(100, accessibility))

    technical = 100

    if response.status_code >= 400:
        technical -= 30
    if parsed.scheme != "https":
        technical -= 20
    if not canonical:
        technical -= 5
    if not robots_detected:
        technical -= 5
    if not sitemap_detected:
        technical -= 5

    technical = max(0, min(100, technical))

    ux = 100

    if not forms:
        ux -= 5
    if not buttons:
        ux -= 5
    if not h1:
        ux -= 5

    ux = max(0, min(100, ux))

    security = 100

    if parsed.scheme != "https":
        security -= 30

    security -= min(
        30,
        len(missing_security_headers) * 5
    )

    if mixed_content:
        security -= 15

    if suspicious_downloads:
        security -= 20

    security = max(0, min(100, security))

    overall = round(
        (
            seo +
            performance +
            accessibility +
            technical +
            ux +
            security
        ) / 6
    )

    # --------------------------------------------------------
    # FINDINGS
    # --------------------------------------------------------

    findings = []

    if not h1:
        findings.append({
            "category": "SEO",
            "severity": "High",
            "finding": "No H1 heading found.",
            "recommendation": "Add one clear, descriptive H1."
        })

    if response_time > 1:
        findings.append({
            "category": "Performance",
            "severity": "High",
            "finding":
                "Initial server response took more than 1 second.",
            "recommendation":
                "Investigate server response time, caching, "
                "CDN usage and backend processing."
        })

    if not json_ld:
        findings.append({
            "category": "SEO",
            "severity": "Medium",
            "finding": "No JSON-LD structured data detected.",
            "recommendation":
                "Evaluate whether appropriate Schema.org "
                "structured data should be implemented."
        })

    if not viewport:
        findings.append({
            "category": "Accessibility",
            "severity": "Medium",
            "finding": "Mobile viewport metadata was not detected.",
            "recommendation":
                "Add an appropriate viewport meta tag."
        })

    if missing_security_headers:
        findings.append({
            "category": "Security",
            "severity": "Medium",
            "finding":
                "Important security headers are missing: "
                + ", ".join(missing_security_headers),
            "recommendation":
                "Review and implement appropriate HTTP security headers."
        })

    if mixed_content:
        findings.append({
            "category": "Security",
            "severity": "High",
            "finding":
                f"{len(mixed_content)} insecure HTTP resource(s) "
                "were detected on an HTTPS page.",
            "recommendation":
                "Serve all website resources securely over HTTPS."
        })

    if suspicious_scripts:
        findings.append({
            "category": "Security",
            "severity": "Medium",
            "finding":
                "Potentially suspicious JavaScript patterns were detected.",
            "recommendation":
                "Review the affected scripts manually and verify "
                "that they are legitimate."
        })

    if suspicious_downloads:
        findings.append({
            "category": "Security",
            "severity": "High",
            "finding":
                f"{len(suspicious_downloads)} potentially risky "
                "download link(s) were detected.",
            "recommendation":
                "Verify that these downloads are intentional "
                "and trusted."
        })

    security_findings = [
        item for item in findings
        if item["category"] == "Security"
    ]

    if not security_findings:
        security_findings = [{
            "severity": "Pass",
            "finding":
                "No obvious security indicators were detected "
                "during this external scan.",
            "recommendation":
                "Continue regular security monitoring."
        }]

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {
        "url": url,
        "domain": parsed.netloc,
        "final_url": final_url,
        "status_code": response.status_code,
        "response_time": response_time,
        "page_size": page_size_mb,
        "https": parsed.scheme == "https",
        "canonical": bool(canonical),
        "mobile_viewport": bool(viewport),
        "robots": robots_detected,
        "sitemap": sitemap_detected,
        "structured_data": len(json_ld),
        "images": len(images),
        "images_missing_alt": len(missing_alt),
        "total_links": len(links),
        "internal_links": len(internal_links),
        "external_links": len(external_links),
        "word_count": len(
            soup.get_text(" ", strip=True).split()
        ),
        "forms": len(forms),
        "buttons": len(buttons),

        "social": {
            "og_title": bool(og_title),
            "og_description": bool(og_description),
            "og_image": bool(og_image)
        },

        "security": {
            "score": security,
            "headers": security_headers,
            "missing_headers": missing_security_headers,
            "mixed_content": mixed_content,
            "suspicious_scripts": len(suspicious_scripts),
            "suspicious_downloads": suspicious_downloads,
            "findings": security_findings
        },

        "scores": {
            "overall": overall,
            "seo": seo,
            "performance": performance,
            "accessibility": accessibility,
            "technical": technical,
            "ux": ux,
            "security": security
        },

        "findings": findings
    }