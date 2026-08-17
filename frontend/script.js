// ============================================================
// SITEFORGE — FRONTEND ENGINE
// ============================================================

let currentAudit = null;
let currentAI = null;


// ============================================================
// ELEMENT HELPERS
// ============================================================

function $(id) {
    return document.getElementById(id);
}


// ============================================================
// URL NORMALIZATION
// ============================================================

function normalizeUrl(value) {

    value = value.trim();

    if (!value) {
        return "";
    }

    if (!value.startsWith("http://") &&
        !value.startsWith("https://")) {
        value = "https://" + value;
    }

    return value;
}


// ============================================================
// ANALYZE WEBSITE
// ============================================================

async function analyzeWebsite() {

    const input = $("urlInput");
    const button = $("analyzeBtn");
    const loading = $("loading");
    const results = $("results");

    const rawUrl = input.value;
    const url = normalizeUrl(rawUrl);

    if (!url) {
        alert("Please enter a website URL.");
        input.focus();
        return;
    }

    button.disabled = true;
    loading.style.display = "block";
    results.style.display = "none";

    try {

        const response = await fetch("/api/audit", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                url: url
            })

        });

        const contentType =
            response.headers.get("content-type") || "";

        let data;

        if (contentType.includes("application/json")) {
            data = await response.json();
        } else {

            const text = await response.text();

            throw new Error(
                "Server returned an unexpected response."
            );
        }

        if (!response.ok || !data.success) {

            throw new Error(
                data.error ||
                "Website audit failed."
            );
        }

        currentAudit = data.audit;
        currentAI = data.ai || null;

        displayResults(
            currentAudit,
            currentAI
        );

    } catch (error) {

        console.error(error);

        alert(
            "Audit failed:\n\n" +
            error.message
        );

    } finally {

        button.disabled = false;
        loading.style.display = "none";
    }
}


// ============================================================
// DISPLAY RESULTS
// ============================================================

