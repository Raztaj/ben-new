# Beneficiary Management System Features

This document outlines the key features of the Beneficiary Management System, a comprehensive Flask-based application with an Arabic interface, role-based access control, and an approval workflow.

## Core Functionality

- **Arabic User Interface**: The entire user interface is in Arabic with Right-to-Left (RTL) support, providing a localized user experience.
- **Role-Based Access Control (RBAC)**: The system implements two user roles with distinct permissions:
    - **Admin**: Full control over all system features, including user management and approval of changes.
    - **User**: Can create and view beneficiary records but requires admin approval for modifications and deletions.
- **Approval Workflow**: Non-admin users' changes (updates and deletions) are submitted as pending requests that admins can approve or reject, ensuring data integrity and oversight.
- **CRUD Operations**: Comprehensive Create, Read, Update, and Delete functionality for beneficiary records, with soft-delete to preserve data history.
- **Search and Filtering**: Advanced search capabilities allow users to find beneficiaries by name, ID number, or phone number. Filtering options include status and creation date.

## Data Management

- **Data Export/Import**:
    - **Excel Export**: Export beneficiary data to Excel format, with options to export all records or a filtered subset.
    - **Excel Import**: Import beneficiary data from an Excel file, with a downloadable template to ensure correct formatting.
- **PDF Generation**: Generate professional PDF reports for individual beneficiary profiles, including their personal details and family members.

## Reporting and Analytics

- **Interactive Reports**: The application provides a reports page with various charts and statistics, visualized using Chart.js:
    - **Beneficiary Statistics**: Charts for gender distribution, marital status, and record status.
    - **Age Group Analysis**: A breakdown of beneficiaries by age group.
    - **Monthly Growth**: A chart showing the number of new beneficiaries added each month over the past year.

## User Management (Admin-Only)

- **Admin Panel**: A dedicated settings page for admins to manage user accounts.
- **User Creation**: Admins can create new users and assign them a role (admin or user).
- **Account Management**: Admins can edit user details, including their username, full name, role, and password.
- **Security Features**:
    - Prevents admins from deleting their own accounts.
    - Prevents the deletion of users who have created records in the system to maintain data integrity.

## Technical Features

- **Responsive Design**: The application features a mobile-first, responsive layout that adapts to various screen sizes.
- **Modern UI/UX**: A custom CSS design system with consistent styling, interactive effects, and a user-friendly interface.
- **Form Validation**: Both client-side and server-side validation to ensure data quality.
- **Database Integration**: Uses PostgreSQL with the SQLAlchemy ORM for robust and secure database interactions.
- **API Endpoints**: A set of API endpoints for dynamic frontend functionality, such as live search suggestions and fetching beneficiary data.
