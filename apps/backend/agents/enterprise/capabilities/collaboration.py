"""Collaboration capability for enterprise agents.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from enum import Enum
import uuid


class MessageType(str, Enum):
    """Type of collaboration message."""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    HANDOFF = "handoff"
    STATUS = "status"
    ERROR = "error"


class Priority(str, Enum):
    """Message priority."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Message:
    """A collaboration message between agents."""
    id: str = ""
    sender_id: str = ""
    recipient_id: str = ""  # Empty for broadcasts
    message_type: MessageType = MessageType.REQUEST
    content: Dict[str, Any] = field(default_factory=dict)
    priority: Priority = Priority.NORMAL
    timestamp: Optional[datetime] = None
    correlation_id: Optional[str] = None  # For request-response pairing
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
        }
    
    def create_response(
        self,
        sender_id: str,
        content: Dict[str, Any],
    ) -> "Message":
        """Create a response to this message."""
        return Message(
            sender_id=sender_id,
            recipient_id=self.sender_id,
            message_type=MessageType.RESPONSE,
            content=content,
            correlation_id=self.id,
        )


@dataclass
class Conversation:
    """A conversation thread between agents."""
    id: str = ""
    participants: List[str] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    started_at: Optional[datetime] = None
    topic: str = ""
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.started_at is None:
            self.started_at = datetime.now()
    
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
        if message.sender_id not in self.participants:
            self.participants.append(message.sender_id)
        if message.recipient_id and message.recipient_id not in self.participants:
            self.participants.append(message.recipient_id)
    
    def get_context(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation context."""
        return [m.to_dict() for m in self.messages[-limit:]]


class CollaborationCapability:
    """Provides inter-agent collaboration capabilities.
    
    Enables agents to communicate, delegate tasks,
    and coordinate work.
    """
    
    def __init__(self):
        """Initialize the capability."""
        self._conversations: Dict[str, Conversation] = {}
        self._message_handlers: Dict[str, Callable] = {}
        self._pending_responses: Dict[str, Message] = {}
    
    def create_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: Dict[str, Any],
        message_type: MessageType = MessageType.REQUEST,
        priority: Priority = Priority.NORMAL,
    ) -> Message:
        """Create a new message.
        
        Args:
            sender_id: ID of sending agent
            recipient_id: ID of receiving agent
            content: Message content
            message_type: Type of message
            priority: Message priority
            
        Returns:
            Created message
        """
        return Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            priority=priority,
        )
    
    def create_broadcast(
        self,
        sender_id: str,
        content: Dict[str, Any],
        priority: Priority = Priority.NORMAL,
    ) -> Message:
        """Create a broadcast message to all agents.
        
        Args:
            sender_id: ID of sending agent
            content: Message content
            priority: Message priority
            
        Returns:
            Broadcast message
        """
        return Message(
            sender_id=sender_id,
            recipient_id="",  # Empty = broadcast
            message_type=MessageType.BROADCAST,
            content=content,
            priority=priority,
        )
    
    def create_handoff(
        self,
        sender_id: str,
        recipient_id: str,
        task: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Message:
        """Create a task handoff message.
        
        Args:
            sender_id: ID of handing off agent
            recipient_id: ID of receiving agent
            task: Task details
            context: Context for the task
            
        Returns:
            Handoff message
        """
        return Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.HANDOFF,
            content={
                "task": task,
                "context": context,
            },
            priority=Priority.HIGH,
        )
    
    def start_conversation(
        self,
        topic: str,
        initial_message: Message,
    ) -> Conversation:
        """Start a new conversation.
        
        Args:
            topic: Conversation topic
            initial_message: First message
            
        Returns:
            New conversation
        """
        conversation = Conversation(topic=topic)
        conversation.add_message(initial_message)
        self._conversations[conversation.id] = conversation
        return conversation
    
    def add_to_conversation(
        self,
        conversation_id: str,
        message: Message,
    ) -> bool:
        """Add a message to an existing conversation.
        
        Args:
            conversation_id: Conversation ID
            message: Message to add
            
        Returns:
            True if successful
        """
        conversation = self._conversations.get(conversation_id)
        if conversation:
            conversation.add_message(message)
            return True
        return False
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self._conversations.get(conversation_id)
    
    def register_handler(
        self,
        message_type: MessageType,
        handler: Callable[[Message], Optional[Message]],
    ) -> None:
        """Register a message handler.
        
        Args:
            message_type: Type of message to handle
            handler: Handler function
        """
        self._message_handlers[message_type.value] = handler
    
    def route_message(
        self,
        message: Message,
    ) -> Optional[Message]:
        """Route a message to its handler.
        
        Args:
            message: Message to route
            
        Returns:
            Response message if any
        """
        handler = self._message_handlers.get(message.message_type.value)
        if handler:
            return handler(message)
        return None
    
    def create_delegation(
        self,
        from_agent: str,
        to_agent: str,
        task_name: str,
        task_context: Dict[str, Any],
        expected_output: str,
    ) -> Message:
        """Create a task delegation message.
        
        Args:
            from_agent: Delegating agent ID
            to_agent: Target agent ID
            task_name: Name of the task
            task_context: Task context/input
            expected_output: Description of expected output
            
        Returns:
            Delegation message
        """
        return self.create_handoff(
            sender_id=from_agent,
            recipient_id=to_agent,
            task={
                "name": task_name,
                "expected_output": expected_output,
            },
            context=task_context,
        )
    
    def summarize_conversation(
        self,
        conversation_id: str,
    ) -> Dict[str, Any]:
        """Get a summary of a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation summary
        """
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return {"error": "Conversation not found"}
        
        return {
            "id": conversation.id,
            "topic": conversation.topic,
            "participants": conversation.participants,
            "message_count": len(conversation.messages),
            "started_at": conversation.started_at.isoformat() if conversation.started_at else None,
            "message_types": [
                m.message_type.value for m in conversation.messages
            ],
        }
    
    def clear_conversations(self) -> None:
        """Clear all conversations."""
        self._conversations.clear()
