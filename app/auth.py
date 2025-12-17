"""
Auth0 Fine-Grained Authorization (FGA) checker.

Think of this like a security guard at a door.
Before you can enter a room (read a document), the guard checks if you have permission.
"""

from typing import Dict
from app.models import User, Document


# Mock Auth0 FGA client
# In real life, this would talk to Auth0's servers
# For this demo, we're just checking simple rules
class Auth0FGAClient:
    """
    A pretend Auth0 FGA client.
    
    In a real app, this would call Auth0's API to check permissions.
    For our demo, we use simple rules:
    - Managers can see sensitive documents
    - Employees can only see public documents
    """
    
    def __init__(self):
        # This is where we'd store Auth0 API keys in a real app
        # For demo: we just use simple rules
        pass
    
    def can_user_access_document(self, user: User, document: Document) -> bool:
        """
        Check if a user can read a document.
        
        This is THE KEY FUNCTION as it checks permissions BEFORE retrieval!
        
        Rules:
        - If document is NOT sensitive (public): everyone can read it
        - If document IS sensitive: only managers can read it
        
        Returns:
            True if user can read, False if they cannot
        """
        # Public documents: everyone can read
        if not document.is_sensitive:
            return True
        
        # Sensitive documents: only managers can read
        if document.is_sensitive and user.role == "manager":
            return True
        
        # If we get here, user is an employee trying to read sensitive doc
        # DENY ACCESS!
        return False
    
    def check_batch_permissions(
        self, user: User, documents: list[Document]
    ) -> Dict[str, bool]:
        """
        Check permissions for multiple documents at once.
        
        Like checking a list of rooms - which ones can this person enter?
        
        Returns:
            Dictionary mapping document IDs to True/False (can access or not)
        """
        permissions = {}
        for doc in documents:
            permissions[doc.id] = self.can_user_access_document(user, doc)
        return permissions

