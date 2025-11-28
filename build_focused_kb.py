"""
Build Focused Knowledge Base
Only include real-world, ticket-relevant data
"""

import json
from pathlib import Path
from src.data_processor import DataProcessor
from src.chunker import SemanticChunker
from src.vector_store import VectorStore
import shutil

def load_manual_kb_articles():
    """Load manually curated KB articles"""
    kb_dir = Path("data/kb")
    articles = []
    
    print("\n[1/4] Loading Manual KB Articles...")
    
    for kb_file in kb_dir.glob("*.md"):
        with open(kb_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract category from filename
        filename = kb_file.stem
        if 'password' in filename:
            category = "Password/Login"
        elif 'rdp' in filename or 'connection' in filename:
            category = "Remote Desktop"
        elif 'quickbooks' in filename:
            category = "QuickBooks"
        elif 'email' in filename:
            category = "Email"
        elif 'server' in filename or 'performance' in filename:
            category = "Server"
        elif 'printer' in filename:
            category = "Printer"
        elif 'user' in filename:
            category = "User Management"
        elif 'storage' in filename or 'disk' in filename:
            category = "Storage"
        elif 'monitor' in filename:
            category = "Display"
        else:
            category = "General"
        
        articles.append({
            "id": filename,
            "content": content,
            "metadata": {
                "filename": kb_file.name,
                "doc_id": filename,
                "category": category,
                "source": "manual_kb",
                "type": "kb_article",
                "char_count": len(content),
                "word_count": len(content.split())
            }
        })
    
    # Also load the support guide
    support_guide = kb_dir / "acebuddy_support_guide.txt"
    if support_guide.exists():
        with open(support_guide, 'r', encoding='utf-8') as f:
            content = f.read()
        
        articles.append({
            "id": "acebuddy_support_guide",
            "content": content,
            "metadata": {
                "filename": "acebuddy_support_guide.txt",
                "doc_id": "acebuddy_support_guide",
                "category": "General",
                "source": "manual_kb",
                "type": "support_guide",
                "char_count": len(content),
                "word_count": len(content.split())
            }
        })
    
    print(f"✅ Loaded {len(articles)} manual KB articles")
    return articles

def load_pdf_kb_docs():
    """Load PDF KB documentation"""
    print("\n[2/4] Loading PDF KB Documents...")
    
    processor = DataProcessor()
    documents = processor.process_all_pdfs()
    
    # Filter to only keep relevant, high-quality docs
    filtered_docs = []
    for doc in documents:
        # Skip if too short (likely extraction error)
        if doc['metadata']['word_count'] < 50:
            continue
        
        # Keep all - they're all relevant KB docs
        filtered_docs.append(doc)
    
    print(f"✅ Loaded {len(filtered_docs)} PDF KB documents")
    return filtered_docs

def create_manual_training_examples():
    """Create high-quality manual training examples based on common tickets"""
    print("\n[3/4] Creating Manual Training Examples...")
    
    training_examples = [
        {
            "query": "I forgot my password, how do I reset it?",
            "response": "For security reasons, password resets require verification. Please contact our support team at 1-855-223-4887 with your business name and registered email. Our team will verify your account and assist you with the password reset process.",
            "category": "Password/Login",
            "source": "manual_curation"
        },
        {
            "query": "I'm getting QuickBooks error -6177 when trying to open my company file",
            "response": "Error -6177 occurs when QuickBooks can't access the company file. To fix: 1) Close QuickBooks completely, 2) Navigate to your company file location (usually in the Company Files folder), 3) Right-click the .QBW file and rename it (add '_temp' to the end), 4) Rename it back to the original name, 5) Try opening QuickBooks again. This refreshes the file connection. If the issue persists, contact support at 1-855-223-4887.",
            "category": "QuickBooks",
            "source": "manual_curation"
        },
        {
            "query": "I can't connect to the Remote Desktop server",
            "response": "Common RDP connection issues: 1) Check your internet connection, 2) Verify you're using the correct server address and credentials, 3) Make sure Remote Desktop is enabled on your local computer, 4) Try restarting the Remote Desktop application. If you see error 0x204 or 'logon attempt failed', verify your username and password. For Mac users with error 0x300006xc, update your Microsoft Remote Desktop app. Still having issues? Contact support at 1-855-223-4887.",
            "category": "Remote Desktop",
            "source": "manual_curation"
        },
        {
            "query": "The server is running very slow",
            "response": "Server slowness can be caused by: 1) High disk usage - check available space in C: drive, 2) Too many applications running simultaneously, 3) Multiple users accessing resource-intensive applications, 4) Pending Windows updates. Try closing unused applications and logging off idle sessions. If the issue persists, contact support at 1-855-223-4887 for server performance analysis.",
            "category": "Server",
            "source": "manual_curation"
        },
        {
            "query": "My email is not working in Outlook",
            "response": "Common Outlook email issues: 1) If Outlook keeps asking for password, try removing and re-adding your account, 2) Check if you can access email via webmail to verify credentials, 3) Ensure your internet connection is stable, 4) For Office 365, verify MFA settings if enabled. To configure email: Go to File > Add Account and follow the setup wizard. Need help? Contact support at 1-855-223-4887.",
            "category": "Email",
            "source": "manual_curation"
        },
        {
            "query": "How do I add a new user to the server?",
            "response": "To add a new user, please contact our support team at 1-855-223-4887 with: 1) Full name of the new user, 2) Email address, 3) Required access level (admin or standard user), 4) Applications they need access to. Our team will create the user account and provide login credentials. For QuickBooks user permissions, we can also help configure those within your company file.",
            "category": "User Management",
            "source": "manual_curation"
        },
        {
            "query": "My disk is full" or "C drive showing red",
            "response": "Let's free up some space first! Try these cleanup steps: 1) Press Windows Key + R, type 'temp' and delete all files, 2) Press Windows Key + R, type '%temp%' and delete all files, 3) Right-click C: Drive > Properties > Disk Cleanup > check all boxes and clean, 4) Uninstall unused programs from Control Panel. After cleanup, if you still need more space, we offer storage upgrades: 40GB ($28/month), 60GB ($40/month), 80GB ($50/month), 100GB ($60/month), or 200GB ($120/month). I can help you create a ticket for an upgrade with 2-4 hour ETA. Which plan interests you?",
            "category": "Storage",
            "source": "manual_curation"
        },
        {
            "query": "QuickBooks error 'You have exceeded the maximum number of users'",
            "response": "This error means all available QuickBooks licenses are in use. Solutions: 1) Check if other users have QuickBooks open but aren't actively using it - ask them to close it, 2) On dedicated servers, you can use QB Instance Kill tool to end frozen sessions, 3) Verify your license count matches your subscription. If you need additional licenses, contact support at 1-855-223-4887.",
            "category": "QuickBooks",
            "source": "manual_curation"
        },
        {
            "query": "My printer is not working on the server",
            "response": "For printer issues: 1) Verify your local printer is turned on and connected, 2) In RDP, go to Options > Local Resources > More and ensure 'Printers' is checked, 3) Reconnect to the server, 4) Check if the printer appears in Devices and Printers on the server, 5) For check printing alignment issues, use UniPrint settings to adjust. Need help with printer setup? Contact support at 1-855-223-4887.",
            "category": "Printer",
            "source": "manual_curation"
        },
        {
            "query": "The screen size is wrong when I connect to the server",
            "response": "To adjust screen size: 1) Before connecting, click 'Show Options' in Remote Desktop, 2) Go to Display tab, 3) Adjust the slider for screen resolution, 4) For Windows: Use 'Display settings' on the server to adjust scaling, 5) For Mac: Update display settings in System Preferences. You can also adjust RDP display settings in the connection properties. Need assistance? Contact support at 1-855-223-4887.",
            "category": "Display",
            "source": "manual_curation"
        },
        {
            "query": "QuickBooks payroll update is failing",
            "response": "For QuickBooks payroll update errors (PS032, PS077, PS034, PS038): 1) Close QuickBooks completely, 2) Run QuickBooks as administrator, 3) Go to Employees > Get Payroll Updates, 4) Select 'Download Entire Update', 5) If error persists, verify your payroll subscription is active, 6) Check internet connection stability. For persistent issues, contact support at 1-855-223-4887.",
            "category": "QuickBooks",
            "source": "manual_curation"
        },
        {
            "query": "I'm getting 'Another user has connected to the session' error",
            "response": "This error occurs when your session is still active on the server. Solutions: 1) Wait 2-3 minutes and try reconnecting, 2) Contact support at 1-855-223-4887 to reset your session, 3) To prevent this, always log off properly instead of just closing the RDP window. Use Start > Sign Out before disconnecting.",
            "category": "Remote Desktop",
            "source": "manual_curation"
        },
        {
            "query": "How much does storage upgrade cost?",
            "response": "Our storage upgrade plans are: 40GB for $28/month, 60GB for $40/month, 80GB for $50/month, 100GB for $60/month, and 200GB for $120/month. Before upgrading, I recommend trying cleanup steps to free up space: delete temp files (Windows Key + R, type 'temp'), use Disk Cleanup tool, and remove unused programs. If you'd like to proceed with an upgrade, I can create a ticket for you with 2-4 hour ETA. Which plan would you like?",
            "category": "Storage",
            "source": "manual_curation"
        },
        {
            "query": "How do I set up multi-factor authentication for Office 365?",
            "response": "For Office 365 MFA setup: 1) Sign in to your Office 365 account, 2) Go to Security Settings, 3) Enable Multi-Factor Authentication, 4) Follow prompts to add your phone number or authenticator app, 5) Complete verification. If you need to disable MFA, contact support at 1-855-223-4887 as this requires admin access.",
            "category": "Email",
            "source": "manual_curation"
        },
        {
            "query": "QuickBooks is showing unrecoverable error",
            "response": "For QuickBooks unrecoverable errors: 1) Note the exact error code, 2) Close QuickBooks and restart your computer, 3) Run QuickBooks File Doctor tool (available in QuickBooks Tool Hub), 4) If error persists, restore from a recent backup, 5) Check if company file is corrupted by running Verify Data utility. For assistance, contact support at 1-855-223-4887 with the error code.",
            "category": "QuickBooks",
            "source": "manual_curation"
        },
        {
            "query": "How do I backup my QuickBooks data?",
            "response": "To backup QuickBooks: 1) Open your company file, 2) Go to File > Create Backup, 3) Choose 'Local Backup', 4) Select location (recommend saving to a different drive or cloud storage), 5) Click OK to create backup. For automatic backups, go to File > Create Backup > Schedule Future Backups. Your ACE server also has automated backups. For backup restoration help, contact support at 1-855-223-4887.",
            "category": "QuickBooks",
            "source": "manual_curation"
        }
    ]
    
    print(f"✅ Created {len(training_examples)} manual training examples")
    return training_examples

def build_focused_knowledge_base():
    """Build complete focused knowledge base"""
    
    print("="*70)
    print("BUILDING FOCUSED KNOWLEDGE BASE")
    print("Only ticket-relevant, real-world data")
    print("="*70)
    
    # Load all data sources
    manual_kb = load_manual_kb_articles()
    pdf_docs = load_pdf_kb_docs()
    training_examples = create_manual_training_examples()
    
    # Combine all documents
    all_documents = manual_kb + pdf_docs
    
    print(f"\n{'='*70}")
    print(f"DATA SUMMARY")
    print(f"{'='*70}")
    print(f"Manual KB Articles: {len(manual_kb)}")
    print(f"PDF KB Documents: {len(pdf_docs)}")
    print(f"Training Examples: {len(training_examples)}")
    print(f"Total Documents: {len(all_documents)}")
    
    # Create chunks
    print(f"\n[4/4] Creating Semantic Chunks...")
    chunker = SemanticChunker(chunk_size=500, overlap=50)
    
    # Process documents into chunks
    all_chunks = chunker.process_documents(all_documents, training_examples)
    
    # Save chunks
    output_dir = Path("data/processed")
    output_dir.mkdir(exist_ok=True)
    
    chunks_file = output_dir / "focused_chunks.json"
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(all_chunks)} chunks to {chunks_file}")
    
    # Show breakdown
    doc_chunks = [c for c in all_chunks if c['metadata'].get('type') not in ['training_example', 'kb_article']]
    kb_chunks = [c for c in all_chunks if c['metadata'].get('type') == 'kb_article']
    training_chunks = [c for c in all_chunks if c['metadata'].get('type') == 'training_example']
    
    print(f"\nChunk Breakdown:")
    print(f"  - PDF KB chunks: {len(doc_chunks)}")
    print(f"  - Manual KB chunks: {len(kb_chunks)}")
    print(f"  - Training examples: {len(training_chunks)}")
    
    # Category breakdown
    categories = {}
    for chunk in all_chunks:
        cat = chunk['metadata'].get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nBy Category:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {cat}: {count}")
    
    return all_chunks

