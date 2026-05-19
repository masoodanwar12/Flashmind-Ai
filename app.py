"""
app.py — Main Flask Server
AI Flashcard Study App
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from ai_brain import generate_flashcards, check_answer_with_ai
from storage import save_deck, get_deck, get_all_decks, update_card_progress, get_deck_stats

app = Flask(__name__)

# ── HOME PAGE ──
@app.route("/")
def index():
    decks = get_all_decks()
    return render_template("index.html", decks=decks)

# ── GENERATE FLASHCARDS ──
@app.route("/generate", methods=["POST"])
def generate():
    topic = request.form.get("topic", "").strip()
    if not topic:
        return redirect(url_for("index"))

    # Generate cards with Groq AI
    cards = generate_flashcards(topic)
    if not cards:
        return render_template("index.html",
                               decks=get_all_decks(),
                               error="Failed to generate flashcards. Try again!")

    # Save deck
    deck_id = save_deck(topic, cards)
    return redirect(url_for("study", deck_id=deck_id))

# ── STUDY PAGE ──
@app.route("/study/<deck_id>")
def study(deck_id):
    deck = get_deck(deck_id)
    if not deck:
        return redirect(url_for("index"))
    stats = get_deck_stats(deck_id)
    return render_template("study.html", deck=deck, stats=stats)

# ── UPDATE CARD PROGRESS ──
@app.route("/progress", methods=["POST"])
def progress():
    data = request.json
    deck_id = data.get("deck_id")
    card_id = data.get("card_id")
    status  = data.get("status")   # easy / medium / hard
    update_card_progress(deck_id, card_id, status)
    stats = get_deck_stats(deck_id)
    return jsonify({"success": True, "stats": stats})

# ── RESULTS PAGE ──
@app.route("/results/<deck_id>")
def results(deck_id):
    deck  = get_deck(deck_id)
    if not deck:
        return redirect(url_for("index"))
    stats = get_deck_stats(deck_id)
    return render_template("results.html", deck=deck, stats=stats)


# ── AI CHECK ANSWER ──
@app.route("/check_answer", methods=["POST"])
def check_answer():
    data = request.json
    user_answer = data.get("user_answer", "")
    correct_answer = data.get("correct_answer", "")
    question = data.get("question", "")
    result = check_answer_with_ai(question, correct_answer, user_answer)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)