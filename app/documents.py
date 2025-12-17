"""
Document storage and management.

Think of this like a library with books (documents).
We store documents here and can search through them.
"""

from typing import List, Dict
from app.models import Document


class DocumentStore:
    """
    Our document library.
    
    Stores all documents and lets us search for them.
    """
    
    def __init__(self):
        # In a real app, this would be a database or vector store
        # For demo: we just use a list
        self.documents: List[Document] = []
        self._load_sample_documents()
    
    def _load_sample_documents(self):
        """
        Load some example documents for our demo.
        
        We create:
        - Public documents (anyone can read)
        - Sensitive documents (only managers can read)
        """
        self.documents = [
            # PUBLIC DOCUMENTS - anyone can read these
            Document(
                id="doc_public_1",
                title="Company Holiday Schedule",
                content="The company will be closed on December 25th and January 1st. All employees get 10 vacation days per year.",
                is_sensitive=False
            ),
            Document(
                id="doc_public_2",
                title="Office Policies",
                content="The office hours are 9 AM to 5 PM. Remote work is allowed on Fridays. Dress code is business casual.",
                is_sensitive=False
            ),
            Document(
                id="doc_public_3",
                title="Health Benefits",
                content="All employees are eligible for health insurance. The company covers 80% of premiums. Dental and vision are included.",
                is_sensitive=False
            ),
            
            # SENSITIVE DOCUMENTS - only managers can read these
            Document(
                id="doc_sensitive_1",
                title="Q4 Budget Report",
                content="The Q4 budget allocation is $500,000. Marketing gets $150k, Engineering gets $200k, Sales gets $100k, and Operations gets $50k.",
                is_sensitive=True
            ),
            Document(
                id="doc_sensitive_2",
                title="Salary Information",
                content="Manager salaries range from $120k to $180k. Senior engineers earn $100k-$140k. Junior employees start at $60k.",
                is_sensitive=True
            ),
            Document(
                id="doc_sensitive_3",
                title="Executive Strategy",
                content="The company plans to expand to 3 new markets in 2024. We're considering an IPO in 2025. Confidential discussions with investors are ongoing.",
                is_sensitive=True
            ),
        ]
    
    def get_all_documents(self) -> List[Document]:
        """Get all documents in the store."""
        return self.documents
    
    def search_documents(self, query: str) -> List[Document]:
        """
        Simple keyword search through documents.
        
        In a real RAG system, this would use vector embeddings and semantic search.
        For demo: we just check if query words appear in document content.
        
        Returns documents that might be relevant to the query.
        """
        query_lower = query.lower()
        relevant_docs = []
        
        for doc in self.documents:
            # Simple keyword matching
            if (query_lower in doc.content.lower() or 
                query_lower in doc.title.lower()):
                relevant_docs.append(doc)
        
        # If no matches, return all documents (for demo purposes)
        if not relevant_docs:
            return self.documents[:3]  # Return first 3 as example
        
        return relevant_docs
    
    def get_document_by_id(self, doc_id: str) -> Document:
        """Get a specific document by its ID."""
        for doc in self.documents:
            if doc.id == doc_id:
                return doc
        raise ValueError(f"Document {doc_id} not found")


# Global document store instance
document_store = DocumentStore()

