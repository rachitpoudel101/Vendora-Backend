# Vendora

A comprehensive Django-based ERP Driven Inventory Management System designed specifically for stationary and retail businesses. Streamline your operations with powerful inventory tracking, billing, and supplier management capabilities.

---

## 🚀 Core Features

### 📦 Inventory Management
- **Multi-Unit Support**: Manage products with flexible unit types (pieces, boxes, cartons, etc.)
- **Unit Conversion System**: Automatic conversion between different unit types (e.g., 1 box = 12 pieces)
- **Stock Tracking**: Real-time stock level monitoring with low stock alerts
- **Product Categorization**: Organize products by categories with custom attributes
- **Batch & Serial Number Tracking**: Track products by batch numbers and serial numbers
- **Expiry Date Management**: Monitor product expiry dates for perishable items
- **Cost & Margin Control**: Set cost prices and profit margins per product
- **Soft Delete**: Safely delete products without losing historical data

### 💰 Billing & Invoicing
- **Quick Billing**: Fast and efficient point-of-sale billing system
- **Multiple Payment Methods**: Support for cash and online payments
- **Flexible Discounts**: Apply discounts at item level and bill level
- **Tax Management**: Automatic tax and VAT calculations
- **Bill History**: Complete billing history with customer details
- **Real-time Stock Updates**: Automatic inventory deduction on sales
- **User Tracking**: Track which staff member created each bill

### 👥 User Management
- **Role-Based Access Control**: Admin and Staff roles with different permissions
- **User Hierarchy**: Track who created which user account
- **Secure Authentication**: Built-in Django authentication system
- **User Activity Tracking**: Monitor user actions and changes
- **Soft Delete Users**: Deactivate users without losing data

### 🏢 Supplier Management
- **Supplier Database**: Maintain complete supplier contact information
- **Product-Supplier Linking**: Track which products come from which suppliers
- **Supplier History**: View all products supplied by each vendor
- **Contact Management**: Store phone numbers and addresses

### 📊 Dashboard & Analytics
- **Business Insights**: Real-time analytics and reporting
- **Sales Overview**: Track daily, weekly, and monthly sales
- **Inventory Status**: Monitor stock levels and product performance
- **Quick Access**: Centralized dashboard for all key metrics

### 🔔 Notification System
- **System Alerts**: Automated notifications for important events
- **Low Stock Alerts**: Get notified when products run low
- **Expiry Warnings**: Alerts for products nearing expiry dates

---

## 💼 Pricing

### Initial Setup
**NPR 25,000** (One-time)
- Complete system installation and configuration
- Database setup and initial data migration
- User training and documentation
- Basic customization to match your business needs

### Annual License Renewal
**NPR 40,000** (Per Year)
- Software updates and new features
- Security patches and bug fixes
- License renewal for continued use
- Email support for general queries

### Technical Support
**NPR 15,000** (Per Year)
- Priority technical support
- Phone and email assistance
- Issue resolution and troubleshooting
- System maintenance guidance

### Hosting
**Client Responsibility**
- Hosting costs are borne by the client
- Can be deployed on any VPS/cloud provider
- Recommended: DigitalOcean, AWS, or local server
- Estimated hosting cost: NPR 1,000-3,000/month depending on provider

---

## 🎯 Who Is This For?

- Stationary shops and bookstores
- Retail businesses with inventory
- Small to medium-sized enterprises
- Businesses looking to digitize their operations
- Shops needing multi-user access with role management

---

## 📋 System Requirements

- Python 3.8 or higher
- PostgreSQL/MySQL/SQLite database
- 1GB RAM minimum (2GB recommended)
- 10GB storage space
- Linux/Windows/macOS server

---

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
