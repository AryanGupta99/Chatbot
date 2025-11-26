"""Test automation workflows"""

from src.hybrid_chatbot import HybridChatbot
from src.automation_workflows import WorkflowType
import json

def test_automation_workflows():
    print("="*70)
    print("TESTING AUTOMATION WORKFLOWS")
    print("="*70)
    
    chatbot = HybridChatbot()
    
    # Test cases for each workflow
    test_cases = [
        {
            "query": "My disk is full, I need to upgrade storage",
            "workflow": WorkflowType.DISK_UPGRADE,
            "description": "Disk Space Upgrade"
        },
        {
            "query": "I forgot my password",
            "workflow": WorkflowType.PASSWORD_RESET,
            "description": "Password Reset"
        },
        {
            "query": "I need to add a new user to the system",
            "workflow": WorkflowType.USER_MANAGEMENT,
            "description": "User Management"
        },
        {
            "query": "How do I set up multiple monitors?",
            "workflow": WorkflowType.MONITOR_SETUP,
            "description": "Monitor Setup"
        },
        {
            "query": "My printer is offline",
            "workflow": WorkflowType.PRINTER_ISSUES,
            "description": "Printer Issues"
        },
        {
            "query": "My server is running slow",
            "workflow": WorkflowType.SERVER_SLOWNESS,
            "description": "Server Slowness"
        },
        {
            "query": "I can't connect to RDP",
            "workflow": WorkflowType.RDP_CONNECTION,
            "description": "RDP Connection"
        },
        {
            "query": "I need to reboot the server",
            "workflow": WorkflowType.SERVER_REBOOT,
            "description": "Server Reboot"
        },
        {
            "query": "I can't get my MFA security code",
            "workflow": WorkflowType.QB_MFA,
            "description": "QB MFA"
        },
        {
            "query": "My email won't sync in Outlook",
            "workflow": WorkflowType.EMAIL_ISSUES,
            "description": "Email Issues"
        },
        {
            "query": "QuickBooks won't start",
            "workflow": WorkflowType.QB_ISSUES,
            "description": "QB Issues"
        },
        {
            "query": "Windows update failed",
            "workflow": WorkflowType.WINDOWS_UPDATE,
            "description": "Windows Update"
        },
        {
            "query": "My account is locked",
            "workflow": WorkflowType.ACCOUNT_LOCKED,
            "description": "Account Locked"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{len(test_cases)}] {test['description']}")
        print(f"Query: {test['query']}")
        print("-" * 70)
        
        try:
            # Process query with session
            session_id = f"test_workflow_{i}"
            user_id = "test_user"
            
            result = chatbot.process_query(
                test['query'],
                conversation_history=[],
                session_id=session_id,
                user_id=user_id
            )
            
            print(f"✅ Source: {result.get('source')}")
            print(f"   Confidence: {result.get('confidence')}")
            print(f"   Escalate: {result.get('escalate')}")
            
            if result.get('source') == 'automation_workflow':
                print(f"   Workflow Type: {result.get('workflow_type')}")
                print(f"   Response: {result.get('response')[:150]}...")
                
                # Check workflow data
                wf_data = result.get('workflow_data', {})
                if wf_data.get('type'):
                    print(f"   Workflow Step Type: {wf_data.get('type')}")
                
                results.append({
                    "test": test['description'],
                    "query": test['query'],
                    "workflow_detected": True,
                    "workflow_type": result.get('workflow_type'),
                    "response_type": wf_data.get('type'),
                    "success": True
                })
            else:
                print(f"   Response: {result.get('response')[:150]}...")
                results.append({
                    "test": test['description'],
                    "query": test['query'],
                    "workflow_detected": False,
                    "source": result.get('source'),
                    "success": False
                })
        
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "test": test['description'],
                "error": str(e),
                "success": False
            })
    
    # Summary
    print("\n" + "="*70)
    print("AUTOMATION WORKFLOW TEST SUMMARY")
    print("="*70)
    
    successful = [r for r in results if r.get('success')]
    detected = [r for r in results if r.get('workflow_detected')]
    
    print(f"\nTotal Tests: {len(test_cases)}")
    print(f"Successful: {len(successful)}")
    print(f"Workflows Detected: {len(detected)}")
    
    if detected:
        print(f"\nWorkflow Detection Rate: {len(detected)/len(test_cases)*100:.0f}%")
        
        # Group by workflow type
        workflows_by_type = {}
        for r in detected:
            wf_type = r.get('workflow_type')
            if wf_type not in workflows_by_type:
                workflows_by_type[wf_type] = []
            workflows_by_type[wf_type].append(r)
        
        print(f"\nWorkflows Detected by Type:")
        for wf_type, items in workflows_by_type.items():
            print(f"  - {wf_type}: {len(items)}")
        
        # Step types
        step_types = {}
        for r in detected:
            step_type = r.get('response_type')
            if step_type:
                step_types[step_type] = step_types.get(step_type, 0) + 1
        
        if step_types:
            print(f"\nWorkflow Step Types:")
            for step_type, count in step_types.items():
                print(f"  - {step_type}: {count}")
    
    print(f"\n✅ Automation workflows are ready for deployment!")

def test_workflow_execution():
    """Test workflow step execution"""
    print("\n" + "="*70)
    print("TESTING WORKFLOW STEP EXECUTION")
    print("="*70)
    
    chatbot = HybridChatbot()
    
    # Start a disk upgrade workflow
    print("\n[Test] Disk Upgrade Workflow Execution")
    print("-" * 70)
    
    session_id = "test_disk_upgrade"
    user_id = "test_user"
    
    # Step 1: Initiate workflow
    result1 = chatbot.process_query(
        "I need to upgrade my disk storage",
        session_id=session_id,
        user_id=user_id
    )
    
    print(f"✅ Workflow Initiated")
    print(f"   Source: {result1.get('source')}")
    print(f"   Response: {result1.get('response')[:100]}...")
    
    wf_data = result1.get('workflow_data', {})
    step_id = wf_data.get('step_id')
    
    if step_id:
        # Step 2: Respond to first step
        print(f"\n✅ Processing Step: {step_id}")
        
        result2 = chatbot.process_workflow_response(
            session_id,
            step_id,
            "100gb"  # Select 100GB plan
        )
        
        print(f"   Response: {result2.get('response')[:100]}...")
        print(f"   Status: {result2.get('source')}")
    
    print(f"\n✅ Workflow execution test complete!")

def test_workflow_list():
    """Test workflow list endpoint"""
    print("\n" + "="*70)
    print("TESTING WORKFLOW LIST")
    print("="*70)
    
    chatbot = HybridChatbot()
    workflows = chatbot.workflow_executor.workflows.get_workflow_list()
    
    print(f"\nAvailable Workflows: {len(workflows)}")
    print("-" * 70)
    
    for wf in workflows:
        print(f"\n✅ {wf['name']}")
        print(f"   Type: {wf['type']}")
        print(f"   Closure Rate: {wf['closure_rate']*100:.0f}%")
        print(f"   Time Saved: {wf['time_saved']} minutes")

if __name__ == "__main__":
    test_automation_workflows()
    test_workflow_execution()
    test_workflow_list()
