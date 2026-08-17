import os
import threading
import webbrowser

from flask import Flask, request, jsonify, send_from_directory

from backend.auditor import audit_website
from backend.ai import generate_ai_analysis
from backend.report import generate_report


# ============================================================
# SITEFORGE
# WEBSITE INTELLIGENCE ENGINE
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)

REPORTS_DIR = os.path.join(
    BASE_DIR,
    "reports"
)


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


# ============================================================
# FRONTEND FILES
# ============================================================

@app.route("/<path:filename>")
def frontend_file(filename):

    file_path = os.path.join(
        FRONTEND_DIR,
        filename
    )

    if os.path.isfile(file_path):

        return send_from_directory(
            FRONTEND_DIR,
            filename
        )

    return jsonify({
        "error": "File not found."
    }), 404


# ============================================================
# WEBSITE AUDIT API
# ============================================================

@app.route(
    "/api/audit",
    methods=["POST"]
)
def audit():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                "success": False,
                "error": "No request data received."
            }), 400

        url = data.get("url")

        if not url:

            return jsonify({
                "success": False,
                "error": "Website URL is required."
            }), 400

        print()
        print("=" * 60)
        print("SITEFORGE — NEW AUDIT")
        print("=" * 60)
        print(f"Target: {url}")
        print()

        # ----------------------------------------------------
        # STEP 1 — WEBSITE AUDIT
        # ----------------------------------------------------

        print("[1/3] Running website audit...")

        audit_data = audit_website(url)

        if not audit_data:

            return jsonify({
                "success": False,
                "error":
                    "The website audit returned no data."
            }), 500

        print("[1/3] Audit complete.")

        # ----------------------------------------------------
        # STEP 2 — ANALYSIS
        # ----------------------------------------------------

        print("[2/3] Generating analysis...")

        analysis_data = generate_ai_analysis(
            audit_data
        )

        print("[2/3] Analysis complete.")

        # ----------------------------------------------------
        # STEP 3 — RETURN RESULTS
        # ----------------------------------------------------

        print("[3/3] Sending results to browser...")
        print("=" * 60)

        return jsonify({

            "success": True,

            "audit": audit_data,

            "ai": analysis_data

        })

    except Exception as error:

        print()
        print("AUDIT ERROR:")
        print(error)
        print()

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# PDF REPORT API
# ============================================================

@app.route(
    "/api/report",
    methods=["POST"]
)
def create_report():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                "success": False,
                "error":
                    "No report data received."
            }), 400

        audit_data = data.get(
            "audit"
        )

        analysis_data = data.get(
            "ai"
        )

        if not audit_data:

            return jsonify({
                "success": False,
                "error":
                    "Audit data is missing."
            }), 400

        if not analysis_data:

            return jsonify({
                "success": False,
                "error":
                    "Analysis data is missing."
            }), 400

        print()
        print("Generating PDF report...")

        os.makedirs(
            REPORTS_DIR,
            exist_ok=True
        )

        report_path = generate_report({

            "audit": audit_data,

            "ai": analysis_data

        })

        filename = os.path.basename(
            report_path
        )

        print(
            f"Report created: {filename}"
        )

        return jsonify({

            "success": True,

            "filename": filename,

            "download_url":
                f"/reports/{filename}"

        })

    except Exception as error:

        print()
        print("REPORT ERROR:")
        print(error)
        print()

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# ============================================================
# SERVE GENERATED REPORTS
# ============================================================

@app.route(
    "/reports/<path:filename>"
)
def download_report(filename):

    file_path = os.path.join(
        REPORTS_DIR,
        filename
    )

    if not os.path.isfile(file_path):

        return jsonify({
            "success": False,
            "error": "Report not found."
        }), 404

    return send_from_directory(
        REPORTS_DIR,
        filename,
        as_attachment=False
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "service": "SiteForge"
    })


# ============================================================
# LOCAL BROWSER
# ============================================================

def open_browser():

    try:

        webbrowser.open(
            "http://127.0.0.1:5000"
        )

    except Exception:

        pass


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    os.makedirs(
        REPORTS_DIR,
        exist_ok=True
    )

    print()
    print("=" * 60)
    print("                 SITEFORGE")
    print("          WEBSITE INTELLIGENCE ENGINE")
    print("=" * 60)
    print()

    print(
        "Local server: "
        "http://127.0.0.1:5000"
    )

    print()
    print(
        "Starting application..."
    )

    print(
        "Press CTRL+C to stop."
    )

    print()

    # --------------------------------------------------------
    # LOCAL DEVELOPMENT
    # --------------------------------------------------------

    if os.environ.get("RENDER") != "true":

        threading.Timer(
            1.2,
            open_browser
        ).start()

    # --------------------------------------------------------
    # SERVER CONFIGURATION
    # --------------------------------------------------------

    host = "0.0.0.0"

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host=host,
        port=port,
        debug=False
    )