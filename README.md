# Privacy-Aware RAG Bot with Auth0 FGA

A proof-of-concept RAG (Retrieval-Augmented Generation) bot that demonstrates **document-level access control** using Auth0 Fine-Grained Authorization (FGA). 

## 🎯 What This Does (Explained Simply)

Imagine a library with books (documents). Some books are public (anyone can read), and some are locked (only managers can read).

When you ask our bot a question:
1. It finds books that might answer your question
2. **Before opening any book**, it checks: "Does this person have permission?"
3. If YES → uses the book to answer
4. If NO → pretends the book doesn't exist (never uses it!)

This ensures sensitive documents (like salary info) are **never retrieved** for unauthorized users.

## 📁 Project Structure

```
privacy-aware-rag-auth0/
├── app/
│   ├── __init__.py          # Makes app a Python package
│   ├── main.py              # FastAPI web server (the front door)
│   ├── models.py            # Data shapes (User, Document, etc.)
│   ├── auth.py              # Auth0 FGA permission checker (the security guard)
│   ├── documents.py         # Document storage (the library)
│   └── rag.py               # RAG system with privacy checks (the smart bot)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

### 3. Test It!

**Option A: Use the Demo Endpoint (Easiest for Judges!)**

Visit: `http://localhost:8000/demo`

This shows a side-by-side comparison:
- Employee asking about budget → **BLOCKED** from sensitive docs
- Manager asking about budget → **ALLOWED** to see sensitive docs

**Option B: Use the API**

1. **List available users:**
   ```bash
   curl http://localhost:8000/users
   ```

2. **Ask a question as an employee:**
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "employee_1",
       "question": "What is the Q4 budget?"
     }'
   ```

3. **Ask the same question as a manager:**
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "manager_1",
       "question": "What is the Q4 budget?"
     }'
   ```

**Notice the difference:**
- Employee: `blocked_documents` contains sensitive doc IDs
- Manager: `blocked_documents` is empty (has access)

## 🔐 How Privacy Works

### The Critical Flow:

```
User asks question
    ↓
Find relevant documents (search)
    ↓
FOR EACH DOCUMENT:
    ↓
    Check Auth0 FGA: "Can user read this?"
    ↓
    ├─ YES → Add to allowed list
    └─ NO  → Add to blocked list (NEVER use this!)
    ↓
Generate answer using ONLY allowed documents
```

**Key Point:** Permission checks happen **BEFORE** retrieval. Blocked documents are never sent to the LLM.

### Access Rules (Current Demo):

- **Public documents** (is_sensitive=False): Everyone can read
- **Sensitive documents** (is_sensitive=True): Only managers can read

## 📊 Sample Documents

**Public (anyone can read):**
- Company Holiday Schedule
- Office Policies
- Health Benefits

**Sensitive (managers only):**
- Q4 Budget Report
- Salary Information
- Executive Strategy

## 🧪 Testing Scenarios

1. **Employee asks about holidays** → Should work (public doc)
2. **Employee asks about budget** → Should be blocked (sensitive doc)
3. **Manager asks about budget** → Should work (manager has access)
4. **Manager asks about holidays** → Should work (public doc)

## 🔧 For Production

This is a **proof-of-concept**. For production, you'd need:

1. **Real Auth0 FGA Integration:**
   - Replace mock `Auth0FGAClient` with actual OpenFGA SDK
   - Set up Auth0 FGA store and authorization model

2. **Real LLM Integration:**
   - Add OpenAI/Anthropic API calls in `rag.py`
   - Use embeddings for semantic search

3. **Real Authentication:**
   - Integrate Auth0 Authentication (not just FGA)
   - Use JWT tokens instead of mock users

4. **Vector Database:**
   - Use ChromaDB, Pinecone, or similar for document embeddings
   - Enable semantic search instead of keyword matching

## 📝 API Endpoints

- `GET /` - Welcome message and API info
- `GET /health` - Health check
- `GET /users` - List mock users
- `GET /demo` - Run demo comparison (employee vs manager)
- `POST /query` - Ask a question (requires `user_id` and `question`)

## 🎓 For Judges

**What this demonstrates:**
- ✅ Document-level access control in RAG
- ✅ Auth0 FGA integration (mocked but structured for real integration)
- ✅ Pre-retrieval permission checks (documents blocked before LLM sees them)
- ✅ Clear separation of concerns (auth, documents, RAG logic)

**Key files to review:**
- `app/auth.py` - Permission checking logic
- `app/rag.py` - How permissions are checked BEFORE retrieval
- `app/main.py` - API endpoints

## 📄 License

This is a hackathon project for MLH.
