# Expense Tracker
🔗 Live Demo:
- Frontend: https://sde-assessment-app-owpopjvzbj5tr2zrr2skhx.streamlit.app/

> A production-ready personal finance app that tracks where your money goes—even when your network doesn't cooperate.

Built to handle real-world conditions: network failures, retries, page refreshes, and all the messy stuff that happens in the real world.

---

## Quick Start (5 minutes)

### Prerequisites
- Python 3.9 or higher
- That's it!

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Run (two terminals)
```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload

# Terminal 2: Frontend
streamlit run frontend/app.py
```

### 3. Open & Use
- Frontend: https://sde-assessment-app-owpopjvzbj5tr2zrr2skhx.streamlit.app/
- Backend API: https://sde-assessment-app-production.up.railway.app
Done! Start adding expenses.

---

## What It Does

**Core Features:**
- Create expenses with amount, category, description & date
- View all expenses in a clean table
- Filter expenses by category
- Sort by date (newest first)
- See total for filtered expenses
- Bonus: Category breakdown chart

**Built for Real Life:**
- Idempotent: Submit twice = one expense (no duplicates)
- Network failures: Just retry. It handles it.
- Input validation: Prevents bad data
- Loading states: Always see what's happening

---

## Project Structure

```
sde-assessment-app/
├── backend/
│   └── main.py                 # FastAPI server (89 lines)
├── frontend/
│   └── app.py                  # Streamlit UI (110 lines)
├── expenses.db                 # SQLite database (auto-created)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## API Reference

### POST /expenses - Create an Expense

**Request:**
```bash
curl -X POST https://sde-assessment-app-production.up.railway.app/expenses \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.99,
    "category": "Food",
    "description": "Lunch",
    "date": "2026-04-22",
    "client_id": "unique-uuid"
  }'
```

**Response (201):**
```json
{
  "id": "expense-uuid-here",
  "status": "created"
}
```

**Response (duplicate):**
```json
{
  "id": "expense-uuid-here",
  "status": "already exists"
}
```

---

### GET /expenses - List Expenses

**All expenses:**
```bash
curl http://localhost:8000/expenses
```

**Filter by category:**
```bash
curl "http://sde-assessment-app-production.up.railway.app/expenses?category=Food"
```

**Sort by date (newest first):**
```bash
curl "http://sde-assessment-app-production.up.railway.app/expenses?sort=date_desc"
```

**Filter AND sort:**
```bash
curl "http://sde-assessment-app-production.up.railway.app/expenses?category=Food&sort=date_desc"
```

**Response:**
```json
[
  {
    "id": "exp-123",
    "amount": 50.99,
    "category": "Food",
    "description": "Lunch",
    "date": "2026-04-22",
    "created_at": "2026-04-22T12:30:45"
  }
]
```

---

## Database Schema

```
expenses table:
- id              UUID (primary key)
- amount          Integer in paise (₹0.01 units)
- category        String (Food, Transport, Shopping, etc)
- description     String
- date            String (YYYY-MM-DD)
- created_at      Timestamp
- client_id       String (unique, for idempotency)
```

Example: ₹50.99 stored as 5099 paise, returned as 50.99

---

## How Key Features Work

### Idempotency (Safe Retries)

**Problem:** Network timeout. User clicks submit again. Result? Duplicate expense.

**Our Solution:** Track request by `client_id`
1. User submits with UUID: `abc123`
2. Network fails → User retries
3. Frontend reuses UUID: `abc123` (stored in session)
4. Backend sees `abc123` → Returns existing expense
5. No duplicate!

**Real example:**
```
Submit: "₹50 lunch" with ID abc123 → Created
Network timeout (no response shown to user)
User clicks submit again → Same ID abc123 sent
Backend: "I've seen abc123 before!" → Returns existing
Database: Still only ONE expense
```

### Money in Paise (Not Floats!)

**Problem:** `0.1 + 0.2 = 0.30000000000000004` (floating point error)

**Our Solution:** Store all money as integers
- ₹50.99 → Store as `5099` paise → Display as `₹50.99`
- Calculations are exact, no rounding errors

### SQLite Database

**Why SQLite?**
- Single user → No multi-user complexity
- Zero setup → Just works
- File-based → Easy to backup/restore
- When this scales → Migrate to PostgreSQL

---

## Development & Troubleshooting

### Stop the Servers
```bash
# Terminal with backend: Press Ctrl+C
# Terminal with frontend: Press Ctrl+C
```

### Reset All Data
Delete the database:
```bash
rm expenses.db
```
Then restart servers. Fresh start!

### Common Issues

**Issue: `ModuleNotFoundError: No module named 'fastapi'`**
- Fix: `pip install -r requirements.txt`

**Issue: `Port 8000 already in use`**
- Fix: `lsof -ti:8000 | xargs kill -9` (Mac/Linux) or close the process using port 8000 (Windows)

**Issue: Streamlit won't connect to backend**
- Check: Is backend running on http://localhost:8000?
- Check: Is `API = "http://localhost:8000"` correct in `frontend/app.py`?

**Issue: Database locked error**
- Fix: Close all terminals, delete `expenses.db`, restart

**Issue: Form not resetting after submit**
- This is normal in Streamlit. Refresh the page.

---

## Design Decisions Explained

### Why FastAPI + Streamlit?
- **FastAPI:** Modern, fast, great for APIs
- **Streamlit:** Beautiful UI without fighting CSS/JavaScript
- **Together:** Perfect for rapid prototyping without compromises

### Why Session State for Idempotency?
Two options considered:
1. Browser localStorage → Complex to implement
2. Session state → Simple, works, MVP-friendly ← We chose this

Trade-off: If you close browser, new expense gets new ID. Acceptable for MVP.

### Why Paise Instead of Rupees?
Floats are the enemy of money. Always use integers with fixed scale (paise).

### Why No Authentication?
Assumption: This is YOUR personal tool. Multi-user? Add auth later.

---

## Trade-offs & Constraints

### What We Prioritized
1. Correctness (idempotency, money handling)
2. Reliability (error handling)
3. Code clarity (short, readable)
4. Real-world design (network failures matter)

### What We Skipped (On Purpose)
- Authentication (single-user tool)
- Edit/delete (nice-to-have, not core)
- Automated tests (MVP doesn't need them)
- Multi-user support (out of scope)
- Advanced analytics (keep it simple)
- Deployment config (code is ready, just needs server)

### Why These Choices?
We focused on what matters for a personal finance tool: being correct, reliable, and simple.

---

## Deployment

### Ready to Deploy?

1. Choose a platform:
   - Railway.app (10 min, easiest)
   - Render.com
   - Heroku
   - PythonAnywhere

2. Push to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Expense tracker"
   git push origin main
   ```

