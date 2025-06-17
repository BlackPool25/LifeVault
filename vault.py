from database import get_cursor, get_connection, log_security_event
from encryption import encrypt_data, decrypt_data
from models import VaultData, CATEGORIES
from ascii_ui import print_error, print_success, print_info, print_data_entry, get_user_choice, print_category_menu, refresh_screen

class VaultManager:
    def __init__(self):
        self.cursor = get_cursor()
        self.conn = get_connection()
        self.data_entries = []
        self.current_user_id = None

    def load_user_data(self, user_id):
        """Load data for a specific user"""
        self.current_user_id = user_id
        self.cursor.execute(
            "SELECT id, user_id, category, title, encrypted_data, created_at, updated_at FROM vault WHERE user_id = ?",
            (user_id,)
        )
        self.data_entries = [
            VaultData(id_, user_id, cat, title, enc, created, updated, decrypt_data) 
            for id_, user_id, cat, title, enc, created, updated in self.cursor.fetchall()
        ]

    def add_entry(self):
        """Add a new data entry"""
        if not self.current_user_id:
            print_error("Not logged in!")
            return False

        refresh_screen()
        print("\n📝 Add New Entry")
        print("═" * 30)
        
        # Show category menu
        print_category_menu()
        category_choice = get_user_choice("Select category: ", (1, len(CATEGORIES) + 1))
        
        if category_choice == len(CATEGORIES) + 1:
            print_info("Operation cancelled.")
            return False
        
        # Get category key
        category_key = list(CATEGORIES.keys())[category_choice - 1]
        category_name = CATEGORIES[category_key]['name']
        
        # Get entry details
        title = input("Title: ").strip()
        if not title:
            print_error("Title cannot be empty!")
            return False
            
        content = input("Content: ").strip()
        if not content:
            print_error("Content cannot be empty!")
            return False
            
        # Encrypt and save
        encrypted = encrypt_data(content)
        self.cursor.execute(
            "INSERT INTO vault (user_id, category, title, encrypted_data) VALUES (?, ?, ?, ?)", 
            (self.current_user_id, category_name, title, encrypted)
        )
        self.conn.commit()
        
        # Reload data
        self.load_user_data(self.current_user_id)
        log_security_event(self.current_user_id, "entry_added", details=f"Category: {category_name}, Title: {title}")
        print_success("Entry added successfully!")
        return True

    def view_all_entries(self):
        """View all user entries"""
        if not self.current_user_id:
            print_error("Not logged in!")
            return False

        refresh_screen()
        if not self.data_entries:
            print_info("No data found.")
            return False
            
        print("\n📋 All Entries")
        print("═" * 50)
        
        # Group by category
        categories = {}
        for entry in self.data_entries:
            if entry.category not in categories:
                categories[entry.category] = []
            categories[entry.category].append(entry)
        
        for category, entries in categories.items():
            print(f"\n🏷️  {category.upper()}")
            print("-" * 30)
            for entry in entries:
                print_data_entry(entry)
        
        log_security_event(self.current_user_id, "entries_viewed")
        input("\nPress Enter to continue...")
        return True

    def edit_entry(self):
        """Edit an existing entry"""
        if not self.current_user_id:
            print_error("Not logged in!")
            return False

        if not self.data_entries:
            print_info("No data to edit.")
            return False
            
        refresh_screen()
        print("\n✏️  Edit Entry")
        print("═" * 20)
        
        # Show available entries
        for i, entry in enumerate(self.data_entries, 1):
            print(f"{i}. {entry.category} | {entry.title}")
        
        choice = get_user_choice("Select entry to edit: ", (1, len(self.data_entries)))
        entry = self.data_entries[choice - 1]
        
        print(f"\nEditing: {entry.title}")
        print("(Press Enter to keep current value)")
        
        # Get new values
        new_category = input(f"Category [{entry.category}]: ").strip()
        if not new_category:
            new_category = entry.category
            
        new_title = input(f"Title [{entry.title}]: ").strip()
        if not new_title:
            new_title = entry.title
            
        new_content = input(f"Content [{entry.get_decrypted_content()}]: ").strip()
        if not new_content:
            new_content = entry.get_decrypted_content()
            
        # Update in database
        encrypted = encrypt_data(new_content)
        self.cursor.execute(
            "UPDATE vault SET category=?, title=?, encrypted_data=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", 
            (new_category, new_title, encrypted, entry.id)
        )
        self.conn.commit()
        
        # Reload data
        self.load_user_data(self.current_user_id)
        log_security_event(self.current_user_id, "entry_edited", details=f"Entry ID: {entry.id}")
        print_success("Entry updated successfully!")
        return True

    def delete_entry(self):
        """Delete an entry"""
        if not self.current_user_id:
            print_error("Not logged in!")
            return False

        if not self.data_entries:
            print_info("No data to delete.")
            return False
            
        refresh_screen()
        print("\n🗑️  Delete Entry")
        print("═" * 20)
        
        # Show available entries
        for i, entry in enumerate(self.data_entries, 1):
            print(f"{i}. {entry.category} | {entry.title}")
        
        choice = get_user_choice("Select entry to delete: ", (1, len(self.data_entries)))
        entry = self.data_entries[choice - 1]
        
        # Confirm deletion
        confirm = input(f"Are you sure you want to delete '{entry.title}'? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print_info("Deletion cancelled.")
            return False
            
        # Delete from database
        self.cursor.execute("DELETE FROM vault WHERE id=?", (entry.id,))
        self.conn.commit()
        
        # Reload data
        self.load_user_data(self.current_user_id)
        log_security_event(self.current_user_id, "entry_deleted", details=f"Entry ID: {entry.id}, Title: {entry.title}")
        print_success("Entry deleted successfully!")
        return True

    def search_entries(self):
        """Search entries by title or content"""
        if not self.current_user_id:
            print_error("Not logged in!")
            return False

        if not self.data_entries:
            print_info("No data to search.")
            return False
            
        refresh_screen()
        print("\n🔍 Search Entries")
        print("═" * 20)
        
        search_term = input("Enter search term: ").strip().lower()
        if not search_term:
            print_error("Search term cannot be empty!")
            return False
        
        # Search in titles and content
        results = []
        for entry in self.data_entries:
            if (search_term in entry.title.lower() or 
                search_term in entry.get_decrypted_content().lower()):
                results.append(entry)
        
        if not results:
            print_info("No entries found matching your search.")
            return False
        
        print(f"\nFound {len(results)} matching entries:")
        print("═" * 40)
        
        for entry in results:
            print_data_entry(entry)
        
        log_security_event(self.current_user_id, "entries_searched", details=f"Search term: {search_term}")
        input("\nPress Enter to continue...")
        return True

    def get_statistics(self):
        """Get data statistics"""
        if not self.current_user_id:
            print_error("Not logged in!")
            return False

        refresh_screen()
        print("\n📊 Data Statistics")
        print("═" * 20)
        
        # Count by category
        categories = {}
        for entry in self.data_entries:
            if entry.category not in categories:
                categories[entry.category] = 0
            categories[entry.category] += 1
        
        print(f"Total entries: {len(self.data_entries)}")
        print("\nBy category:")
        for category, count in categories.items():
            print(f"  • {category}: {count} entries")
        
        # Recent activity
        if self.data_entries:
            recent_entries = sorted(self.data_entries, key=lambda x: x.updated_at, reverse=True)[:5]
            print(f"\nRecent updates:")
            for entry in recent_entries:
                print(f"  • {entry.title} ({entry.updated_at})")
        
        input("\nPress Enter to continue...")
        return True

    def get_entries_by_categories(self, allowed_categories):
        """Get entries filtered by allowed categories"""
        return [entry for entry in self.data_entries if entry.category.lower() in allowed_categories]