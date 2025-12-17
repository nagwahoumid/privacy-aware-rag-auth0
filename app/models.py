"""
Data models for our RAG bot.

Think of these like cookie cutters - they define the shape of our data.
"""

from pydantic import BaseModel
from typing import List, Optional


class User(BaseModel):
    """
    A user in our system.
    
    Like a name tag that says who you are and what you can do.
    """
    id: str
    name: str
    role: str  # "employee" or "manager"
    department: str


class Document(BaseModel):
    """
    A document in our knowledge base.
    
    Like a book in a library, it has a title, content, and rules about who can read it.
    """
    id: str
    title: str
    content: str
    is_sensitive: bool  # True = needs special permission, False = anyone can read
    department: Optional[str] = None  # Which department owns this document


class QueryRequest(BaseModel):
    """
    What the user asks our bot.
    
    Like writing a question on a piece of paper.
    """
    user_id: str
    question: str


class QueryResponse(BaseModel):
    """
    What our bot answers back.
    
    Like the bot writing an answer on the paper.
    """
    answer: str
    retrieved_documents: List[str]  # Which documents we looked at
    blocked_documents: List[str]  # Which documents we couldn't look at (no permission)