function displayResults(audit, ai) {

    $("results").style.display = "block";

    $("resultDomain").textContent =
        audit.domain || "Website Audit";

    $("overallScore").textContent =
        audit.scores?.overall ?? 0;

    $("seoScore").textContent =
        audit.scores?.seo ?? 0;

    $("performanceScore").textContent =
        audit.scores?.performance ?? 0;

    $("accessibilityScore").textContent =
        audit.scores?.accessibility ?? 0;

    $("technicalScore").textContent =
        audit.scores?.technical ?? 0;

    $("uxScore").textContent =
        audit.scores?.ux ?? 0;

    if ($("securityScore")) {

        $("securityScore").textContent =
            audit.scores?.security ?? 0;
    }

    updateHealth(
        audit.scores?.overall ?? 0
    );

    generateSummary(
        audit,
        ai
    );

    displaySecurity(
        audit.security
    );

    displayFindings(
        audit.findings
    );

    animateScore(
        audit.scores?.overall ?? 0
    );

    $("results").scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


// ============================================================
// HEALTH STATUS
// ============================================================

function updateHealth(score) {

    const health = $("healthText");

    if (!health) {
        return;
    }

    if (score >= 90) {

        health.textContent =
            "Excellent";

    } else if (score >= 75) {

        health.textContent =
            "Good";

    } else if (score >= 60) {

        health.textContent =
            "Needs Improvement";

    } else {

        health.textContent =
            "Critical";
    }
}


// ============================================================
// SUMMARY
// ============================================================

function generateSummary(audit, ai) {

    const summary = $("summaryText");

    if (!summary) {
        return;
    }

    const score =
        audit.scores?.overall ?? 0;

    if (ai && typeof ai === "object") {

        const possibleSummary =
            ai.summary ||
            ai.executive_summary ||
            ai.overall_assessment;

        if (typeof possibleSummary === "string" &&
            possibleSummary.trim()) {

            summary.textContent =
                possibleSummary;

            return;
        }
    }

    if (score >= 90) {

        summary.textContent =
            `${audit.domain} has a strong technical foundation. ` +
            `The remaining opportunities are primarily optimization, ` +
            `security and conversion improvements.`;

    } else if (score >= 75) {

        summary.textContent =
            `${audit.domain} has a solid foundation, but several ` +
            `optimization opportunities could improve search visibility, ` +
            `performance, accessibility and security.`;

    } else if (score >= 60) {

        summary.textContent =
            `${audit.domain} has several areas that should be reviewed. ` +
            `Addressing the highest-priority findings can improve ` +
            `website quality and visitor experience.`;

    } else {

        summary.textContent =
            `${audit.domain} has significant issues that should be ` +
            `reviewed and addressed as soon as possible.`;
    }
}


// ============================================================
// SECURITY
// ============================================================

function displaySecurity(security) {

    const section =
        $("securitySection");

    const status =
        $("securityStatus");

    const findingsContainer =
        $("securityFindings");

    if (!section ||
        !status ||
        !findingsContainer) {

        return;
    }

    section.style.display = "block";

    findingsContainer.innerHTML = "";

    if (!security) {

        status.innerHTML =
            `<div class="security-status">
                Security scan data unavailable.
            </div>`;

        return;
    }

    const score =
        security.score ?? 0;

    let statusText;

    if (score >= 90) {

        statusText =
            "No major security indicators were detected.";

    } else if (score >= 70) {

        statusText =
            "Some security improvements are recommended.";

    } else {

        statusText =
            "Important security issues require attention.";
    }

    status.innerHTML = `
        <div class="security-status">
            <strong>Security Score: ${score}/100</strong>
            <br>
            <span style="color:#9ca4b8;">
                ${escapeHtml(statusText)}
            </span>
        </div>
    `;

    const findings =
        security.findings || [];

    findings.forEach(
        finding => {

            const card =
                document.createElement("div");

            card.className =
                "finding";

            const severity =
                String(
                    finding.severity || "Info"
                ).toLowerCase();

            let severityClass =
                "severity-medium";

            if (severity === "high") {
                severityClass =
                    "severity-high";
            }

            if (severity === "pass") {
                severityClass =
                    "severity-pass";
            }

            card.innerHTML = `

                <div class="severity ${severityClass}">
                    ${escapeHtml(
                        finding.severity || "Info"
                    )}
                </div>

                <div class="finding-title">
                    ${escapeHtml(
                        finding.finding || ""
                    )}
                </div>

                <div class="finding-text">
                    ${escapeHtml(
                        finding.recommendation || ""
                    )}
                </div>

            `;

            findingsContainer.appendChild(
                card
            );
        }
    );

    // --------------------------------------------------------
    // Additional security details
    // --------------------------------------------------------

    if (security.missing_headers &&
        security.missing_headers.length > 0) {

        const card =
            document.createElement("div");

        card.className =
            "finding";

        card.innerHTML = `

            <div class="severity severity-medium">
                SECURITY HEADERS
            </div>

            <div class="finding-title">
                Missing security headers
            </div>

            <div class="finding-text">
                ${security.missing_headers
                    .map(escapeHtml)
                    .join(", ")}
            </div>

        `;

        findingsContainer.appendChild(
            card
        );
    }

    if (security.mixed_content &&
        security.mixed_content.length > 0) {

        const card =
            document.createElement("div");

        card.className =
            "finding";

        card.innerHTML = `

            <div class="severity severity-high">
                MIXED CONTENT
            </div>

            <div class="finding-title">
                Insecure resources detected
            </div>

            <div class="finding-text">
                ${security.mixed_content.length}
                HTTP resource(s) were detected
                on an HTTPS page.
            </div>

        `;

        findingsContainer.appendChild(
            card
        );
    }

    if (security.suspicious_downloads &&
        security.suspicious_downloads.length > 0) {

        const card =
            document.createElement("div");

        card.className =
            "finding";

        card.innerHTML = `

            <div class="severity severity-high">
                DOWNLOAD WARNING
            </div>

            <div class="finding-title">
                Potentially dangerous downloads detected
            </div>

            <div class="finding-text">
                ${security.suspicious_downloads.length}
                potentially dangerous download link(s)
                were found.
            </div>

        `;

        findingsContainer.appendChild(
            card
        );
    }
}


// ============================================================
// GENERAL FINDINGS
// ============================================================

function displayFindings(findings) {

    const section =
        $("findingsSection");

    const container =
        $("findings");

    if (!section || !container) {
        return;
    }

    container.innerHTML = "";

    if (!findings ||
        findings.length === 0) {

        section.style.display = "none";
        return;
    }

    section.style.display = "block";

    findings.forEach(
        finding => {

            const card =
                document.createElement("div");

            card.className =
                "finding";

            const severity =
                String(
                    finding.severity || "Info"
                ).toLowerCase();

            let severityClass =
                "severity-medium";

            if (severity === "high") {
                severityClass =
                    "severity-high";
            }

            if (severity === "pass") {
                severityClass =
                    "severity-pass";
            }

            card.innerHTML = `

                <div class="severity ${severityClass}">
                    ${escapeHtml(
                        finding.severity || "Info"
                    )}
                </div>

                <div class="finding-title">
                    ${escapeHtml(
                        finding.category || "Website"
                    )}
                </div>

                <div class="finding-text">
                    <strong>
                        ${escapeHtml(
                            finding.finding || ""
                        )}
                    </strong>
                    <br><br>
                    ${escapeHtml(
                        finding.recommendation || ""
                    )}
                </div>

            `;

            container.appendChild(
                card
            );
        }
    );
}


// ============================================================
// PDF REPORT
// ============================================================

async function generatePDF() {

    if (!currentAudit) {

        alert(
            "Please analyze a website first."
        );

        return;
    }

    try {

        const response =
            await fetch(
                "/api/report",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        audit:
                            currentAudit,

                        ai:
                            currentAI

                    })

                }
            );

        const contentType =
            response.headers.get(
                "content-type"
            ) || "";

        let data;

        if (contentType.includes(
            "application/json"
        )) {

            data =
                await response.json();

        } else {

            throw new Error(
                "Server returned an unexpected response."
            );
        }

        if (!response.ok ||
            !data.success) {

            throw new Error(
                data.error ||
                "Could not generate PDF."
            );
        }

        if (data.download_url) {

            window.open(
                data.download_url,
                "_blank"
            );

        } else {

            throw new Error(
                "PDF was created but no download link was returned."
            );
        }

    } catch (error) {

        console.error(error);

        alert(
            "PDF generation failed:\n\n" +
            error.message
        );
    }
}


