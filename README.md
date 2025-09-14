# Vendora

This project is a Django-based ERP Driven Inventory Management System designed to handle inventory, billing, user management, notifications, and supplier management for a stationary business.

## Project Structure

- **core/**: Main Django project folder
  - **apps/**: Contains Django apps
    - **billing/**: Billing and invoice management
    - **dashboard/**: Dashboard and analytics
    - **inventory/**: Inventory and stock management
    - **notifications/**: User and system notifications
    - **Supliers/**: Supplier management
    - **users/**: User authentication and management
  - **config/**: Project configuration and settings
  - **requirements/**: Dependency files
  - **urls/**: URL routing for different apps
  - **asgi.py, wsgi.py**: ASGI and WSGI entry points

## Features
- Inventory tracking and management
- Billing and invoicing
- User authentication and permissions
- Supplier management
- Dashboard analytics
- Notification system

## Setup Instructions
1. Clone the repository
2. Create a virtual environment and activate it:
   - **Linux/macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - **Windows**:
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements/base.txt
   ```
4. Configure environment variables in `.env`
5. Apply migrations:
   ```bash
   python manage.py migrate
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Requirements
All Python dependencies for this project are listed in `requirements/base.txt`. To install them, use:
```bash
pip install -r requirements/base.txt
```
To add new dependencies, update `requirements/base.txt` and re-run the install command.


## Contact
E-mail:rachit300poudel@gmail.com
