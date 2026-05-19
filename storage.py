"""
storage.py — Save and load flashcard data
Uses JSON file as simple database
"""

import json
import os
from datetime import datetime, timedelta

DATA_FILE = "data.json"

def load_data() -> dict:
    """Load all data from JSON file"""
    if not os.path.exists(DATA_FILE):
        return {"decks": [], "progress": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data: dict):
    """Save all data to JSON file"""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_deck(topic: str, cards: list) -> str:
    """Save a new deck of flashcards"""
    data = load_data()
    deck_id = str(len(data["decks"]) + 1)
    deck = {
        "id": deck_id,
        "topic": topic,
        "cards": cards,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_cards": len(cards)
    }
    data["decks"].append(deck)
    # Initialize progress for this deck
    data["progress"][deck_id] = {
        str(card["id"]): {
            "status": "new",
            "next_review": None,
            "times_seen": 0,
            "times_correct": 0
        } for card in cards
    }
    save_data(data)
    return deck_id

def get_deck(deck_id: str) -> dict:
    """Get a specific deck by ID"""
    data = load_data()
    for deck in data["decks"]:
        if deck["id"] == deck_id:
            return deck
    return None

def get_all_decks() -> list:
    """Get all decks"""
    data = load_data()
    return data["decks"]

def update_card_progress(deck_id: str, card_id: int, status: str):
    """Update progress for a card after user rates it"""
    data = load_data()
    if deck_id not in data["progress"]:
        return

    # Spaced repetition — when to show card next
    days_map = {
        "easy":   7,   # show again in 7 days
        "medium": 3,   # show again in 3 days
        "hard":   1,   # show again tomorrow
    }
    days = days_map.get(status, 1)
    next_review = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    card_progress = data["progress"][deck_id].get(str(card_id), {
        "status": "new",
        "next_review": None,
        "times_seen": 0,
        "times_correct": 0
    })

    card_progress["status"] = status
    card_progress["next_review"] = next_review
    card_progress["times_seen"] = card_progress.get("times_seen", 0) + 1
    if status == "easy":
        card_progress["times_correct"] = card_progress.get("times_correct", 0) + 1

    data["progress"][deck_id][str(card_id)] = card_progress
    save_data(data)

def get_deck_stats(deck_id: str) -> dict:
    """Get statistics for a deck"""
    data = load_data()
    progress = data["progress"].get(deck_id, {})

    stats = {"easy": 0, "medium": 0, "hard": 0, "new": 0, "total": len(progress)}
    for card_progress in progress.values():
        status = card_progress.get("status", "new")
        stats[status] = stats.get(status, 0) + 1

    return stats