Password Manager

About the Project

A simple Python desktop application that helps users store and manage passwords securely using encryption.

Features

- Add website and username details.
- Encrypt passwords using Fernet encryption.
- View saved passwords.
- Delete saved entries.
- Store records in an SQLite database.

Technologies Used

- Python 3
- Tkinter
- SQLite
- Cryptography (Fernet)

How to Run

1. Install Python 3.

2. Install the required library:
   
   "python -m pip install cryptography"

3. Run the application:
   
   "python password_manager.py"

Security

Keep the encryption key private. Never upload secret keys or databases containing passwords to a public repository.
