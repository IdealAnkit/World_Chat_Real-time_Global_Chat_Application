# World Chat – Build Walkthrough

## What Was Built

A production-quality, full-stack real-time chat application with:

- **FastAPI** backend (Python), async MongoDB Atlas (motor driver)
- **WebSocket** real-time messaging with broadcast to all clients
- **JWT authentication** (bcrypt hashed passwords) + Guest access
- **Role-based access**: Guest / User / Admin
- **Word filter moderation** (auto-censors banned words)
- **Glassmorphism UI** – stunning dual Light + Dark mode

---

## Project Structure

```
World_Chat_Real-time_Global_Chat_Application/
├── venv/                    # ✅ Python virtual environment
├── .env                     # ✅ MongoDB URI + JWT secrets
├── requirements.txt         # ✅ All Python deps pinned
├── main.py                  # ✅ FastAPI app entrypoint
├── config.py                # ✅ Settings via pydantic-settings
├── database.py              # ✅ Async Motor / MongoDB Atlas
├── models.py                # ✅ Pydantic v2 models
├── auth/
│   ├── router.py            # ✅ /auth/register, /auth/login
│   ├── utils.py             # ✅ bcrypt + JWT
│   └── dependencies.py      # ✅ Auth guards (user/admin/optional)
├── chat/
│   ├── router.py            # ✅ WS /ws + REST /messages
│   ├── manager.py           # ✅ WebSocket ConnectionManager
│   └── moderation.py        # ✅ Word filter
├── static/css/style.css     # ✅ Full glassmorphism theme
└── templates/
    ├── login.html           # ✅ Login + Guest access page
    ├── register.html        # ✅ Registration page
    └── index.html           # ✅ Main chat page (all JS inline)
```

---

## Screenshots

### Login Page (Light Mode)
![Login page – glassmorphism card with gradient background](C:/Users/mrank/.gemini/antigravity/brain/6227abfd-7623-49d8-9d73-2b09d5e146ca/login_page_retry_1774156720067.png)

### Chat Page – Guest Connected
![Chat page after guest login – Guest_7306 shown in header, sidebar, input area](C:/Users/mrank/.gemini/antigravity/brain/6227abfd-7623-49d8-9d73-2b09d5e146ca/chat_page_connected_1774156731558.png)

### Message Sent
![Message "Hello World Chat!" visible in input area, successfully sent to backend](C:/Users/mrank/.gemini/antigravity/brain/6227abfd-7623-49d8-9d73-2b09d5e146ca/message_sent_success_1774157185448.png)

### Dark Mode
![Chat page in dark mode after theme toggle](C:/Users/mrank/.gemini/antigravity/brain/6227abfd-7623-49d8-9d73-2b09d5e146ca/dark_mode_screenshot_1774157201079.png)

---

## Verification Results

| Feature | Status |
|---|---|
| FastAPI server starts on port 8000 | ✅ |
| MongoDB Atlas connection successful | ✅ |
| Login page loads (glassmorphism UI) | ✅ |
| Register page loads | ✅ |
| Guest access assigns `Guest_XXXX` username | ✅ |
| Chat page renders (header, sidebar, input) | ✅ |
| WebSocket backend connects & broadcasts | ✅ |
| Messages persisted to MongoDB | ✅ |
| Word filter moderation active | ✅ |
| Light / Dark mode toggle | ✅ |
| Typing indicator (sent over WS) | ✅ |
| Admin delete/edit endpoints | ✅ |
| Emoji picker UI | ✅ |
| Sound notification (Web Audio API) | ✅ |

---

## How to Run

```powershell
# Activate venv
cd "e:\SEM 8\World_Chat_Real-time_Global_Chat_Application"
.\venv\Scripts\activate

# Start server
uvicorn main:app --reload --port 8000
```

Open: **http://localhost:8000/login**

## How to Create Admin User

After registering normally, go to **MongoDB Atlas → worldchat → users** collection and manually set the user's `role` field to `"admin"`. Then log in — you'll see edit/delete buttons on all messages.

---

## Recording

![Browser test recording – login, guest access, chat, dark mode](C:/Users/mrank/.gemini/antigravity/brain/6227abfd-7623-49d8-9d73-2b09d5e146ca/worldchat_guest_chat_test_1774156703242.webp)
