"""SalesIQ Chat Handler
Handles incoming SalesIQ messages and integrates with Zoho Desk
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from src.hybrid_chatbot import HybridChatbot
from src.zoho_desk_integration import ZohoDeskIntegration

class SalesIQHandler:
    """Handles SalesIQ chat messages and ticket creation"""
    
    def __init__(self):
        self.chatbot = HybridChatbot()
        self.zoho_desk = ZohoDeskIntegration()
        self.chat_sessions: Dict[str, Dict[str, Any]] = {}
    
    def handle_incoming_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming SalesIQ message"""
        try:
            # Validate payload
            if not payload:
                return {
                    "status": "error",
                    "error": "Empty payload received",
                    "response": "Unable to process empty message"
                }
            
            chat_id = payload.get("chat_id", "")
            visitor_id = payload.get("visitor_id", "")
            message = payload.get("message", "")
            visitor_email = payload.get("visitor_email", "")
            visitor_name = payload.get("visitor_name", "Unknown")
            
            if not message:
                return {
                    "status": "ignored",
                    "reason": "No message content",
                    "response": "No message to process"
                }
            
            # Get or create session
            session_key = f"salesiq_{chat_id}"
            if session_key not in self.chat_sessions:
                self.chat_sessions[session_key] = {
                    "chat_id": chat_id,
                    "visitor_id": visitor_id,
                    "visitor_email": visitor_email,
                    "visitor_name": visitor_name,
                    "ticket_id": None,
                    "messages": [],
                    "created_at": datetime.now().isoformat()
                }
            
            session = self.chat_sessions[session_key]
            
            # Store message
            session["messages"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Process with chatbot
            result = self.chatbot.process_query(
                message,
                conversation_history=session.get("messages", []),
                session_id=session_key,
                user_id=visitor_email
            )
            
            # Store bot response
            session["messages"].append({
                "role": "assistant",
                "content": result.get("response"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Check if workflow was triggered
            if result.get("source") == "automation_workflow":
                return self._handle_workflow_response(result, session, payload)
            
            # Regular response
            return {
                "status": "success",
                "response": result.get("response"),
                "escalate": result.get("escalate"),
                "confidence": result.get("confidence"),
                "source": result.get("source"),
                "quick_actions": result.get("quick_actions", [])
            }
        
        except Exception as e:
            print(f"[SalesIQ Handler] Error processing message: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "response": "I apologize, but I encountered an error processing your message. Please try again or contact support."
            }
    
    def _handle_workflow_response(self, result: Dict[str, Any], session: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow response and create ticket"""
        workflow_type = result.get("workflow_type")
        workflow_data = result.get("workflow_data", {})
        
        # Prepare workflow data for ticket
        ticket_data = {
            "workflow_type": workflow_type,
            "category": workflow_type.replace("_", " ").title(),
            "subject": f"{workflow_type.replace('_', ' ').title()} - {session.get('visitor_name', 'User')}",
            "email": session.get("visitor_email"),
            "name": session.get("visitor_name"),
            "phone": payload.get("visitor_phone", ""),
            "priority": self._get_priority_for_workflow(workflow_type),
            "details": {
                "workflow_step": workflow_data.get("step_id"),
                "workflow_type": workflow_type,
                "chat_messages": session.get("messages", [])
            },
            "tags": [workflow_type, "SalesIQ", "Automated"]
        }
        
        # Create ticket in Zoho Desk
        ticket_result = self.zoho_desk.create_ticket_from_workflow(
            ticket_data,
            chat_id=session.get("chat_id"),
            visitor_id=session.get("visitor_id")
        )
        
        if ticket_result.get("success"):
            ticket_id = ticket_result.get("ticket_id")
            ticket_number = ticket_result.get("ticket_number")
            
            # Store ticket ID in session
            session["ticket_id"] = ticket_id
            
            # Prepare response with ticket info
            response_message = f"""
            ✅ Your request has been logged!
            
            **Ticket ID:** {ticket_id}
            **Ticket Number:** {ticket_number}
            
            Our support team has been notified and will assist you shortly.
            You'll receive updates via email at {session.get('visitor_email')}.
            
            {result.get('response')}
            """
            
            return {
                "status": "success",
                "response": response_message.strip(),
                "ticket_created": True,
                "ticket_id": ticket_id,
                "ticket_number": ticket_number,
                "escalate": False,
                "workflow_type": workflow_type,
                "quick_actions": result.get("quick_actions", [])
            }
        else:
            # Fallback response if ticket creation fails
            return {
                "status": "success",
                "response": result.get("response"),
                "ticket_created": False,
                "error": ticket_result.get("error"),
                "escalate": True,
                "workflow_type": workflow_type
            }
    
    def handle_workflow_step(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow step response"""
        try:
            chat_id = payload.get("chat_id", "")
            step_id = payload.get("step_id", "")
            response = payload.get("response", "")
            
            session_key = f"salesiq_{chat_id}"
            
            if session_key not in self.chat_sessions:
                return {"status": "error", "error": "Session not found"}
            
            session = self.chat_sessions[session_key]
            
            # Process workflow step
            result = self.chatbot.process_workflow_response(
                session_key,
                step_id,
                response
            )
            
            # Store response
            session["messages"].append({
                "role": "user",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            session["messages"].append({
                "role": "assistant",
                "content": result.get("response"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Check if workflow completed
            if result.get("ticket_id"):
                session["ticket_id"] = result.get("ticket_id")
                
                return {
                    "status": "success",
                    "response": result.get("response"),
                    "ticket_created": True,
                    "ticket_id": result.get("ticket_id"),
                    "ticket_number": result.get("ticket_number"),
                    "eta": result.get("eta")
                }
            
            return {
                "status": "success",
                "response": result.get("response"),
                "workflow_data": result.get("workflow_data")
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_ticket_for_chat(self, chat_id: str) -> Dict[str, Any]:
        """Get ticket associated with a chat"""
        session_key = f"salesiq_{chat_id}"
        
        if session_key in self.chat_sessions:
            session = self.chat_sessions[session_key]
            if session.get("ticket_id"):
                return {
                    "success": True,
                    "ticket_id": session.get("ticket_id"),
                    "chat_id": chat_id
                }
        
        return {
            "success": False,
            "error": "No ticket found for this chat"
        }
    
    def send_ticket_update_to_chat(self, chat_id: str, message: str) -> Dict[str, Any]:
        """Send ticket update message to SalesIQ chat"""
        session_key = f"salesiq_{chat_id}"
        
        if session_key not in self.chat_sessions:
            return {"success": False, "error": "Session not found"}
        
        session = self.chat_sessions[session_key]
        
        # Store message
        session["messages"].append({
            "role": "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": "Update sent to chat"
        }
    
    def _get_priority_for_workflow(self, workflow_type: str) -> str:
        """Determine priority based on workflow type"""
        high_priority = [
            "server_reboot",
            "account_locked",
            "server_slowness",
            "rdp_connection"
        ]
        
        medium_priority = [
            "password_reset",
            "email_issues",
            "qb_issues",
            "printer_issues"
        ]
        
        if workflow_type in high_priority:
            return "High"
        elif workflow_type in medium_priority:
            return "Medium"
        else:
            return "Low"
    
    def get_session_info(self, chat_id: str) -> Dict[str, Any]:
        """Get session information"""
        session_key = f"salesiq_{chat_id}"
        
        if session_key in self.chat_sessions:
            session = self.chat_sessions[session_key]
            return {
                "success": True,
                "chat_id": chat_id,
                "visitor_name": session.get("visitor_name"),
                "visitor_email": session.get("visitor_email"),
                "ticket_id": session.get("ticket_id"),
                "message_count": len(session.get("messages", [])),
                "created_at": session.get("created_at")
            }
        
        return {
            "success": False,
            "error": "Session not found"
        }
    
    def close_session(self, chat_id: str) -> Dict[str, Any]:
        """Close a chat session"""
        session_key = f"salesiq_{chat_id}"
        
        if session_key in self.chat_sessions:
            session = self.chat_sessions[session_key]
            
            # If ticket exists, add closing comment
            if session.get("ticket_id"):
                closing_comment = f"""
                Chat session closed.
                Total messages: {len(session.get('messages', []))}
                Duration: {datetime.now().isoformat()}
                """
                
                self.zoho_desk.add_comment_to_ticket(
                    session.get("ticket_id"),
                    closing_comment.strip(),
                    is_internal=True
                )
            
            # Remove session
            del self.chat_sessions[session_key]
            
            return {
                "success": True,
                "message": "Session closed"
            }
        
        return {
            "success": False,
            "error": "Session not found"
        }