// ============================================================
// PROPOSAL
// ============================================================

async function generateProposal() {

    if (!currentAudit) {

        alert(
            "Please analyze a website first."
        );

        return;
    }

    try {

        const response =
            await fetch(
                "/api/proposal",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        audit:
                            currentAudit,

                        ai:
                            currentAI

                    })

                }
            );

        const contentType =
            response.headers.get(
                "content-type"
            ) || "";

        let data;

        if (contentType.includes(
            "application/json"
        )) {

            data =
                await response.json();

        } else {

            throw new Error(
                "Server returned an unexpected response."
            );
        }

        if (!response.ok ||
            !data.success) {

            throw new Error(
                data.error ||
                "Could not generate proposal."
            );
        }

        if (data.download_url) {

            window.open(
                data.download_url,
                "_blank"
            );

        } else {

            throw new Error(
                "Proposal was created but no download link was returned."
            );
        }

    } catch (error) {

        console.error(error);

        alert(
            "Proposal generation failed:\n\n" +
            error.message
        );
    }
}


// ============================================================
// SCORE ANIMATION
// ============================================================

function animateScore(target) {

    const element =
        $("overallScore");

    if (!element) {
        return;
    }

    const duration = 900;

    const start =
        performance.now();

    function update(now) {

        const progress =
            Math.min(
                (now - start) /
                duration,
                1
            );

        const eased =
            1 -
            Math.pow(
                1 - progress,
                3
            );

        element.textContent =
            Math.round(
                target * eased
            );

        if (progress < 1) {

            requestAnimationFrame(
                update
            );
        }
    }

    requestAnimationFrame(
        update
    );
}


// ============================================================
// ENTER KEY
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const input =
            $("urlInput");

        if (!input) {
            return;
        }

        input.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter"
                ) {

                    event.preventDefault();

                    analyzeWebsite();
                }
            }
        );
    }
);


// ============================================================
// HTML ESCAPE
// ============================================================

function escapeHtml(value) {

    if (value === null ||
        value === undefined) {

        return "";
    }

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}