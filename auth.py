import hashlib
import getpass
import re
from database import get_cursor, get_connection, log_security_event, log_failed_attempt, is_account_locked
from ascii_ui import print_error, print_success, print_warning, print_info, print_security_warning, refresh_screen
from models import User

class AuthManager:
    def __init__(self):
        self.cursor = get_cursor()
        self.conn = get_connection()
        self.current_user = None

    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_email(self, email):
        """Basic email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_pin(self, pin):
        """Validate 4-digit PIN"""
        return len(pin) == 4 and pin.isdigit()

    def signup(self):
        """User registration"""
        refresh_screen()
        print("\n📝 Create New Account")
        print("═" * 30)
        
        # Username
        while True:
            username = input("Username: ").strip()
            if not username:
                print_error("Username cannot be empty!")
                continue
            if len(username) < 3:
                print_error("Username must be at least 3 characters!")
                continue
                
            # Check if username exists
            self.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if self.cursor.fetchone():
                print_error("Username already exists!")
                continue
            break
        
        # Email
        while True:
            email = input("Email (optional): ").strip()
            if email and not self.validate_email(email):
                print_error("Invalid email format!")
                continue
            break
        
        # Password
        while True:
            password = getpass.getpass("Password: ")
            if len(password) < 6:
                print_error("Password must be at least 6 characters!")
                continue
            confirm_password = getpass.getpass("Confirm password: ")
            if password != confirm_password:
                print_error("Passwords don't match!")
                continue
            break
        
        # Emergency PIN
        while True:
            pin = getpass.getpass("4-digit Emergency PIN: ")
            if not self.validate_pin(pin):
                print_error("PIN must be exactly 4 digits!")
                continue
            confirm_pin = getpass.getpass("Confirm Emergency PIN: ")
            if pin != confirm_pin:
                print_error("PINs don't match!")
                continue
            break
        
        # Create user
        password_hash = self.hash_password(password)
        pin_hash = self.hash_password(pin)
        
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, email, emergency_pin) VALUES (?, ?, ?, ?)",
                (username, password_hash, email, pin_hash)
            )
            self.conn.commit()
            
            user_id = self.cursor.lastrowid
            log_security_event(user_id, "user_registration", details=f"New user: {username}")
            
            print_success("Account created successfully!")
            return True
            
        except Exception as e:
            print_error(f"Registration failed: {e}")
            return False

    def login(self):
        """User login"""
        refresh_screen()
        print("\n🔑 Login")
        print("═" * 20)
        
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        
        if not username or not password:
            print_error("Username and password are required!")
            return False
        
        # Get user
        self.cursor.execute(
            "SELECT id, username, password_hash, email, emergency_pin, created_at FROM users WHERE username = ?",
            (username,)
        )
        user_data = self.cursor.fetchone()
        
        if not user_data:
            print_error("Invalid username or password!")
            return False
        
        user_id, db_username, db_password_hash, email, emergency_pin, created_at = user_data
        
        # Check password
        if self.hash_password(password) != db_password_hash:
            log_failed_attempt(user_id, "login")
            print_error("Invalid username or password!")
            return False
        
        # Check if account is locked
        if is_account_locked(user_id, "login"):
            print_security_warning()
            return False
        
        # Success
        self.current_user = User(user_id, db_username, db_password_hash, email, emergency_pin, created_at)
        log_security_event(user_id, "login_success")
        print_success(f"Welcome back, {username}!")
        return True

    def emergency_access(self, vault_manager):
        """Emergency access with PIN verification"""
        refresh_screen()
        print("\n🆘 Emergency Access")
        print("═" * 30)
        
        username = input("Username: ").strip()
        if not username:
            print_error("Username is required!")
            return False
        
        # Get user
        self.cursor.execute(
            "SELECT id, username, emergency_pin FROM users WHERE username = ?",
            (username,)
        )
        user_data = self.cursor.fetchone()
        
        if not user_data:
            print_error("User not found!")
            return False
        
        user_id, db_username, db_emergency_pin = user_data
        
        # Check if account is locked
        if is_account_locked(user_id, "pin"):
            print_security_warning()
            return False
        
        # PIN verification
        pin = getpass.getpass("4-digit Emergency PIN: ")
        if self.hash_password(pin) != db_emergency_pin:
            log_failed_attempt(user_id, "pin")
            log_security_event(user_id, "emergency_access_failed", details="Invalid PIN")
            print_error("Invalid PIN!")
            
            # Check if account should be locked
            if is_account_locked(user_id, "pin"):
                print_security_warning()
            return False
        
        # Success - grant emergency access
        log_security_event(user_id, "emergency_access_granted")
        print_success("Emergency access granted!")
        
        # Show emergency data
        self._show_emergency_data(user_id, vault_manager)
        return True

    def _show_emergency_data(self, user_id, vault_manager):
        """Show emergency data for the user"""
        print("\n🆘 Emergency Data Access")
        print("═" * 40)
        
        # Get emergency contacts
        self.cursor.execute(
            "SELECT id, name, phone, email, allowed_categories, created_at FROM emergency_contacts WHERE user_id = ?",
            (user_id,)
        )
        contacts = self.cursor.fetchall()
        
        if not contacts:
            print_info("No emergency contacts configured for this user.")
            return
        
        print("\n📞 Emergency Contacts:")
        for contact_id, name, phone, email, allowed_categories, created_at in contacts:
            print(f"  • {name} ({phone})")
            if email:
                print(f"    Email: {email}")
            print(f"    Access: {allowed_categories}")
        
        # Show accessible data
        print("\n📋 Accessible Data:")
        vault_manager.load_user_data(user_id)
        entries = vault_manager.data_entries
        
        if not entries:
            print_info("No data found for this user.")
            return
        
        # Group by category
        categories = {}
        for entry in entries:
            if entry.category not in categories:
                categories[entry.category] = []
            categories[entry.category].append(entry)
        
        for category, category_entries in categories.items():
            print(f"\n🏷️  {category.upper()}")
            print("-" * 30)
            for entry in category_entries:
                print(f"  • {entry.title}: {entry.get_decrypted_content()}")
        
        input("\nPress Enter to continue...")

    def change_password(self):
        """Change user password"""
        if not self.current_user:
            print_error("Not logged in!")
            return False
        
        refresh_screen()
        print("\n🔑 Change Password")
        print("═" * 20)
        
        current_password = getpass.getpass("Current password: ")
        if self.hash_password(current_password) != self.current_user.password_hash:
            print_error("Current password is incorrect!")
            return False
        
        # New password
        while True:
            new_password = getpass.getpass("New password: ")
            if len(new_password) < 6:
                print_error("Password must be at least 6 characters!")
                continue
            confirm_password = getpass.getpass("Confirm new password: ")
            if new_password != confirm_password:
                print_error("Passwords don't match!")
                continue
            break
        
        # Update password
        new_password_hash = self.hash_password(new_password)
        self.cursor.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (new_password_hash, self.current_user.id)
        )
        self.conn.commit()
        
        # Update current user object
        self.current_user.password_hash = new_password_hash
        
        log_security_event(self.current_user.id, "password_changed")
        print_success("Password changed successfully!")
        return True

    def logout(self):
        """User logout"""
        if self.current_user:
            log_security_event(self.current_user.id, "logout")
            self.current_user = None
        print_success("Logged out successfully!")
        return True 