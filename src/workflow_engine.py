"""Workflow Execution Engine
Executes automation workflows with state management and escalation
"""

import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from src.automation_workflows import AutomationWorkflows, WorkflowType, WorkflowStatus

class WorkflowExecutor:
    """Executes workflows with full state management"""
    
    def __init__(self):
        self.workflows = AutomationWorkflows()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.crm_data = self._load_crm_data()
        self.email_config = self._load_email_config()
    
    def _load_crm_data(self) -> Dict[str, Any]:
        """Load CRM data for verification"""
        crm_file = Path("data/crm_data.json")
        if crm_file.exists():
            with open(crm_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_email_config(self) -> Dict[str, Any]:
        """Load email configuration"""
        return {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "acebuddy@acecloudhosting.com",
            "sender_password": "your_app_password"
        }
    
    def start_workflow(self, workflow_type: WorkflowType, session_id: str, user_id: str) -> Dict[str, Any]:
        """Start a new workflow"""
        workflow_def = self.workflows.workflows.get(workflow_type)
        
        if not workflow_def:
            return {"error": "Workflow not found"}
        
        session = {
            "workflow_type": workflow_type,
            "user_id": user_id,
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "current_step": 0,
            "collected_data": {},
            "workflow_def": workflow_def
        }
        
        self.active_sessions[session_id] = session
        
        # Get first step
        first_step = workflow_def["steps"][0]
        return self._format_step_response(first_step, session_id)
    
    def _format_step_response(self, step: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Format step as chat response"""
        action = step.get("action")
        
        if action == "ask_question":
            return {
                "type": "question",
                "question": step.get("question"),
                "options": step.get("options"),
                "step_id": step.get("id"),
                "session_id": session_id
            }
        
        elif action == "collect_form_data":
            return {
                "type": "form",
                "fields": step.get("fields"),
                "step_id": step.get("id"),
                "session_id": session_id
            }
        
        elif action == "present_choices":
            return {
                "type": "choices",
                "options": step.get("options"),
                "step_id": step.get("id"),
                "session_id": session_id
            }
        
        elif action == "provide_steps":
            return {
                "type": "instructions",
                "instructions": step.get("description"),
                "step_id": step.get("id"),
                "session_id": session_id
            }
        
        elif action == "ask_confirmation":
            return {
                "type": "confirmation",
                "question": step.get("question", "Is this correct?"),
                "step_id": step.get("id"),
                "session_id": session_id
            }
        
        return {
            "type": "action",
            "action": action,
            "description": step.get("description"),
            "step_id": step.get("id"),
            "session_id": session_id
        }
    
    def process_step_response(self, session_id: str, step_id: str, response: Any) -> Dict[str, Any]:
        """Process user response to a workflow step"""
        session = self.active_sessions.get(session_id)
        
        if not session:
            return {"error": "Session not found"}
        
        workflow_def = session["workflow_def"]
        current_step = session["current_step"]
        step = workflow_def["steps"][current_step]
        
        # Validate step ID matches
        if step.get("id") != step_id:
            return {"error": "Step ID mismatch"}
        
        # Store response
        session["collected_data"][step_id] = response
        
        # Process based on action type
        action = step.get("action")
        
        if action == "ask_question":
            result = self._process_question(session, step, response)
        elif action == "collect_form_data":
            result = self._process_form(session, step, response)
        elif action == "present_choices":
            result = self._process_choice(session, step, response)
        elif action == "ask_confirmation":
            result = self._process_confirmation(session, step, response)
        else:
            result = {"status": "processed"}
        
        # Check for escalation
        if result.get("escalate"):
            session["status"] = "escalated"
            return result
        
        # Move to next step
        session["current_step"] += 1
        
        if session["current_step"] >= len(workflow_def["steps"]):
            # Workflow complete
            return self._complete_workflow(session)
        
        # Get next step
        next_step = workflow_def["steps"][session["current_step"]]
        return self._format_step_response(next_step, session_id)
    
    def _process_question(self, session: Dict, step: Dict, response: str) -> Dict[str, Any]:
        """Process question response"""
        options = step.get("options", [])
        
        if options and response not in options:
            return {
                "error": f"Invalid option. Please choose from: {', '.join(options)}",
                "escalate": False
            }
        
        return {"status": "processed"}
    
    def _process_form(self, session: Dict, step: Dict, response: Dict) -> Dict[str, Any]:
        """Process form data"""
        fields = step.get("fields", [])
        
        # Validate required fields
        for field in fields:
            if field not in response or not response[field]:
                return {
                    "error": f"Missing required field: {field}",
                    "escalate": False
                }
        
        # Store form data
        session["collected_data"].update(response)
        
        return {"status": "processed"}
    
    def _process_choice(self, session: Dict, step: Dict, response: str) -> Dict[str, Any]:
        """Process choice selection"""
        options = step.get("options", [])
        
        # Find selected option
        selected = None
        for opt in options:
            if opt.get("value") == response or opt.get("size") == response:
                selected = opt
                break
        
        if not selected:
            return {
                "error": "Invalid selection",
                "escalate": False
            }
        
        session["collected_data"]["selected_option"] = selected
        return {"status": "processed"}
    
    def _process_confirmation(self, session: Dict, step: Dict, response: bool) -> Dict[str, Any]:
        """Process confirmation"""
        if not response:
            return {
                "message": "Please provide correct information",
                "escalate": False,
                "restart_step": True
            }
        
        return {"status": "confirmed"}
    
    def _complete_workflow(self, session: Dict) -> Dict[str, Any]:
        """Complete workflow and trigger actions"""
        workflow_type = session["workflow_type"]
        collected_data = session["collected_data"]
        
        # Execute workflow-specific completion actions
        if workflow_type == WorkflowType.DISK_UPGRADE:
            return self._complete_disk_upgrade(session)
        elif workflow_type == WorkflowType.PASSWORD_RESET:
            return self._complete_password_reset(session)
        elif workflow_type == WorkflowType.USER_MANAGEMENT:
            return self._complete_user_management(session)
        elif workflow_type == WorkflowType.ACCOUNT_LOCKED:
            return self._complete_account_unlock(session)
        else:
            return self._complete_generic_workflow(session)
    
    def _complete_disk_upgrade(self, session: Dict) -> Dict[str, Any]:
        """Complete disk upgrade workflow"""
        data = session["collected_data"]
        selected = data.get("selected_option", {})
        
        # Send to POC for approval
        ticket_id = self._create_ticket("disk_upgrade", data)
        self._send_email_to_poc(
            subject="Disk Upgrade Request - Approval Needed",
            body=f"""
            User: {session['user_id']}
            Selected Plan: {selected.get('size')} - {selected.get('price')}
            Ticket ID: {ticket_id}
            
            Please approve or reject this upgrade request.
            """
        )
        
        session["status"] = "awaiting_approval"
        session["ticket_id"] = ticket_id
        
        return {
            "status": "awaiting_approval",
            "message": f"Your upgrade request has been sent to your POC for approval. Ticket ID: {ticket_id}",
            "ticket_id": ticket_id,
            "next_action": "We'll notify you once approved"
        }
    
    def _complete_password_reset(self, session: Dict) -> Dict[str, Any]:
        """Complete password reset workflow"""
        data = session["collected_data"]
        
        # Create support ticket
        ticket_id = self._create_ticket("password_reset", data)
        
        # Send to support team
        self._send_email_to_support(
            subject="Password Reset Request",
            body=f"""
            User: {data.get('username')}
            Email: {data.get('email')}
            Ticket ID: {ticket_id}
            
            Please process this password reset request.
            """
        )
        
        # Notify user
        self._send_email_to_user(
            email=data.get('email'),
            subject="Password Reset Request Received",
            body=f"""
            Your password reset request has been received.
            Ticket ID: {ticket_id}
            Expected time: 2-4 hours
            """
        )
        
        session["status"] = "completed"
        session["ticket_id"] = ticket_id
        
        return {
            "status": "completed",
            "message": "Password reset request submitted successfully",
            "ticket_id": ticket_id,
            "eta": "2-4 hours"
        }
    
    def _complete_user_management(self, session: Dict) -> Dict[str, Any]:
        """Complete user management workflow"""
        data = session["collected_data"]
        action = data.get("action_type", "add")
        
        # Create support ticket
        ticket_id = self._create_ticket("user_management", data)
        
        # Send to IT team
        self._send_email_to_it(
            subject=f"User {action.capitalize()} Request",
            body=f"""
            Action: {action.upper()}
            Name: {data.get('full_name')}
            Email: {data.get('email_address')}
            Department: {data.get('department')}
            Role: {data.get('role')}
            Ticket ID: {ticket_id}
            """
        )
        
        session["status"] = "completed"
        session["ticket_id"] = ticket_id
        
        return {
            "status": "completed",
            "message": f"User {action} request submitted successfully",
            "ticket_id": ticket_id,
            "eta": "1-2 hours"
        }
    
    def _complete_account_unlock(self, session: Dict) -> Dict[str, Any]:
        """Complete account unlock workflow"""
        data = session["collected_data"]
        username = data.get("username")
        
        # Verify identity
        if not self._verify_user_identity(username, data):
            return {
                "status": "failed",
                "message": "Identity verification failed",
                "escalate": True
            }
        
        # Unlock account
        success = self._unlock_account(username)
        
        if success:
            session["status"] = "completed"
            return {
                "status": "completed",
                "message": "Your account has been unlocked successfully",
                "next_action": "You can now log in"
            }
        else:
            return {
                "status": "failed",
                "message": "Failed to unlock account",
                "escalate": True
            }
    
    def _complete_generic_workflow(self, session: Dict) -> Dict[str, Any]:
        """Complete generic workflow"""
        data = session["collected_data"]
        workflow_type = session["workflow_type"]
        
        # Create ticket
        ticket_id = self._create_ticket(workflow_type.value, data)
        
        # Send to support
        self._send_email_to_support(
            subject=f"{workflow_type.value.replace('_', ' ').title()} Request",
            body=json.dumps(data, indent=2)
        )
        
        session["status"] = "completed"
        session["ticket_id"] = ticket_id
        
        return {
            "status": "completed",
            "message": "Your request has been submitted successfully",
            "ticket_id": ticket_id
        }
    
    def _create_ticket(self, ticket_type: str, data: Dict) -> str:
        """Create support ticket"""
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        ticket = {
            "id": ticket_id,
            "type": ticket_type,
            "created_at": datetime.now().isoformat(),
            "data": data
        }
        
        # Store ticket (in production, save to database)
        tickets_file = Path("data/tickets.json")
        tickets = []
        
        if tickets_file.exists():
            with open(tickets_file, 'r') as f:
                tickets = json.load(f)
        
        tickets.append(ticket)
        
        with open(tickets_file, 'w') as f:
            json.dump(tickets, f, indent=2)
        
        return ticket_id
    
    def _send_email_to_poc(self, subject: str, body: str) -> bool:
        """Send email to POC"""
        # In production, implement actual email sending
        return True
    
    def _send_email_to_support(self, subject: str, body: str) -> bool:
        """Send email to support team"""
        return True
    
    def _send_email_to_it(self, subject: str, body: str) -> bool:
        """Send email to IT team"""
        return True
    
    def _send_email_to_user(self, email: str, subject: str, body: str) -> bool:
        """Send email to user"""
        return True
    
    def _verify_user_identity(self, username: str, data: Dict) -> bool:
        """Verify user identity against CRM"""
        user = self.crm_data.get(username, {})
        
        if not user:
            return False
        
        # Check if provided data matches CRM
        if data.get("email") != user.get("email"):
            return False
        
        if data.get("department") != user.get("department"):
            return False
        
        return True
    
    def _unlock_account(self, username: str) -> bool:
        """Unlock user account"""
        # In production, call actual account management system
        return True
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current session status"""
        session = self.active_sessions.get(session_id)
        
        if not session:
            return {"error": "Session not found"}
        
        return {
            "workflow_type": session["workflow_type"].value,
            "status": session["status"],
            "current_step": session["current_step"],
            "total_steps": len(session["workflow_def"]["steps"]),
            "progress": (session["current_step"] / len(session["workflow_def"]["steps"])) * 100
        }
    
    def cancel_workflow(self, session_id: str) -> Dict[str, Any]:
        """Cancel active workflow"""
        session = self.active_sessions.get(session_id)
        
        if not session:
            return {"error": "Session not found"}
        
        session["status"] = "cancelled"
        
        return {
            "status": "cancelled",
            "message": "Workflow cancelled"
        }
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        return self.workflows.get_workflow_stats()
