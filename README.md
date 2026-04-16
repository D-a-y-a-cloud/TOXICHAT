# 🛡️ ToxiChat — AI-Powered Chat with Real-Time Toxicity Detection

A WhatsApp-like chat application with ML-powered toxicity detection, real-time alerts, and analytics dashboard.

## 📁 Project Structure

```
toxichat/
├── backend/
│   ├── main.py                 # FastAPI app (REST + WebSocket)
│   ├── models.py               # Pydantic schemas
│   ├── database.py             # MongoDB + in-memory fallback
│   ├── ml_service.py           # ML model loading + prediction
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── public/index.html
│   ├── src/
│   │   ├── App.js              # React app (Login + Chat + Dashboard)
│   │   ├── App.css             # WhatsApp dark theme
│   │   └── index.js            # Entry point
│   └── package.json
├── models/                     # Place model.pkl + tfidf_vectorizer.pkl here
├── ToxiChat_Colab_Backend.py   # Colab-runnable backend
└── README.md
```

---

## 🚀 Step-by-Step Setup (Local)

### 1. Backend

```bash
cd toxichat/backend
pip install -r requirements.txt
python main.py
```
Backend runs at `http://localhost:8000`

> **Note:** MongoDB is optional. The app auto-falls back to in-memory storage if MongoDB isn't running.

### 2. ML Model (Optional)

Place your pre-trained files in `toxichat/models/`:
- `model.pkl` — Trained SVM/RF classifier
- `tfidf_vectorizer.pkl` — Fitted TF-IDF vectorizer

If no model files exist, the app uses a keyword-based fallback.

### 3. Frontend

```bash
cd toxichat/frontend
npm install
npm start
```
Frontend runs at `http://localhost:3000`

**To connect to a different backend** (e.g., Colab ngrok URL):
```bash
REACT_APP_API_URL=https://your-ngrok-url.ngrok.io npm start
```

### 4. Test the App

1. Open `http://localhost:3000`
2. Register two accounts (use two browser tabs/windows)
3. Select the other user from the contacts list
4. Start chatting! Toxic messages will trigger alerts.

---

## 🧪 Google Colab Setup

1. Open a new Colab notebook
2. Copy `ToxiChat_Colab_Backend.py` into cells (split at `# === CELL N ===` markers)
3. Replace `YOUR_NGROK_AUTH_TOKEN` with a free token from [ngrok.com](https://ngrok.com)
4. Run — you'll get a public URL
5. Use that URL with the React frontend:
   ```bash
   REACT_APP_API_URL=https://xxxx.ngrok.io npm start
   ```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register new user |
| POST | `/api/login` | Login |
| GET | `/api/users` | List all users |
| POST | `/api/predict` | Predict toxicity for text |
| GET | `/api/messages/{user1}/{user2}` | Get chat history |
| GET | `/api/dashboard/stats` | Dashboard analytics |
| WS | `/ws/{token}` | WebSocket for real-time chat |

---

## 💬 WebSocket Message Format

**Send message:**
```json
{"type": "message", "text": "Hello!", "receiver": "username", "is_group": false}
```

**Receive types:** `message`, `toxicity_alert`, `toxicity_warning`, `users_list`, `system`