def rebuild_vector_store_with_focused_data(chunks):
    """Rebuild vector store with focused chunks"""
    
    print(f"\n{'='*70}")
    print("REBUILDING VECTOR STORE")
    print(f"{'='*70}")
    
    # Delete existing vector store
    from config import settings
    chroma_dir = Path(settings.chroma_persist_directory)
    
    if chroma_dir.exists():
        print(f"\nDeleting existing vector store...")
        try:
            shutil.rmtree(chroma_dir)
            print("✅ Deleted old vector store")
        except Exception as e:
            print(f"⚠️  Warning: {e}")
    
    # Create new vector store
    print(f"\nCreating new vector store...")
    vector_store = VectorStore()
    vector_store.create_collection()
    
    # Add chunks
    print(f"\nAdding {len(chunks)} chunks...")
    print("⏳ Generating embeddings (this takes a few minutes)...")
    
    try:
        vector_store.add_documents(chunks)
        print("✅ Successfully added all chunks!")
    except Exception as e:
        print(f"❌ Error: {e}")
        if "401" in str(e) or "api" in str(e).lower():
            print("\n⚠️  API KEY ISSUE DETECTED")
            print("Please update your .env file with a valid OpenAI API key:")
            print("OPENAI_API_KEY=sk-proj-your-actual-key-here")
        return False
    
    # Verify
    stats = vector_store.get_collection_stats()
    print(f"\n{'='*70}")
    print("VERIFICATION")
    print(f"{'='*70}")
    print(f"Documents in vector store: {stats['total_documents']}")
    print(f"Expected: {len(chunks)}")
    
    if stats['total_documents'] == len(chunks):
        print("✅ SUCCESS! All chunks loaded correctly.")
        return True
    else:
        print(f"⚠️  Mismatch detected")
        return False

if __name__ == "__main__":
    print("\n🎯 Building Focused, Ticket-Relevant Knowledge Base\n")
    
    # Build knowledge base
    chunks = build_focused_knowledge_base()
    
    # Rebuild vector store
    print("\n" + "="*70)
    input("Press Enter to rebuild vector store (requires valid OpenAI API key)...")
    
    success = rebuild_vector_store_with_focused_data(chunks)
    
    if success:
        print(f"\n{'='*70}")
        print("✅ COMPLETE!")
        print(f"{'='*70}")
        print("\nYour knowledge base now contains:")
        print("✓ Manual KB articles (curated)")
        print("✓ PDF KB documentation (all relevant docs)")
        print("✓ 15 high-quality training examples")
        print("✓ All focused on real ticket scenarios")
        print("\nNext: Test with python test_chatbot.py")
    else:
        print(f"\n{'='*70}")
        print("❌ FAILED")
        print(f"{'='*70}")
        print("\nMost likely cause: Invalid or missing OpenAI API key")
        print("Fix: Update .env file with valid key and run again")
