"""Zoho Desk Integration Module
Handles ticket creation, updates, and notifications in Zoho Desk
"""

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import os

class ZohoDeskIntegration:
    """Integrates with Zoho Desk API for ticket management"""
    
    def __init__(self):
        self.api_key = os.getenv("ZOHO_DESK_API_KEY")
        self.org_id = os.getenv("ZOHO_DESK_ORG_ID")
        self.base_url = "https://desk.zoho.com/api/v1"
        self.headers = {
            "Authorization": f"Zoho-orgId {self.org_id}",
            "Content-Type": "application/json"
        }
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Zoho Desk configuration"""
        config_file = Path("config/zoho_desk_config.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        
        return {
            "department_id": os.getenv("ZOHO_DESK_DEPARTMENT_ID", ""),
            "default_assignee": os.getenv("ZOHO_DESK_DEFAULT_ASSIGNEE", ""),
            "ticket_source": "SalesIQ",
            "custom_fields": {}
        }
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a ticket in Zoho Desk"""
        try:
            payload = {
                "subject": ticket_data.get("subject", "Support Request"),
                "description": ticket_data.get("description", ""),
                "departmentId": self.config.get("department_id"),
                "contactId": ticket_data.get("contact_id"),
                "email": ticket_data.get("email"),
                "phone": ticket_data.get("phone"),
                "priority": ticket_data.get("priority", "Medium"),
                "status": "Open",
                "source": self.config.get("ticket_source"),
                "customFields": {
                    "workflow_type": ticket_data.get("workflow_type"),
                    "automation_source": "AceBuddy",
                    "ticket_category": ticket_data.get("category", "General")
                }
            }
            
            # Add optional fields
            if ticket_data.get("assignee_id"):
                payload["assigneeId"] = ticket_data["assignee_id"]
            
            if ticket_data.get("tags"):
                payload["tags"] = ticket_data["tags"]
            
            # Create ticket via API
            response = requests.post(
                f"{self.base_url}/tickets",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                ticket = response.json().get("data", {})
                return {
                    "success": True,
                    "ticket_id": ticket.get("id"),
                    "ticket_number": ticket.get("ticketNumber"),
                    "status": ticket.get("status"),
                    "created_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create ticket: {response.text}",
                    "status_code": response.status_code
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_comment_to_ticket(self, ticket_id: str, comment: str, is_internal: bool = False) -> Dict[str, Any]:
        """Add a comment to an existing ticket"""
        try:
            payload = {
                "content": comment,
                "isInternal": is_internal
            }
            
            response = requests.post(
                f"{self.base_url}/tickets/{ticket_id}/comments",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "comment_id": response.json().get("data", {}).get("id")
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to add comment: {response.text}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_ticket_status(self, ticket_id: str, status: str) -> Dict[str, Any]:
        """Update ticket status"""
        try:
            payload = {"status": status}
            
            response = requests.patch(
                f"{self.base_url}/tickets/{ticket_id}",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                return {
                    "success": True,
                    "status": status
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to update status: {response.text}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Get ticket details"""
        try:
            response = requests.get(
                f"{self.base_url}/tickets/{ticket_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "ticket": response.json().get("data", {})
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get ticket: {response.text}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_contact(self, email: str) -> Dict[str, Any]:
        """Search for contact by email"""
        try:
            response = requests.get(
                f"{self.base_url}/contacts",
                headers=self.headers,
                params={"email": email},
                timeout=10
            )
            
            if response.status_code == 200:
                contacts = response.json().get("data", [])
                if contacts:
                    return {
                        "success": True,
                        "contact_id": contacts[0].get("id"),
                        "contact": contacts[0]
                    }
                else:
                    return {
                        "success": False,
                        "error": "Contact not found"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Failed to search contact: {response.text}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_or_get_contact(self, email: str, name: str, phone: str = "") -> Dict[str, Any]:
        """Create contact if not exists, or get existing"""
        try:
            # First try to find existing contact
            search_result = self.search_contact(email)
            
            if search_result.get("success"):
                return search_result
            
            # Create new contact
            payload = {
                "email": email,
                "firstName": name.split()[0] if name else "User",
                "lastName": name.split()[-1] if len(name.split()) > 1 else "",
                "phone": phone
            }
            
            response = requests.post(
                f"{self.base_url}/contacts",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                contact = response.json().get("data", {})
                return {
                    "success": True,
                    "contact_id": contact.get("id"),
                    "contact": contact,
                    "created": True
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create contact: {response.text}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_ticket_notification(self, ticket_id: str, email: str, ticket_number: str, subject: str) -> Dict[str, Any]:
        """Send ticket notification to customer"""
        try:
            # Add internal comment with ticket details
            comment = f"""
            Ticket Created Successfully!
            
            Ticket ID: {ticket_id}
            Ticket Number: {ticket_number}
            Subject: {subject}
            Status: Open
            Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Your support request has been logged and assigned to our support team.
            You will receive updates via email at {email}.
            """
            
            self.add_comment_to_ticket(ticket_id, comment, is_internal=False)
            
            return {
                "success": True,
                "message": "Notification sent"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def link_salesiq_chat(self, ticket_id: str, chat_id: str, visitor_id: str) -> Dict[str, Any]:
        """Link SalesIQ chat to Zoho Desk ticket"""
        try:
            payload = {
                "customFields": {
                    "salesiq_chat_id": chat_id,
                    "salesiq_visitor_id": visitor_id
                }
            }
            
            response = requests.patch(
                f"{self.base_url}/tickets/{ticket_id}",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                return {
                    "success": True,
                    "message": "Chat linked to ticket"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to link chat: {response.text}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_ticket_by_chat_id(self, chat_id: str) -> Dict[str, Any]:
        """Get ticket associated with a SalesIQ chat"""
        try:
            response = requests.get(
                f"{self.base_url}/tickets",
                headers=self.headers,
                params={"customFields.salesiq_chat_id": chat_id},
                timeout=10
            )
            
            if response.status_code == 200:
                tickets = response.json().get("data", [])
                if tickets:
                    return {
                        "success": True,
                        "ticket": tickets[0]
                    }
                else:
                    return {
                        "success": False,
                        "error": "No ticket found for this chat"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Failed to search tickets: {response.text}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_ticket_from_workflow(self, workflow_data: Dict[str, Any], chat_id: str = "", visitor_id: str = "") -> Dict[str, Any]:
        """Create ticket from automation workflow"""
        try:
            # Get or create contact
            contact_result = self.create_or_get_contact(
                email=workflow_data.get("email", ""),
                name=workflow_data.get("name", "User"),
                phone=workflow_data.get("phone", "")
            )
            
            if not contact_result.get("success"):
                return contact_result
            
            contact_id = contact_result.get("contact_id")
            
            # Prepare ticket data
            ticket_data = {
                "subject": workflow_data.get("subject", "Support Request"),
                "description": self._format_ticket_description(workflow_data),
                "contact_id": contact_id,
                "email": workflow_data.get("email"),
                "phone": workflow_data.get("phone"),
                "priority": workflow_data.get("priority", "Medium"),
                "workflow_type": workflow_data.get("workflow_type"),
                "category": workflow_data.get("category", "General"),
                "tags": workflow_data.get("tags", [])
            }
            
            # Create ticket
            ticket_result = self.create_ticket(ticket_data)
            
            if not ticket_result.get("success"):
                return ticket_result
            
            ticket_id = ticket_result.get("ticket_id")
            
            # Link SalesIQ chat if provided
            if chat_id and visitor_id:
                self.link_salesiq_chat(ticket_id, chat_id, visitor_id)
            
            # Send notification
            self.send_ticket_notification(
                ticket_id,
                workflow_data.get("email"),
                ticket_result.get("ticket_number"),
                ticket_data["subject"]
            )
            
            return {
                "success": True,
                "ticket_id": ticket_id,
                "ticket_number": ticket_result.get("ticket_number"),
                "contact_id": contact_id,
                "message": "Ticket created successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_ticket_description(self, workflow_data: Dict[str, Any]) -> str:
        """Format workflow data as ticket description"""
        description = f"""
        Workflow Type: {workflow_data.get('workflow_type', 'General')}
        Category: {workflow_data.get('category', 'General')}
        
        Details:
        {json.dumps(workflow_data.get('details', {}), indent=2)}
        
        Created via: AceBuddy Automation
        Timestamp: {datetime.now().isoformat()}
        """
        return description.strip()
    
    def get_department_id(self, department_name: str) -> Optional[str]:
        """Get department ID by name"""
        try:
            response = requests.get(
                f"{self.base_url}/departments",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                departments = response.json().get("data", [])
                for dept in departments:
                    if dept.get("name").lower() == department_name.lower():
                        return dept.get("id")
            
            return None
        
        except Exception as e:
            print(f"Error getting department: {e}")
            return None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Zoho Desk API connection"""
        try:
            response = requests.get(
                f"{self.base_url}/tickets",
                headers=self.headers,
                params={"limit": 1},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Connected to Zoho Desk successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Connection failed: {response.status_code}",
                    "details": response.text
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
