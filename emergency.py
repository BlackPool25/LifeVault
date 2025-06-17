from database import get_cursor, get_connection, log_security_event
from models import EmergencyContact, CATEGORIES
from ascii_ui import print_error, print_success, print_info, print_contact_info, get_user_choice, print_category_menu, refresh_screen

class EmergencyManager:
    def __init__(self):
        self.cursor = get_cursor()
        self.conn = get_connection()
        self.current_user_id = None

    def set_current_user(self, user_id):
        """Set the current user for emergency operations"""
        self.current_user_id = user_id

    def add_emergency_contact(self):
        """Add a new emergency contact"""
        if not self.current_user_id:
            print_error("Not logged in!")
            return False

        refresh_screen()
        print("\n🆘 Add Emergency Contact")
        print("═" * 30)
        
        # Get contact details
        name = input("Contact Name: ").strip()
        if not name:
            print_error("Name cannot be empty!")
            return False
            
        phone = input("Phone Number: ").strip()
        if not phone:
            print_error("Phone number cannot be empty!")
            return False
            
        email = input("Email (optional): ").strip()
        
        # Select allowed categories
        print("\nSelect categories this contact can access:")
        print_category_menu()
        
        allowed_categories = []
        while True:
            choice = get_user_choice("Select category (or 0 to finish): ", (0, len(CATEGORIES)))
            if choice == 0:
                break
            category_key = list(CATEGORIES.keys())[choice - 1]
            category_name = CATEGORIES[category_key]['name']
            if category_name not in allowed_categories:
                allowed_categories.append(category_name)
                print_success(f"Added {category_name}")
        
        if not allowed_categories:
            print_error("Must select at least one category!")
            return False
        
        # Save contact
        allowed_categories_str = ",".join(allowed_categories)
        self.cursor.execute(
            "INSERT INTO emergency_contacts (user_id, name, phone, email, allowed_categories) VALUES (?, ?, ?, ?, ?)", 
            (self.current_user_id, name, phone, email, allowed_categories_str)
        )
        self.conn.commit()
        
        log_security_event(self.current_user_id, "emergency_contact_added", details=f"Contact: {name}")
        print_success("Emergency contact added successfully!")
        return True

    def view_emergency_contacts(self):
        """View all emergency contacts"""
        if not self.current_user_id:
            print_error("Not logged in!")
            return False

        refresh_screen()
        self.cursor.execute(
            "SELECT id, name, phone, email, allowed_categories, created_at FROM emergency_contacts WHERE user_id = ?",
            (self.current_user_id,)
        )
        contacts_data = self.cursor.fetchall()
        
        if not contacts_data:
            print_info("No emergency contacts found.")
            return False
            
        print("\n📞 Emergency Contacts")
        print("═" * 40)
        
        for contact_id, name, phone, email, allowed_categories, created_at in contacts_data:
            contact = EmergencyContact(contact_id, self.current_user_id, name, phone, email, allowed_categories, created_at)
            print_contact_info(contact)
        
        input("\nPress Enter to continue...")
        return True

    def delete_emergency_contact(self):
        """Delete an emergency contact"""
        if not self.current_user_id:
            print_error("Not logged in!")
            return False

        # Get contacts
        self.cursor.execute(
            "SELECT id, name, phone FROM emergency_contacts WHERE user_id = ?",
            (self.current_user_id,)
        )
        contacts = self.cursor.fetchall()
        
        if not contacts:
            print_info("No emergency contacts to delete.")
            return False
        
        refresh_screen()
        print("\n🗑️  Delete Emergency Contact")
        print("═" * 30)
        
        for i, (contact_id, name, phone) in enumerate(contacts, 1):
            print(f"{i}. {name} ({phone})")
        
        choice = get_user_choice("Select contact to delete: ", (1, len(contacts)))
        contact_id, name, phone = contacts[choice - 1]
        
        # Confirm deletion
        confirm = input(f"Are you sure you want to delete {name}? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print_info("Deletion cancelled.")
            return False
        
        # Delete contact
        self.cursor.execute("DELETE FROM emergency_contacts WHERE id = ?", (contact_id,))
        self.conn.commit()
        
        log_security_event(self.current_user_id, "emergency_contact_deleted", details=f"Contact: {name}")
        print_success("Emergency contact deleted successfully!")
        return True

    def edit_emergency_contact(self):
        """Edit an emergency contact"""
        if not self.current_user_id:
            print_error("Not logged in!")
            return False

        # Get contacts
        self.cursor.execute(
            "SELECT id, name, phone, email, allowed_categories FROM emergency_contacts WHERE user_id = ?",
            (self.current_user_id,)
        )
        contacts = self.cursor.fetchall()
        
        if not contacts:
            print_info("No emergency contacts to edit.")
            return False
        
        refresh_screen()
        print("\n✏️  Edit Emergency Contact")
        print("═" * 30)
        
        for i, (contact_id, name, phone, email, allowed_categories) in enumerate(contacts, 1):
            print(f"{i}. {name} ({phone})")
        
        choice = get_user_choice("Select contact to edit: ", (1, len(contacts)))
        contact_id, name, phone, email, allowed_categories = contacts[choice - 1]
        
        print(f"\nEditing: {name}")
        print("(Press Enter to keep current value)")
        
        # Get new values
        new_name = input(f"Name [{name}]: ").strip()
        if not new_name:
            new_name = name
            
        new_phone = input(f"Phone [{phone}]: ").strip()
        if not new_phone:
            new_phone = phone
            
        new_email = input(f"Email [{email or 'none'}]: ").strip()
        if not new_email:
            new_email = email
        
        # Update contact
        self.cursor.execute(
            "UPDATE emergency_contacts SET name = ?, phone = ?, email = ? WHERE id = ?",
            (new_name, new_phone, new_email, contact_id)
        )
        self.conn.commit()
        
        log_security_event(self.current_user_id, "emergency_contact_edited", details=f"Contact: {name} -> {new_name}")
        print_success("Emergency contact updated successfully!")
        return True

    def manage_emergency_contacts(self):
        """Main emergency contact management menu"""
        if not self.current_user_id:
            print_error("Not logged in!")
            return False

        while True:
            refresh_screen()
            print("\n👥 Emergency Contact Management")
            print("═" * 40)
            print("1. ➕ Add New Contact")
            print("2. 👁️  View All Contacts")
            print("3. ✏️  Edit Contact")
            print("4. 🗑️  Delete Contact")
            print("5. 🔙 Back to Main Menu")
            
            choice = get_user_choice("Select option: ", (1, 5))
            
            if choice == 1:
                self.add_emergency_contact()
            elif choice == 2:
                self.view_emergency_contacts()
            elif choice == 3:
                self.edit_emergency_contact()
            elif choice == 4:
                self.delete_emergency_contact()
            elif choice == 5:
                break
        
        return True

    def get_user_emergency_contacts(self, user_id):
        """Get emergency contacts for a specific user"""
        self.cursor.execute(
            "SELECT id, name, phone, email, allowed_categories, created_at FROM emergency_contacts WHERE user_id = ?",
            (user_id,)
        )
        contacts_data = self.cursor.fetchall()
        
        return [
            EmergencyContact(contact_id, user_id, name, phone, email, allowed_categories, created_at)
            for contact_id, name, phone, email, allowed_categories, created_at in contacts_data
        ]