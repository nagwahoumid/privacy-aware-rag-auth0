"""
RAG (Retrieval-Augmented Generation) system with privacy controls.

RAG means: 
1. Find relevant documents (Retrieval)
2. Use them to answer questions (Augmented Generation)

THE KEY: We check permissions BEFORE retrieving documents!
If a user can't access a document, we pretend it doesn't exist.
"""

from typing import List
from app.models import User, Document, QueryResponse
from app.documents import document_store
from app.auth import Auth0FGAClient


class PrivacyAwareRAG:
    """
    Our smart bot that answers questions using documents.
    
    But it's PRIVACY-AWARE: it only uses documents the user is allowed to see!
    """
    
    def __init__(self):
        self.document_store = document_store
        self.auth_client = Auth0FGAClient()
    
    def answer_question(self, user: User, question: str) -> QueryResponse:
        """
        Answer a user's question using RAG, but with privacy checks!
        
        Steps:
        1. Search for relevant documents
        2. CHECK PERMISSIONS for each document (Auth0 FGA)
        3. Only use documents the user CAN access
        4. Generate answer from allowed documents only
        
        This is the CORE of privacy-aware RAG!
        """
        # Step 1: Find documents that might answer the question
        candidate_documents = self.document_store.search_documents(question)
        
        # Step 2: CHECK PERMISSIONS BEFORE RETRIEVAL!
        # This is the critical step - we filter out documents the user can't access
        allowed_documents = []
        blocked_documents = []
        
        for doc in candidate_documents:
            # Ask Auth0 FGA: "Can this user read this document?"
            can_access = self.auth_client.can_user_access_document(user, doc)
            
            if can_access:
                # User has permission - add to allowed list
                allowed_documents.append(doc)
            else:
                # User does NOT have permission - block it!
                # This document will NOT be used in the answer
                blocked_documents.append(doc.id)
        
        # Step 3: Generate answer using ONLY allowed documents
        # In a real app, this would use an LLM (like OpenAI, Anthropic, etc.)
        # For demo: we create a simple answer
        answer = self._generate_answer(question, allowed_documents)
        
        # Step 4: Return answer with info about what was retrieved/blocked
        return QueryResponse(
            answer=answer,
            retrieved_documents=[doc.id for doc in allowed_documents],
            blocked_documents=blocked_documents
        )
    
    def _generate_answer(self, question: str, documents: List[Document]) -> str:
        """
        Generate an answer from the allowed documents.
        
        In a real app, this would call an LLM API (OpenAI, Anthropic, etc.)
        For demo: we create a simple text answer.
        """
        if not documents:
            return "I couldn't find any information you're authorized to access that answers your question."
        
        # Simple answer generation (in real app, use LLM)
        answer_parts = [f"Based on the documents I can access, here's what I found:\n"]
        
        for doc in documents:
            answer_parts.append(f"- {doc.title}: {doc.content[:100]}...")
        
        return "\n".join(answer_parts)


# Global RAG instance
rag_system = PrivacyAwareRAG()

