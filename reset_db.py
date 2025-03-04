#!/usr/bin/env python3
"""
Simple utility script to reset the database by clearing all conversations.
This is useful for quickly starting with a clean slate for testing.

Usage:
    python reset_db.py
"""

from clear_conversations import clear_all

if __name__ == "__main__":
    success, message = clear_all()
    print(message)
