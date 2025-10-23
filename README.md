# Beneficiary Management System - Flask Reference Implementation

A comprehensive Flask-based beneficiary management system with Arabic interface, role-based access control, and approval workflows. This serves as a complete reference implementation for building a similar system in PHP.

## Features

### Core Functionality
- **Arabic Interface**: Complete RTL support with Arabic text throughout
- **Role-Based Access Control**: Admin and User roles with different permissions
- **Approval Workflow**: Users require admin approval for modifications and deletions
- **CRUD Operations**: Full Create, Read, Update, Delete functionality for beneficiaries
- **Search & Filtering**: Advanced search with multiple filter options
- **Data Export/Import**: Excel import/export with template generation
- **PDF Generation**: Individual beneficiary profile exports
- **Interactive Reports**: Charts and statistics with Chart.js

### User Management
- **Admin Panel**: Complete user management interface
- **User Creation**: Add new users and admins
- **Account Management**: Edit user accounts with role management
- **Security Features**: Prevent self-deletion and unauthorized role changes
- **Activity Tracking**: View user statistics and created records

### Technical Features
- **Responsive Design**: Mobile-first responsive layout
- **Interactive Effects**: Hover animations and visual feedback
- **Form Validation**: Client and server-side validation
- **Session Management**: Secure user sessions
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **Modern UI**: Custom CSS design system with consistent styling

## Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Modern web browser

### Quick Start

1. **Clone/Extract the project files**
2. **Install dependencies**:
   ```bash
   pip install flask flask-sqlalchemy werkzeug openpyxl reportlab python-dateutil psycopg2-binary gunicorn
   ```

3. **Set up environment variables**:
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost/beneficiary_db"
   export SESSION_SECRET="your-secret-key-here"
   ```

4. **Initialize the database**:
   The application will automatically create tables and demo users on first run.

5. **Run the application**:
   ```bash
   python main.py
   ```
   Or with Gunicorn:
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

6. **Access the application**:
   - URL: http://localhost:5000
   - Admin login: `admin` / `admin123`
   - User login: `user` / `user123`

## Project Structure

```
beneficiary-management-system/
├── app.py                 # Flask application setup
├── main.py               # Application entry point
├── models.py             # Database models (User, Record, PendingChange)
├── routes.py             # Application routes and logic
├── utils.py              # Helper functions and decorators
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Main stylesheet with design system
│   └── js/
│       └── main.js       # Client-side JavaScript functionality
├── templates/            # Jinja2 templates
│   ├── base.html         # Base template with navigation
│   ├── login.html        # Login page
│   ├── dashboard.html    # Main dashboard
│   ├── beneficiaries.html # Beneficiary management
│   ├── review_changes.html # Admin approval interface
│   ├── reports.html      # Interactive reports
│   ├── import_export.html # Data import/export
│   └── settings.html     # User management (admin only)
├── README.md             # This documentation
├── INSTALLATION.md       # Detailed installation guide
└── replit.md            # Project architecture and preferences
```

## User Roles & Permissions

### Admin Users
- Full CRUD access to all beneficiaries
- Direct modification without approval
- Access to user management settings
- Approve/reject change requests from users
- View all reports and statistics
- Import/export data
- Manage system users

### Regular Users
- Create new beneficiary records
- View all beneficiary data
- Request modifications (requires admin approval)
- Request deletions (requires admin approval)
- View reports and statistics
- Export data
- Limited system access

## Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `password_hash` (Encrypted)
- `full_name`
- `role` (admin/user)
- `created_at`

### Records Table (Beneficiaries)
- `id` (Primary Key)
- `first_name`, `father_name`, `grandfather_name`, `family_name`
- `id_passport_number` (Unique)
- `date_of_birth`
- `gender` (ذكر/أنثى)
- `marital_status` (أعزب/متزوج/أرمل/مطلق)
- `phone_number`
- `family_members_count`
- `address`
- `status` (مكتمل/بحاجة لمراجعة/غير نشط)
- `created_by_user_id` (Foreign Key)
- `created_at`, `updated_at`

### Pending Changes Table
- `id` (Primary Key)
- `record_id` (Foreign Key)
- `user_id` (Foreign Key)
- `change_type` (update/delete)
- `changed_data` (JSON)
- `status` (pending/approved/rejected)
- `created_at`
- `reviewed_by`, `reviewed_at`

## Key Features Explained

### Approval Workflow
When a regular user attempts to modify or delete a beneficiary:
1. The change is stored in `pending_changes` table
2. Admin receives notification in the dashboard
3. Admin can review, approve, or reject the change
4. Upon approval, the change is applied to the original record

### Import/Export System
- **Template Download**: Provides Excel template with proper headers
- **Data Import**: Validates and imports Excel files with error handling
- **Data Export**: Multiple export options (all, filtered, by status)
- **PDF Generation**: Individual beneficiary profiles

### Design System
The application uses a comprehensive CSS design system with:
- Custom CSS variables for consistent theming
- Arabic typography and RTL layout
- Interactive hover effects and animations
- Responsive grid layouts
- Status-based color coding
- Accessible form controls

## Security Features

- **Password Hashing**: Uses Werkzeug's secure password hashing
- **Session Management**: Secure server-side sessions
- **Role-Based Access**: Decorator-based route protection
- **Input Validation**: Both client and server-side validation
- **CSRF Protection**: Form-based CSRF protection
- **SQL Injection Prevention**: ORM-based queries

## Customization

### Adding New Fields
1. Update the `Record` model in `models.py`
2. Add fields to forms in templates
3. Update validation in `main.js`
4. Modify export/import logic in `routes.py`

### Styling Changes
All styles are in `static/css/style.css` using CSS variables for easy theming:
- `--primary`: Main brand color
- `--secondary`: Secondary accent color
- `--success`, `--warning`, `--danger`: Status colors
- `--light`, `--dark`: Background and text colors

### Adding New Reports
Reports are generated in the `/reports` route and displayed using Chart.js. Add new queries and chart configurations as needed.

## Production Deployment

### Environment Setup
```bash
export FLASK_ENV=production
export DATABASE_URL="postgresql://user:pass@host:port/dbname"
export SESSION_SECRET="secure-random-key"
```

### Gunicorn Configuration
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 main:app
```

### Database Optimization
- Set up connection pooling
- Configure appropriate indexes
- Regular database maintenance

## API Endpoints

The system includes several AJAX endpoints for dynamic functionality:
- `/api/search_suggestions` - Live search suggestions
- `/api/statistics` - Dashboard statistics
- `/export_records` - Data export with filters
- `/generate_pdf/<id>` - PDF generation

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance Considerations

- Database queries are optimized with proper indexing
- Static assets are cached
- Pagination for large datasets
- Responsive images and optimized CSS
- Minimal JavaScript dependencies

## Troubleshooting

### Common Issues
1. **Database Connection**: Verify DATABASE_URL environment variable
2. **Permission Errors**: Check user roles and decorators
3. **Import Failures**: Validate Excel file format and data
4. **Session Issues**: Verify SESSION_SECRET is set

### Debug Mode
Set `debug=True` in `main.py` for development debugging.

## License

This is a reference implementation for educational and development purposes.

## Support

This Flask implementation serves as a complete reference for building the PHP version. All features, database schema, and workflows can be directly translated to PHP/MySQL.

For PHP implementation:
- Replace Flask routes with PHP files
- Use MySQL instead of PostgreSQL
- Replace Jinja2 templates with PHP templating
- Use PHPSpreadsheet instead of openpyxl
- Implement similar session management in PHP

The UI/UX, database structure, and business logic remain identical across implementations.