import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from services.ai_service import AIServiceError, get_advisor_response
from services.safety_service import detect_crisis, get_crisis_response

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

MAX_MESSAGE_LENGTH = int(os.getenv("MAX_USER_MESSAGE_LENGTH", "1000"))
IS_PRODUCTION = os.getenv("FLASK_ENV", "development") == "production"

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)


@app.route("/")
def index():
    return render_template(
        "index.html",
        app_name=os.getenv("APP_NAME", "AI Emotional Advisor"),
    )


@app.route("/api/chat", methods=["POST"])
@limiter.limit("20 per minute")
def chat():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid request body."}), 400

    message = (data.get("message") or "").strip()
    selected_mood = (data.get("mood") or "").strip().lower() or None

    if not message:
        return jsonify({"success": False, "error": "Message cannot be empty."}), 400

    if len(message) > MAX_MESSAGE_LENGTH:
        return jsonify(
            {
                "success": False,
                "error": f"Message is too long. Maximum {MAX_MESSAGE_LENGTH} characters allowed.",
            }
        ), 400

    if detect_crisis(message):
        return jsonify(
            {
                "success": True,
                "reply": get_crisis_response(),
                "mood": "crisis",
                "is_crisis": True,
            }
        )

    try:
        reply, mood = get_advisor_response(message, selected_mood)
        return jsonify(
            {
                "success": True,
                "reply": reply,
                "mood": mood,
                "is_crisis": False,
            }
        )
    except AIServiceError as exc:
        return jsonify({"success": False, "error": str(exc)}), exc.status_code
    except Exception:
        if IS_PRODUCTION:
            return jsonify(
                {"success": False, "error": "Something went wrong. Please try again later."}
            ), 500
        return jsonify({"success": False, "error": "An unexpected error occurred."}), 500


@app.errorhandler(429)
def rate_limit_exceeded(_error):
    return jsonify(
        {
            "success": False,
            "error": "Too many requests. Please wait a moment before trying again.",
        }
    ), 429


if __name__ == "__main__":
    app.run(debug=not IS_PRODUCTION, host="0.0.0.0", port=5000)
