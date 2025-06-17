from ascii_ui import print_banner, print_auth_menu, print_main_menu, get_user_choice, print_error, print_success, print_info, refresh_screen
from auth import AuthManager
from vault import VaultManager
from emergency import EmergencyManager
from database import close_db, log_security_event
import sys

class PersonalDataVault:
    def __init__(self):
        self.auth_manager = AuthManager()
        self.vault_manager = VaultManager()
        self.emergency_manager = EmergencyManager()

    def run(self):
        """Main application loop"""
        refresh_screen()
        
        while True:
            print_auth_menu()
            choice = get_user_choice("Select option: ", (1, 4))
            
            if choice == 1:
                self.auth_manager.signup()
                refresh_screen()
            elif choice == 2:
                if self.auth_manager.login():
                    self.vault_manager.load_user_data(self.auth_manager.current_user.id)
                    self.emergency_manager.set_current_user(self.auth_manager.current_user.id)
                    self.main_application_loop()
                else:
                    refresh_screen()
            elif choice == 3:
                self.auth_manager.emergency_access(self.vault_manager)
                refresh_screen()
            elif choice == 4:
                print_success("Thank you for using Personal Data Vault!")
                break

    def main_application_loop(self):
        """Main application loop after login"""
        while True:
            refresh_screen()
            print_main_menu(self.auth_manager.current_user.username)
            choice = get_user_choice("Select option: ", (1, 14))
            
            try:
                if choice == 1:
                    self.vault_manager.add_entry()
                elif choice == 2:
                    self.vault_manager.view_all_entries()
                elif choice == 3:
                    self.vault_manager.edit_entry()
                elif choice == 4:
                    self.vault_manager.delete_entry()
                elif choice == 5:
                    self.vault_manager.search_entries()
                elif choice == 6:
                    self.vault_manager.get_statistics()
                elif choice == 7:
                    self.emergency_manager.manage_emergency_contacts()
                elif choice == 8:
                    self.auth_manager.emergency_access(self.vault_manager)
                elif choice == 9:
                    self.emergency_manager.view_emergency_contacts()
                elif choice == 10:
                    self.show_security_settings()
                elif choice == 11:
                    self.show_account_settings()
                elif choice == 12:
                    self.show_security_logs()
                elif choice == 13:
                    self.auth_manager.change_password()
                elif choice == 14:
                    self.auth_manager.logout()
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print_error(f"An error occurred: {e}")

    def show_security_settings(self):
        """Show security settings menu"""
        while True:
            refresh_screen()
            print("\n⚙️  Security Settings")
            print("═" * 20)
            print("1. 🔒 View Account Lock Status")
            print("2. 📧 Security Notifications")
            print("3. 🔙 Back to Main Menu")
            
            choice = get_user_choice("Select option: ", (1, 3))
            
            if choice == 1:
                self.show_account_lock_status()
            elif choice == 2:
                self.show_security_notifications()
            elif choice == 3:
                break

    def show_account_lock_status(self):
        """Show account lock status"""
        from database import get_failed_attempts
        
        print("\n🔒 Account Security Status")
        print("═" * 30)
        
        login_attempts = get_failed_attempts(self.auth_manager.current_user.id, "login")
        pin_attempts = get_failed_attempts(self.auth_manager.current_user.id, "pin")
        
        print(f"Failed login attempts (last 2 hours): {login_attempts}/3")
        print(f"Failed PIN attempts (last 2 hours): {pin_attempts}/3")
        
        if login_attempts >= 3:
            print_error("⚠️  Account is locked due to failed login attempts!")
        elif pin_attempts >= 3:
            print_error("⚠️  Emergency access is locked due to failed PIN attempts!")
        else:
            print_success("✅ Account is secure and unlocked.")

    def show_security_notifications(self):
        """Show security notification settings"""
        print("\n📧 Security Notifications")
        print("═" * 30)
        print("Currently, you will be notified of:")
        print("• Failed login attempts")
        print("• Failed emergency PIN attempts")
        print("• Emergency access granted")
        print("• Account lockouts")
        print("\nNotifications are logged in the security logs.")
        input("\nPress Enter to continue...")

    def show_account_settings(self):
        """Show account settings menu"""
        while True:
            refresh_screen()
            print("\n🔧 Account Settings")
            print("═" * 20)
            print("1. 👤 View Profile")
            print("2. 📧 Update Email")
            print("3. 🔑 Change Emergency PIN")
            print("4. 🔙 Back to Main Menu")
            
            choice = get_user_choice("Select option: ", (1, 4))
            
            if choice == 1:
                self.show_profile()
            elif choice == 2:
                self.update_email()
            elif choice == 3:
                self.change_emergency_pin()
            elif choice == 4:
                break

    def show_profile(self):
        """Show user profile"""
        user = self.auth_manager.current_user
        print("\n👤 User Profile")
        print("═" * 20)
        print(f"Username: {user.username}")
        print(f"Email: {user.email or 'Not set'}")
        print(f"Account created: {user.created_at}")
        
        # Get statistics
        entry_count = len(self.vault_manager.data_entries)
        contact_count = len(self.emergency_manager.get_user_emergency_contacts(user.id))
        
        print(f"Total entries: {entry_count}")
        print(f"Emergency contacts: {contact_count}")
        input("\nPress Enter to continue...")

    def update_email(self):
        """Update user email"""
        print("\n📧 Update Email")
        print("═" * 20)
        
        current_email = self.auth_manager.current_user.email or "Not set"
        print(f"Current email: {current_email}")
        
        new_email = input("New email: ").strip()
        if not new_email:
            print_info("Email update cancelled.")
            return
        
        if not self.auth_manager.validate_email(new_email):
            print_error("Invalid email format!")
            return
        
        # Update email
        self.auth_manager.cursor.execute(
            "UPDATE users SET email = ? WHERE id = ?",
            (new_email, self.auth_manager.current_user.id)
        )
        self.auth_manager.conn.commit()
        
        # Update current user object
        self.auth_manager.current_user.email = new_email
        
        log_security_event(self.auth_manager.current_user.id, "email_updated")
        print_success("Email updated successfully!")

    def change_emergency_pin(self):
        """Change emergency PIN"""
        print("\n🔑 Change Emergency PIN")
        print("═" * 25)
        
        current_password = input("Current password: ")
        if self.auth_manager.hash_password(current_password) != self.auth_manager.current_user.password_hash:
            print_error("Current password is incorrect!")
            return
        
        # New PIN
        while True:
            new_pin = input("New 4-digit Emergency PIN: ")
            if not self.auth_manager.validate_pin(new_pin):
                print_error("PIN must be exactly 4 digits!")
                continue
            confirm_pin = input("Confirm new Emergency PIN: ")
            if new_pin != confirm_pin:
                print_error("PINs don't match!")
                continue
            break
        
        # Update PIN
        new_pin_hash = self.auth_manager.hash_password(new_pin)
        self.auth_manager.cursor.execute(
            "UPDATE users SET emergency_pin = ? WHERE id = ?",
            (new_pin_hash, self.auth_manager.current_user.id)
        )
        self.auth_manager.conn.commit()
        
        # Update current user object
        self.auth_manager.current_user.emergency_pin = new_pin_hash
        
        log_security_event(self.auth_manager.current_user.id, "emergency_pin_changed")
        print_success("Emergency PIN changed successfully!")

    def show_security_logs(self):
        """Show security logs"""
        print("\n📜 Security Logs")
        print("═" * 20)
        
        self.auth_manager.cursor.execute(
            "SELECT action, timestamp, details FROM security_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20",
            (self.auth_manager.current_user.id,)
        )
        logs = self.auth_manager.cursor.fetchall()
        
        if not logs:
            print_info("No security logs found.")
            return
        
        for action, timestamp, details in logs:
            print(f"• {timestamp} - {action}")
            if details:
                print(f"  Details: {details}")
            print()
        input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    try:
        app = PersonalDataVault()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print_error(f"Application error: {e}")
    finally:
        close_db()

if __name__ == "__main__":
    main()