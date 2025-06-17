from datetime import datetime

class User:
    def __init__(self, id, username, password_hash, email, emergency_pin, created_at):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.emergency_pin = emergency_pin
        self.created_at = created_at

class VaultData:
    def __init__(self, id, user_id, category, title, encrypted_data, created_at, updated_at, decrypt_func):
        self.id = id
        self.user_id = user_id
        self.category = category
        self.title = title
        self.encrypted_data = encrypted_data
        self.created_at = created_at
        self.updated_at = updated_at
        self.decrypt_func = decrypt_func

    def get_decrypted_content(self):
        return self.decrypt_func(self.encrypted_data)

class EmergencyContact:
    def __init__(self, id, user_id, name, phone, email, allowed_categories, created_at):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.email = email
        self.allowed_categories = [c.strip().lower() for c in allowed_categories.split(",")]
        self.created_at = created_at

class SecurityLog:
    def __init__(self, id, user_id, action, ip_address, timestamp, details):
        self.id = id
        self.user_id = user_id
        self.action = action
        self.ip_address = ip_address
        self.timestamp = timestamp
        self.details = details

# Predefined categories with descriptions
CATEGORIES = {
    "medical": {
        "name": "🏥 Medical",
        "description": "Health information, medications, blood type, allergies",
        "icon": "🏥"
    },
    "financial": {
        "name": "💰 Financial", 
        "description": "Bank accounts, credit cards, insurance, investments",
        "icon": "💰"
    },
    "emergency": {
        "name": "🆘 Emergency",
        "description": "Emergency contacts, procedures, important documents",
        "icon": "🆘"
    },
    "personal": {
        "name": "👤 Personal",
        "description": "Personal documents, IDs, passwords, private notes",
        "icon": "👤"
    },
    "work": {
        "name": "💼 Work",
        "description": "Work credentials, projects, professional information",
        "icon": "💼"
    },
    "legal": {
        "name": "⚖️ Legal",
        "description": "Legal documents, contracts, important papers",
        "icon": "⚖️"
    },
    "travel": {
        "name": "✈️ Travel",
        "description": "Travel documents, itineraries, passport info",
        "icon": "✈️"
    },
    "other": {
        "name": "📁 Other",
        "description": "Miscellaneous important information",
        "icon": "📁"
    }
}