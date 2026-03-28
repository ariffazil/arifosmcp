"""
Merkle Chain - Cryptographic provenance for arifOS.

The Merkle chain provides tamper-evident logging of all operations,
enabling verification of session continuity and operation history.
"""

import hashlib
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MerkleNode(BaseModel):
    """
    A single node in the Merkle tree.
    
    Each node contains a hash of its data and references to
    its parent, enabling chain verification.
    """
    node_id: str = Field(..., description="Unique node identifier")
    data_hash: str = Field(..., description="Hash of node data")
    parent_hash: Optional[str] = Field(
        default=None,
        description="Hash of parent node"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When node was created"
    )
    operation_type: str = Field(
        ...,
        description="Type of operation this node represents"
    )
    session_id: str = Field(..., description="Session this node belongs to")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional node metadata"
    )
    
    def compute_combined_hash(self) -> str:
        """
        Compute the combined hash including parent reference.
        
        This creates the chain linkage - changing any node
        invalidates all subsequent nodes.
        """
        data = {
            "node_id": self.node_id,
            "data_hash": self.data_hash,
            "parent_hash": self.parent_hash,
            "timestamp": self.timestamp.isoformat(),
            "operation_type": self.operation_type,
            "session_id": self.session_id,
        }
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
    
    def verify_integrity(self, parent_node: Optional["MerkleNode"]) -> bool:
        """
        Verify this node's integrity against its parent.
        
        Args:
            parent_node: The parent node to verify against
            
        Returns:
            True if integrity is valid
        """
        if parent_node is None:
            # Root node - no parent to verify
            return self.parent_hash is None
        
        expected_parent_hash = parent_node.compute_combined_hash()
        return self.parent_hash == expected_parent_hash


class MerkleTree:
    """
    A Merkle tree for a single session.
    
    Maintains all operations within a session as a linked
    chain of hashed nodes for tamper detection.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.nodes: List[MerkleNode] = []
        self.node_index: Dict[str, int] = {}
    
    def add_node(
        self,
        operation_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> MerkleNode:
        """
        Add a new node to the tree.
        
        Args:
            operation_type: Type of operation
            data: Node data (will be hashed)
            metadata: Additional metadata
            
        Returns:
            The created MerkleNode
        """
        # Compute data hash
        data_hash = hashlib.sha256(
            json.dumps(data, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        # Get parent hash (previous node)
        parent_hash = None
        if self.nodes:
            parent_hash = self.nodes[-1].compute_combined_hash()
        
        # Create node
        node = MerkleNode(
            node_id=f"{self.session_id}_{len(self.nodes)}",
            data_hash=data_hash,
            parent_hash=parent_hash,
            operation_type=operation_type,
            session_id=self.session_id,
            metadata=metadata or {}
        )
        
        # Add to tree
        self.node_index[node.node_id] = len(self.nodes)
        self.nodes.append(node)
        
        return node
    
    def get_root(self) -> Optional[MerkleNode]:
        """Get the root (first) node of the tree."""
        return self.nodes[0] if self.nodes else None
    
    def get_leaf(self) -> Optional[MerkleNode]:
        """Get the leaf (most recent) node of the tree."""
        return self.nodes[-1] if self.nodes else None
    
    def get_node(self, node_id: str) -> Optional[MerkleNode]:
        """Get a node by its ID."""
        index = self.node_index.get(node_id)
        if index is not None:
            return self.nodes[index]
        return None
    
    def verify_chain(self) -> Dict[str, Any]:
        """
        Verify the integrity of the entire chain.
        
        Returns:
            Verification result with status and details
        """
        if not self.nodes:
            return {"valid": True, "node_count": 0, "errors": []}
        
        errors = []
        
        for i, node in enumerate(self.nodes):
            parent = self.nodes[i - 1] if i > 0 else None
            
            if not node.verify_integrity(parent):
                errors.append({
                    "node_id": node.node_id,
                    "index": i,
                    "error": "Parent hash mismatch"
                })
        
        return {
            "valid": len(errors) == 0,
            "node_count": len(self.nodes),
            "errors": errors
        }
    
    def get_merkle_root_hash(self) -> Optional[str]:
        """
        Get the Merkle root hash for the entire tree.
        
        This is the cryptographic commitment to all nodes.
        """
        if not self.nodes:
            return None
        
        # Combine all node hashes
        combined = "".join(n.compute_combined_hash() for n in self.nodes)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def to_list(self) -> List[Dict[str, Any]]:
        """Export tree as a list of node dictionaries."""
        return [node.model_dump() for node in self.nodes]


class MerkleChain:
    """
    Global Merkle chain manager for all sessions.
    
    Maintains Merkle trees for multiple sessions and provides
    cross-session verification capabilities.
    """
    
    def __init__(self):
        self.trees: Dict[str, MerkleTree] = {}
        self.global_nodes: List[MerkleNode] = []
    
    def get_or_create_tree(self, session_id: str) -> MerkleTree:
        """Get existing tree or create new one for session."""
        if session_id not in self.trees:
            self.trees[session_id] = MerkleTree(session_id)
        return self.trees[session_id]
    
    def add_operation(
        self,
        session_id: str,
        operation_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> MerkleNode:
        """
        Add an operation to a session's Merkle tree.
        
        Args:
            session_id: Session identifier
            operation_type: Type of operation
            data: Operation data
            metadata: Additional metadata
            
        Returns:
            The created MerkleNode
        """
        tree = self.get_or_create_tree(session_id)
        node = tree.add_node(operation_type, data, metadata)
        
        # Also add to global chain for cross-session verification
        self.global_nodes.append(node)
        
        return node
    
    def verify_session(self, session_id: str) -> Dict[str, Any]:
        """Verify the Merkle chain for a specific session."""
        tree = self.trees.get(session_id)
        if not tree:
            return {
                "valid": False,
                "error": f"Session {session_id} not found"
            }
        return tree.verify_chain()
    
    def verify_all(self) -> Dict[str, Any]:
        """Verify all session chains."""
        results = {}
        all_valid = True
        
        for session_id, tree in self.trees.items():
            result = tree.verify_chain()
            results[session_id] = result
            if not result["valid"]:
                all_valid = False
        
        return {
            "all_valid": all_valid,
            "session_results": results,
            "total_sessions": len(self.trees),
            "total_nodes": len(self.global_nodes)
        }
    
    def get_session_root(self, session_id: str) -> Optional[str]:
        """Get the Merkle root hash for a session."""
        tree = self.trees.get(session_id)
        if tree:
            return tree.get_merkle_root_hash()
        return None
    
    def get_global_root(self) -> Optional[str]:
        """Get the global Merkle root across all sessions."""
        if not self.global_nodes:
            return None
        
        combined = "".join(n.compute_combined_hash() for n in self.global_nodes)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get operation history for a session."""
        tree = self.trees.get(session_id)
        if tree:
            return tree.to_list()
        return []
    
    def export_state(self) -> Dict[str, Any]:
        """Export entire chain state for persistence."""
        return {
            "sessions": {
                sid: tree.to_list()
                for sid, tree in self.trees.items()
            },
            "global_root": self.get_global_root(),
            "total_nodes": len(self.global_nodes)
        }
