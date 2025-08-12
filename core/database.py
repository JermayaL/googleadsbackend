"""
Firebase Firestore database configuration and utilities - FIXED FOR 2025 API
Updated with proper timestamp handling based on 2025 API documentation
"""

from google.cloud import firestore
from google.cloud.firestore import Client
from typing import Dict, Any, List, Optional
import firebase_admin
from firebase_admin import credentials
from config.settings import settings
import datetime

class FirestoreDB:
    def __init__(self):
        self.client = None
        self._initialize_firestore()
    
    def _initialize_firestore(self):
        """Initialize Firestore client using 2025 best practices"""
        try:
            # Initialize Firebase Admin SDK if not already done
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
                firebase_admin.initialize_app(cred, {
                    'projectId': settings.FIREBASE_PROJECT_ID
                })
            
            # Initialize Firestore client - Updated for 2025
            self.client = firestore.Client(project=settings.FIREBASE_PROJECT_ID)
            print("✅ Firestore client initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Firestore: {e}")
            raise
    
    async def create_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> str:
        """Create a new document - FIXED for 2025 API"""
        try:
            # Ensure any timestamp fields use datetime objects
            processed_data = self._process_timestamps(data)
            
            doc_ref = self.client.collection(collection).document(document_id)
            doc_ref.set(processed_data)
            return document_id
        except Exception as e:
            raise Exception(f"Error creating document: {e}")
    
    async def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        try:
            doc_ref = self.client.collection(collection).document(document_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            raise Exception(f"Error getting document: {e}")
    
    async def update_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> None:
        """Update a document - FIXED for 2025 API"""
        try:
            # Ensure any timestamp fields use datetime objects
            processed_data = self._process_timestamps(data)
            
            doc_ref = self.client.collection(collection).document(document_id)
            doc_ref.update(processed_data)
        except Exception as e:
            raise Exception(f"Error updating document: {e}")
    
    async def delete_document(self, collection: str, document_id: str) -> None:
        """Delete a document"""
        try:
            doc_ref = self.client.collection(collection).document(document_id)
            doc_ref.delete()
        except Exception as e:
            raise Exception(f"Error deleting document: {e}")
    
    async def query_collection(
        self, 
        collection: str, 
        where_clauses: List[tuple] = None,
        order_by: tuple = None,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """Query a collection with filters"""
        try:
            query = self.client.collection(collection)
            
            if where_clauses:
                for field, operator, value in where_clauses:
                    query = query.where(field, operator, value)
            
            if order_by:
                field, direction = order_by
                query = query.order_by(field, direction=direction)
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
            
        except Exception as e:
            raise Exception(f"Error querying collection: {e}")
    
    def _process_timestamps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data to ensure proper timestamp handling for 2025 API
        Converts any SERVER_TIMESTAMP references to current datetime
        """
        processed_data = {}
        
        for key, value in data.items():
            if hasattr(value, '__name__') and 'SERVER_TIMESTAMP' in str(value):
                # FIXED: Convert SERVER_TIMESTAMP to current datetime
                processed_data[key] = datetime.datetime.now()
            elif isinstance(value, dict):
                # Recursively process nested dictionaries
                processed_data[key] = self._process_timestamps(value)
            elif isinstance(value, list):
                # Process lists that might contain dictionaries
                processed_data[key] = [
                    self._process_timestamps(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                processed_data[key] = value
        
        return processed_data
    
    def get_collection_reference(self, collection: str):
        """Get a collection reference for advanced operations"""
        return self.client.collection(collection)
    
    def batch_operation(self):
        """Get a batch object for batch operations"""
        return self.client.batch()
    
    def transaction(self):
        """Get a transaction object"""
        return self.client.transaction()
    
    # Additional helper methods for common operations
    async def collection_exists(self, collection: str) -> bool:
        """Check if a collection exists and has documents"""
        try:
            docs = self.client.collection(collection).limit(1).stream()
            return len(list(docs)) > 0
        except Exception:
            return False
    
    async def get_all_documents(self, collection: str) -> List[Dict[str, Any]]:
        """Get all documents in a collection"""
        try:
            docs = self.client.collection(collection).stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            raise Exception(f"Error getting all documents: {e}")
    
    async def count_documents(self, collection: str) -> int:
        """Count documents in a collection"""
        try:
            docs = self.client.collection(collection).stream()
            return len(list(docs))
        except Exception as e:
            raise Exception(f"Error counting documents: {e}")
    
    def close(self):
        """Close the Firestore client connection"""
        if self.client:
            # Note: The Python Firestore client doesn't have an explicit close method
            # Connections are managed automatically
            self.client = None