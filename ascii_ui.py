import os
from models import CATEGORIES

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print the application banner"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║   ██      ██ ███████ ███████ ██    ██  █████  ██    ██ ██   ████████ ║
    ║   ██      ██ ██      ██      ██    ██ ██   ██ ██    ██ ██      ██    ║
    ║   ██      ██ █████   █████   ██    ██ ███████ ██    ██ ██      ██    ║
    ║   ██      ██ ██      ██       ██  ██  ██   ██ ██    ██ ██      ██    ║
    ║   ███████ ██ ██      ███████   ████   ██   ██  ██████  ███████ ██    ║
    ║                                                                      ║
    ║                            🔐 LifeVault                              ║
    ║                                                                      ║
    ║            Your Personal Data Vault with Emergency Access            ║
    ║                                                                      ║
    ║                        Secure • Private • Reliable                   ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)

def refresh_screen():
    """Clear screen and show banner"""
    clear_screen()
    print_banner()

def print_auth_menu():
    print("""
    🔐 Authentication Menu
    ═══════════════════════
    
    1. 📝 Sign Up (New User)
    2. 🔑 Login (Existing User)
    3. 🆘 Emergency Access
    4. ❌ Exit
    
    """)

def print_main_menu(username):
    print(f"""
    🏠 Welcome, {username}! 
    ═══════════════════════════════════════════════════════════════
    
    📁 Data Management:
    ┌─────────────────────────────────────────────────────────────┐
    │ 1. ➕ Add New Entry        │ 2. 👁️  View All Data            │
    │ 3. ✏️  Edit Entry          │ 4. 🗑️  Delete Entry              │
    │ 5. 🔍 Search Entries       │ 6. 📊 Data Statistics          │
    └─────────────────────────────────────────────────────────────┘
    
    🆘 Emergency System:
    ┌─────────────────────────────────────────────────────────────┐
    │ 7. 👥 Manage Contacts      │ 8. 🔐 Emergency Access         │
    │ 9. 📋 View Contacts        │ 10. ⚙️  Security Settings       │
    └─────────────────────────────────────────────────────────────┘
    
    👤 Account:
    ┌─────────────────────────────────────────────────────────────┐
    │ 11. 🔧 Account Settings    │ 12. 📜 Security Logs           │
    │ 13. 🔑 Change Password     │ 14. 🚪 Logout                  │
    └─────────────────────────────────────────────────────────────┘
    
    """)

def print_category_menu():
    print("\n📂 Select Category:")
    print("═" * 50)
    
    for i, (key, category) in enumerate(CATEGORIES.items(), 1):
        print(f"{i}. {category['icon']} {category['name']}")
        print(f"   └─ {category['description']}")
    
    print(f"{len(CATEGORIES) + 1}. ❌ Cancel")

def print_emergency_menu():
    print("""
    🆘 Emergency Access System
    ═══════════════════════════
    
    ⚠️  WARNING: This feature is for emergency situations only!
    
    To access data in an emergency:
    1. You need the 4-digit emergency PIN
    2. Failed attempts will lock the account for 2 hours
    3. Account owner will be notified of access attempts
    
    📋 Emergency Access Features:
    • All Emergency category entries are always accessible
    • Additional categories based on emergency contact permissions
    • Complete emergency contact information displayed
    
    """)

def print_security_warning():
    print("""
    ⚠️  SECURITY WARNING ⚠️
    ═══════════════════════
    
    ❌ Account temporarily locked due to multiple failed attempts!
    🔒 Please wait 2 hours before trying again.
    📧 Account owner has been notified of this security event.
    
    """)

def print_success(message):
    print(f"\n✅ {message}")
    input("\nPress Enter to continue...")
    refresh_screen()

def print_error(message):
    print(f"\n❌ {message}")
    input("\nPress Enter to continue...")
    refresh_screen()

def print_warning(message):
    print(f"\n⚠️  {message}")
    input("\nPress Enter to continue...")
    refresh_screen()

def print_info(message):
    print(f"\nℹ️  {message}")
    input("\nPress Enter to continue...")
    refresh_screen()

def print_loading(message="Loading..."):
    print(f"\n⏳ {message}")

def print_separator():
    print("\n" + "═" * 60)

def print_data_entry(entry, show_content=True):
    """Print a formatted data entry"""
    category_info = CATEGORIES.get(entry.category.lower(), {"name": entry.category, "icon": "📄"})
    
    print(f"\n{category_info['icon']} {category_info['name']}")
    print(f"   Title: {entry.title}")
    if show_content:
        print(f"   Content: {entry.get_decrypted_content()}")
    print(f"   Created: {entry.created_at}")
    print(f"   Updated: {entry.updated_at}")
    print("-" * 40)

def print_contact_info(contact):
    """Print formatted contact information"""
    print(f"\n👤 {contact.name}")
    print(f"   📞 Phone: {contact.phone}")
    if contact.email:
        print(f"   📧 Email: {contact.email}")
    print(f"   🔐 Access: {', '.join(contact.allowed_categories)}")
    print(f"   📅 Added: {contact.created_at}")
    print("-" * 30)

def get_user_choice(prompt="Enter your choice: ", valid_range=None):
    """Get user input with validation"""
    while True:
        try:
            choice = input(prompt).strip()
            if valid_range:
                choice = int(choice)
                if choice < valid_range[0] or choice > valid_range[1]:
                    print_error(f"Please enter a number between {valid_range[0]} and {valid_range[1]}")
                    continue
            return choice
        except ValueError:
            print_error("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            exit(0)