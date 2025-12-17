"""
Main FastAPI application.

This is the web server that handles requests.
Think of it like a restaurant: customers (users) come in, ask questions (queries),
and we serve answers (responses).
"""

from fastapi import FastAPI, HTTPException
from app.models import User, QueryRequest, QueryResponse
from app.rag import rag_system

# Create the FastAPI app
app = FastAPI(
    title="Privacy-Aware RAG Bot",
    description="A RAG bot that enforces document-level access control using Auth0 FGA",
    version="1.0.0"
)

# Mock users database
# In a real app, this would come from Auth0 or a database
MOCK_USERS = {
    "employee_1": User(
        id="employee_1",
        name="Alice Employee",
        role="employee",
        department="Engineering"
    ),
    "manager_1": User(
        id="manager_1",
        name="Bob Manager",
        role="manager",
        department="Engineering"
    ),
}


@app.get("/")
def root():
    """
    Welcome message.
    
    Like a sign on the door saying "Welcome to our RAG bot!"
    """
    return {
        "message": "Privacy-Aware RAG Bot API",
        "description": "Ask questions and get answers, but only from documents you're allowed to see!",
        "endpoints": {
            "/query": "POST - Ask a question (requires user_id and question)",
            "/users": "GET - List available mock users",
            "/health": "GET - Check if the server is running"
        }
    }


@app.get("/health")
def health_check():
    """Check if the server is running."""
    return {"status": "healthy"}


@app.get("/users")
def list_users():
    """
    List all available mock users.
    
    This helps you test with different users (employee vs manager).
    """
    return {
        "users": [
            {
                "id": user.id,
                "name": user.name,
                "role": user.role,
                "department": user.department
            }
            for user in MOCK_USERS.values()
        ]
    }


@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    """
    Ask a question to the RAG bot.
    
    This is the MAIN endpoint that demonstrates privacy-aware RAG!
    
    How it works:
    1. User asks a question
    2. We find relevant documents
    3. We check Auth0 FGA permissions for each document
    4. We only use documents the user CAN access
    5. We generate an answer from allowed documents only
    
    If a document is blocked, it's like it doesn't exist for that user!
    """
    # Get the user
    if request.user_id not in MOCK_USERS:
        raise HTTPException(
            status_code=404,
            detail=f"User {request.user_id} not found. Use /users to see available users."
        )
    
    user = MOCK_USERS[request.user_id]
    
    # Ask the RAG system (which checks permissions internally)
    response = rag_system.answer_question(user, request.question)
    
    return response


@app.get("/demo")
def demo():
    """
    Run a quick demo showing the difference between employee and manager access.
    
    This is perfect for judges to see the privacy controls in action!
    """
    demo_question = "What is the budget for Q4?"
    
    # Try as employee (should be blocked from sensitive docs)
    employee_response = rag_system.answer_question(
        MOCK_USERS["employee_1"],
        demo_question
    )
    
    # Try as manager (should have access)
    manager_response = rag_system.answer_question(
        MOCK_USERS["manager_1"],
        demo_question
    )
    
    return {
        "question": demo_question,
        "employee_response": {
            "answer": employee_response.answer,
            "retrieved_documents": employee_response.retrieved_documents,
            "blocked_documents": employee_response.blocked_documents,
            "note": "Employee cannot access sensitive budget documents!"
        },
        "manager_response": {
            "answer": manager_response.answer,
            "retrieved_documents": manager_response.retrieved_documents,
            "blocked_documents": manager_response.blocked_documents,
            "note": "Manager can access sensitive budget documents!"
        },
        "demonstration": "This shows how Auth0 FGA blocks unauthorized document access!"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

