# 🤖 AI Desktop Workspace & Summarizer (PyQt6)

A high-performance, visually advanced desktop application built with Python and PyQt6. Features real-time AI response streaming powered by the Google Gemini API, hardware-accelerated QSS styling, and a cyber/glassmorphism theme.

## ✨ Features
- **Hardware-Accelerated UI:** Built with PyQt6 and styled with custom QSS stylesheets and native drop-shadow effects.
- **Real-Time Token Streaming:** Asynchronous background streaming powered by `QThread` and Google Gemini API.
- **Fallback Resilience:** Automatic failover across Gemini model endpoints (`gemini-3.8-flash`) for reliability.
- **Multi-Mode Workspace:** Instant summarization, takeaway extraction, and coding assistant options.

## 🛠️ Tech Stack
- **GUI:** PyQt6 (Qt Style Sheets, QGraphicsEffects)
- **AI Backend:** `google-genai` SDK
- **Environment:** `python-dotenv`
- **Language:** Python 3.10+