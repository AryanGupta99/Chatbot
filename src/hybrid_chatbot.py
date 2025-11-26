"""Hybrid Chatbot Engine
Combines rule-based Zobot flows with RAG-based AI responses
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from src.rag_engine import RAGEngine
from src.workflow_engine import WorkflowExecutor
from src.automation_workflows import WorkflowType
import re

class HybridChatbot:
    """Combines Zobot rule-based flows with RAG AI responses"""
    
    def __init__(self):
        self.rag_engine = RAGEngine()
        self.zobot_qa_pairs = self._load_zobot_data()
        self.conversation_flows = self._load_conversation_flows()
        self.workflow_executor = WorkflowExecutor()
        self.automation_triggers = self._load_automation_triggers()
        
    def _load_zobot_data(self) -> List[Dict[str, Any]]:
        """Load existing Zobot Q&A pairs"""
        zobot_file = Path("data/zobot_extracted/zobot_qa_pairs.json")
        if zobot_file.exists():
            with open(zobot_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _load_automation_triggers(self) -> Dict[str, WorkflowType]:
        """Map query patterns to automation workflows"""
        return {
            "disk": WorkflowType.DISK_UPGRADE,
            "storage": WorkflowType.DISK_UPGRADE,
            "upgrade": WorkflowType.DISK_UPGRADE,
            "password": WorkflowType.PASSWORD_RESET,
            "reset": WorkflowType.PASSWORD_RESET,
            "forgot": WorkflowType.PASSWORD_RESET,
            "locked": WorkflowType.ACCOUNT_LOCKED,
            "account locked": WorkflowType.ACCOUNT_LOCKED,
            "add user": WorkflowType.USER_MANAGEMENT,
            "delete user": WorkflowType.USER_MANAGEMENT,
            "new employee": WorkflowType.USER_MANAGEMENT,
            "monitor": WorkflowType.MONITOR_SETUP,
            "display": WorkflowType.MONITOR_SETUP,
            "printer": WorkflowType.PRINTER_ISSUES,
            "print": WorkflowType.PRINTER_ISSUES,
            "slow": WorkflowType.SERVER_SLOWNESS,
            "performance": WorkflowType.SERVER_SLOWNESS,
            "rdp": WorkflowType.RDP_CONNECTION,
            "remote": WorkflowType.RDP_CONNECTION,
            "reboot": WorkflowType.SERVER_REBOOT,
            "restart": WorkflowType.SERVER_REBOOT,
            "mfa": WorkflowType.QB_MFA,
            "security code": WorkflowType.QB_MFA,
            "email": WorkflowType.EMAIL_ISSUES,
            "outlook": WorkflowType.EMAIL_ISSUES,
            "quickbooks": WorkflowType.QB_ISSUES,
            "qb": WorkflowType.QB_ISSUES,
            "windows update": WorkflowType.WINDOWS_UPDATE,
            "update failed": WorkflowType.WINDOWS_UPDATE,
        }
    
    def _load_conversation_flows(self) -> Dict[str, Any]:
        """Load conversation flows from Zobot knowledge"""
        flows = {
            "greeting": {
                "triggers": ["hi", "hello", "hey", "good morning", "good afternoon"],
                "response": "Hello! I'm AceBuddy, your AI support assistant. I'm here to help you with QuickBooks, Remote Desktop, Email, Server issues, and more. What can I help you with today?"
            },
            "quickbooks_issues": {
                "triggers": ["quickbooks", "qb", "accounting", "payroll", "invoice"],
                "follow_up": "What specific QuickBooks issue are you experiencing? (Error codes, login problems, file issues, etc.)"
            },
            "rdp_issues": {
                "triggers": ["rdp", "remote desktop", "connection", "can't connect", "remote access"],
                "follow_up": "I can help with Remote Desktop issues. Are you having trouble connecting, or is it a performance issue?"
            },
            "password_reset": {
                "triggers": ["password", "reset", "forgot", "login", "can't login", "locked out"],
                "response": "I can help you reset your password. Here's what you need to do:\n\n1. Visit our self-care portal: https://selfcare.acecloudhosting.com/\n2. Click 'Forgot Password'\n3. Enter your username or email\n4. Check your email for reset instructions\n\nIf you need immediate assistance, I can also connect you with our support team."
            },
            "email_issues": {
                "triggers": ["email", "outlook", "office 365", "mail", "smtp"],
                "follow_up": "What email issue are you experiencing? (Can't send/receive, password prompts, setup, etc.)"
            },
            "server_issues": {
                "triggers": ["server", "slow", "performance", "storage", "disk space"],
                "follow_up": "What server issue are you experiencing? (Performance, storage, connectivity, etc.)"
            },
            "billing_support": {
                "triggers": ["billing", "payment", "invoice", "subscription", "cost", "price"],
                "response": "For billing and payment inquiries, I'll connect you with our billing specialist who can provide detailed information about your account and pricing. Please hold while I transfer you.",
                "escalate": True
            }
        }
        return flows
    
    def _match_zobot_pattern(self, query: str) -> Optional[Dict[str, Any]]:
        """Check if query matches existing Zobot patterns"""
        query_lower = query.lower()
        
        # Check conversation flows first
        for flow_name, flow_data in self.conversation_flows.items():
            if any(trigger in query_lower for trigger in flow_data["triggers"]):
                return {
                    "type": "flow",
                    "flow": flow_name,
                    "data": flow_data
                }
        
        # Check Zobot Q&A pairs
        for qa_pair in self.zobot_qa_pairs:
            question = qa_pair.get("question", "").lower()
            keywords = qa_pair.get("keywords", [])
            
            # Check if query matches question or keywords
            if (question and any(word in query_lower for word in question.split()) or
                any(keyword.lower() in query_lower for keyword in keywords)):
                return {
                    "type": "qa_pair",
                    "data": qa_pair
                }
        
        return None
    
    def _format_zobot_response(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format response from Zobot match"""
        if match_data["type"] == "flow":
            flow_data = match_data["data"]
            
            if "response" in flow_data:
                return {
                    "response": flow_data["response"],
                    "escalate": flow_data.get("escalate", False),
                    "confidence": "high",
                    "source": "zobot_flow",
                    "follow_up": flow_data.get("follow_up")
                }
            elif "follow_up" in flow_data:
                return {
                    "response": flow_data["follow_up"],
                    "escalate": False,
                    "confidence": "medium",
                    "source": "zobot_flow",
                    "needs_clarification": True
                }
        
        elif match_data["type"] == "qa_pair":
            qa_data = match_data["data"]
            return {
                "response": qa_data.get("answer", "I found relevant information but need to get more details."),
                "escalate": False,
                "confidence": "high",
                "source": "zobot_qa",
                "category": qa_data.get("category")
            }
        
        return None
    
    def _enhance_with_rag(self, query: str, zobot_response: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance Zobot response with RAG context if needed"""
        # If Zobot response needs more detail, get RAG context
        if (zobot_response.get("needs_clarification") or 
            len(zobot_response.get("response", "")) < 100):
            
            rag_result = self.rag_engine.process_query(query)
            
            if not rag_result["escalate"] and rag_result["confidence"] == "high":
                # Combine Zobot flow with RAG details
                combined_response = f"{zobot_response['response']}\n\n{rag_result['response']}"
                
                return {
                    "response": combined_response,
                    "escalate": False,
                    "confidence": "high",
                    "source": "hybrid",
                    "sources": rag_result.get("sources", []),
                    "zobot_flow": zobot_response.get("source")
                }
        
        return zobot_response
    
    def _detect_automation_workflow(self, query: str) -> Optional[WorkflowType]:
        """Detect if query should trigger an automation workflow"""
        query_lower = query.lower()
        
        for trigger, workflow_type in self.automation_triggers.items():
            if trigger in query_lower:
                return workflow_type
        
        return None
    
    def process_query(self, query: str, conversation_history: Optional[List[Dict[str, str]]] = None, session_id: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Main method to process queries with hybrid approach"""
        
        # Step 0: Check for automation workflow triggers
        workflow_type = self._detect_automation_workflow(query)
        
        if workflow_type and session_id and user_id:
            # Start automation workflow
            workflow_response = self.workflow_executor.start_workflow(workflow_type, session_id, user_id)
            
            return {
                "response": self._format_workflow_response(workflow_response),
                "escalate": False,
                "confidence": "high",
                "source": "automation_workflow",
                "workflow_type": workflow_type.value,
                "workflow_data": workflow_response
            }
        
        # Step 1: Check for Zobot pattern matches
        zobot_match = self._match_zobot_pattern(query)
        
        if zobot_match:
            # Step 2: Format Zobot response
            zobot_response = self._format_zobot_response(zobot_match)
            
            if zobot_response:
                # Step 3: Enhance with RAG if needed
                if not zobot_response.get("escalate"):
                    enhanced_response = self._enhance_with_rag(query, zobot_response)
                    return enhanced_response
                else:
                    return zobot_response
        
        # Step 4: Fall back to pure RAG if no Zobot match
        rag_result = self.rag_engine.process_query(query, conversation_history)
        rag_result["source"] = "rag_only"
        
        return rag_result
    
    def get_quick_actions(self, query: str) -> List[Dict[str, str]]:
        """Get quick action buttons based on query"""
        query_lower = query.lower()
        actions = []
        
        if any(word in query_lower for word in ["password", "reset", "login"]):
            actions.extend([
                {"text": "Reset Password", "action": "password_reset"},
                {"text": "Account Locked", "action": "account_locked"},
                {"text": "Contact Support", "action": "escalate"}
            ])
        
        elif any(word in query_lower for word in ["quickbooks", "qb"]):
            actions.extend([
                {"text": "Error Codes", "action": "qb_errors"},
                {"text": "File Issues", "action": "qb_files"},
                {"text": "Payroll Help", "action": "qb_payroll"},
                {"text": "Installation", "action": "qb_install"}
            ])
        
        elif any(word in query_lower for word in ["rdp", "remote"]):
            actions.extend([
                {"text": "Connection Issues", "action": "rdp_connection"},
                {"text": "Performance", "action": "rdp_performance"},
                {"text": "Setup Guide", "action": "rdp_setup"}
            ])
        
        elif any(word in query_lower for word in ["email", "outlook"]):
            actions.extend([
                {"text": "Setup Email", "action": "email_setup"},
                {"text": "Password Issues", "action": "email_password"},
                {"text": "Can't Send/Receive", "action": "email_sync"}
            ])
        
        # Always add general actions
        actions.extend([
            {"text": "Talk to Agent", "action": "escalate"},
            {"text": "Start Over", "action": "restart"}
        ])
        
        return actions[:6]  # Limit to 6 actions
    
    def _format_workflow_response(self, workflow_data: Dict[str, Any]) -> str:
        """Format workflow response for chat"""
        wf_type = workflow_data.get("type")
        
        if wf_type == "question":
            question = workflow_data.get("question", "")
            options = workflow_data.get("options", [])
            
            if options:
                return f"{question}\n\nOptions:\n" + "\n".join(f"• {opt}" for opt in options)
            return question
        
        elif wf_type == "form":
            fields = workflow_data.get("fields", [])
            return f"Please provide the following information:\n" + "\n".join(f"• {field.replace('_', ' ').title()}" for field in fields)
        
        elif wf_type == "choices":
            options = workflow_data.get("options", [])
            return "Please select an option:\n" + "\n".join(f"• {opt.get('size')} - {opt.get('price')}" for opt in options)
        
        elif wf_type == "instructions":
            return workflow_data.get("instructions", "")
        
        elif wf_type == "confirmation":
            return workflow_data.get("question", "Is this correct?")
        
        return str(workflow_data)
    
    def process_workflow_response(self, session_id: str, step_id: str, response: Any) -> Dict[str, Any]:
        """Process workflow step response"""
        result = self.workflow_executor.process_step_response(session_id, step_id, response)
        
        if result.get("error"):
            return {
                "response": result.get("error"),
                "escalate": False,
                "confidence": "high",
                "source": "automation_workflow"
            }
        
        if result.get("status") == "completed":
            return {
                "response": result.get("message", "Request completed successfully"),
                "escalate": result.get("escalate", False),
                "confidence": "high",
                "source": "automation_workflow",
                "ticket_id": result.get("ticket_id"),
                "eta": result.get("eta")
            }
        
        # Next step
        return {
            "response": self._format_workflow_response(result),
            "escalate": False,
            "confidence": "high",
            "source": "automation_workflow",
            "workflow_data": result
        }
    
    def handle_quick_action(self, action: str) -> Dict[str, Any]:
        """Handle quick action button clicks"""
        action_responses = {
            "password_reset": "I'll help you reset your password. Please visit https://selfcare.acecloudhosting.com/ and click 'Forgot Password'. You'll need your username or registered email address.",
            "account_locked": "If your account is locked, please wait 15 minutes and try again, or contact our support team for immediate assistance.",
            "qb_errors": "What QuickBooks error code are you seeing? Common ones include -6177, -6189, -816, 15212, etc.",
            "rdp_connection": "For RDP connection issues, first check: 1) Internet connection, 2) Server address is correct, 3) Firewall settings. What specific error are you getting?",
            "email_setup": "I can help you set up email. Are you using Outlook, Gmail, or another email client?",
            "escalate": "I'll connect you with one of our support specialists. Please hold while I transfer you.",
            "restart": "Hello! I'm AceBuddy. How can I help you today?"
        }
        
        response = action_responses.get(action, "I'm not sure how to handle that action. How can I help you?")
        
        return {
            "response": response,
            "escalate": action == "escalate",
            "confidence": "high",
            "source": "quick_action"
        }