3. Connect your repo to the platform

4. Share the live URL!

(Detailed deployment guide for each platform available upon request)

---

## Quick Reference

| Task | Command |
|------|---------|
| Install deps | `pip install -r requirements.txt` |
| Start backend | `uvicorn backend.main:app --reload` |
| Start frontend | `streamlit run frontend/app.py` |
| Reset data | `rm expenses.db` |
| List all expenses | `curl http://sde-assessment-app-production.up.railway.app/expenses` |
| Filter by Food | `curl "http://sde-assessment-app-production.up.railway.app/expenses?category=Food"` |
| Sort by date | `curl "http://sde-assessment-app-production.up.railway.app/expenses?sort=date_desc"` |

---

## FAQ

**Q: Can I use this for real?**
A: Yes. It's production-ready for personal use.

**Q: What if my network dies?**
A: Just retry. Idempotency handles it—no duplicates.

**Q: Can I edit or delete expenses?**
A: Not yet. It's MVP scope. Could add later.

**Q: Can multiple people use this?**
A: No, single-user. Add auth if you need multi-user.

**Q: How do I backup my data?**
A: Copy `expenses.db` somewhere safe.

**Q: How do I restore a backup?**
A: Replace `expenses.db` with your backup.

**Q: Can I use this with Postgres instead of SQLite?**
A: Yes, change the connection string in `backend/main.py`.

**Q: Is my data encrypted?**
A: No, it's stored as plain SQLite file. For sensitive data, encrypt the file.

---

## Project Stats

- **Backend:** ~89 lines (FastAPI)
- **Frontend:** ~110 lines (Streamlit)
- **Total:** ~200 lines (intentionally minimal)
- **Dependencies:** 5 (FastAPI, Streamlit, SQLAlchemy, Pydantic, Uvicorn)
- **Database:** SQLite (one file)
- **Setup time:** 2 minutes
- **First expense:** 30 seconds

---

## What You'll Learn From This

1. **Idempotency** - How to handle retries safely
2. **Money handling** - Why integers > floats
3. **Real-world design** - Network failures are normal
4. **API design** - Simple RESTful endpoints
5. **Database design** - Sensible schema
6. **Clean code** - Simple, readable, maintainable

Perfect for learning or as a portfolio project!

---

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Backend | FastAPI | Modern, fast, built for APIs |
| Frontend | Streamlit | Beautiful UI, rapid development |
| Database | SQLite | Zero setup, perfect for personal projects |
| ORM | SQLAlchemy | Easy, readable database code |
| Validation | Pydantic | Automatic input validation |

---

## Next Steps

### Want More Features?
- Month/year filtering
- CSV import/export
- Monthly spending charts
- Multi-user support
- Mobile app

### Want to Contribute?
- Fork it
- Make improvements
- Submit a pull request

---

## License

MIT - Use it, modify it, share it. It's yours!

---

**Built for personal finance tracking.**

Have questions? Dive into the code—it's short and clean!
