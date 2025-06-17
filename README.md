# 🔒 Personal Data Vault with Emergency Access

A secure, encrypted personal data management system with multi-user support, emergency access capabilities, and advanced security features.

## 🎯 Features

### 🔐 Security & Authentication
- **Multi-User System**: Individual accounts with separate data storage
- **Password Authentication**: SHA-256 hashed passwords with secure login
- **4-Digit Emergency PIN**: Separate emergency access with PIN verification
- **Account Lockout**: Automatic 2-hour lockout after 3 failed attempts
- **Security Logging**: Comprehensive audit trail of all security events
- **AES Encryption**: All sensitive data encrypted using Fernet (AES-128)

### 📁 Data Management
- **8 Predefined Categories**: Medical, Financial, Emergency, Personal, Work, Legal, Travel, Other
- **CRUD Operations**: Add, view, edit, and delete entries with confirmation
- **Search Functionality**: Search across titles and content
- **Data Statistics**: View entry counts and recent activity
- **Data Validation**: Input validation to ensure data integrity

### 🆘 Emergency Access System
- **Multiple Emergency Contacts**: Support for multiple trusted contacts per user
- **Role-Based Access**: Each contact can access specific categories only
- **PIN Verification**: 4-digit emergency PIN required for access
- **Security Notifications**: Failed attempts are logged and tracked
- **Selective Data Sharing**: Choose which data to share during emergency

### 🖥️ User Interface
- **Beautiful ASCII UI**: Modern, intuitive terminal interface
- **Category Icons**: Visual category indicators with descriptions
- **Error Handling**: Graceful error handling with user-friendly messages
- **Input Validation**: Robust input validation and user guidance
- **Navigation**: Easy-to-use menu system with clear options

### 👤 Account Management
- **Profile Management**: View and update account information
- **Email Updates**: Change email address with validation
- **Password Changes**: Secure password update functionality
- **Emergency PIN Management**: Change emergency PIN with verification
- **Security Settings**: View account lock status and security logs

## 🚀 Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python main.py
   ```

## 📖 Usage

### First Time Setup
1. Run the application
2. Select "Sign Up" to create a new account
3. Enter username, password, email (optional), and 4-digit emergency PIN
4. Start adding your data entries

### Daily Usage
1. **Login** with your username and password
2. **Add Data**: Select from 8 predefined categories
3. **Manage Data**: View, edit, delete, or search your entries
4. **Emergency Contacts**: Add trusted contacts with specific access permissions
5. **Security**: Monitor your account security status and logs

### Emergency Access
1. Select "Emergency Access" from the main menu
2. Enter the username of the account holder
3. Enter the 4-digit emergency PIN
4. View emergency contacts and accessible data
5. **Security**: Failed attempts lock the account for 2 hours

### Data Categories
- **🏥 Medical**: Health information, medications, blood type, allergies
- **💰 Financial**: Bank accounts, credit cards, insurance, investments
- **🆘 Emergency**: Emergency contacts, procedures, important documents
- **👤 Personal**: Personal documents, IDs, passwords, private notes
- **💼 Work**: Work credentials, projects, professional information
- **⚖️ Legal**: Legal documents, contracts, important papers
- **✈️ Travel**: Travel documents, itineraries, passport info
- **📁 Other**: Miscellaneous important information

## 🏗️ Project Structure

```
Python AAT/
├── main.py              # Main application entry point
├── auth.py              # Authentication and user management
├── vault.py             # Core vault management functionality
├── emergency.py         # Emergency access and contact management
├── database.py          # Database operations and security logging
├── encryption.py        # Encryption/decryption utilities
├── models.py            # Data models and category definitions
├── ascii_ui.py          # User interface components
├── requirements.txt     # Project dependencies
└── README.md           # This file
```

## 🔧 Technical Details

### Database Schema
- **users**: User accounts (id, username, password_hash, email, emergency_pin, created_at)
- **vault**: Encrypted data entries (id, user_id, category, title, encrypted_data, timestamps)
- **emergency_contacts**: Emergency contact information (id, user_id, name, phone, email, allowed_categories)
- **security_logs**: Security event audit trail (id, user_id, action, ip_address, timestamp, details)
- **failed_attempts**: Failed login/PIN attempt tracking (id, user_id, attempt_type, ip_address, timestamp)

### Security Features
- **Encryption**: AES-128 encryption using Fernet for all sensitive data
- **Password Hashing**: SHA-256 for secure password storage
- **PIN Security**: Separate emergency PIN with same security level
- **Account Lockout**: 3 failed attempts trigger 2-hour lockout
- **Audit Logging**: Complete security event tracking
- **User Isolation**: Each user's data is completely separated

### Security Events Logged
- User registration and login/logout
- Password and PIN changes
- Data entry operations (add, edit, delete)
- Emergency access attempts (successful and failed)
- Account lockouts
- Security setting changes

## 🛡️ Security Considerations

- **Local Storage**: All data stored locally on your machine
- **Encryption**: All sensitive data encrypted at rest
- **No Cloud Sync**: Data never leaves your local machine
- **Key Management**: Encryption keys stored securely
- **Account Lockout**: Protection against brute force attacks
- **Audit Trail**: Complete logging of all security events

## 🔮 Future Enhancements

- [ ] Web-based interface
- [ ] Cloud backup with end-to-end encryption
- [ ] Two-factor authentication (TOTP/SMS)
- [ ] Email notifications for security events
- [ ] Data export/import functionality
- [ ] Mobile app companion
- [ ] Advanced search and filtering
- [ ] Data expiration and auto-deletion
- [ ] Backup and restore functionality
- [ ] Multi-language support

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this project.

## 📄 License

This project is open source and available under the MIT License.

## ⚠️ Disclaimer

This software is provided as-is for educational and personal use. Always backup your data and test thoroughly before storing critical information. The developers are not responsible for any data loss or security breaches. 