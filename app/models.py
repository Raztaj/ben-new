
# This file defines the database models for the application using SQLAlchemy.
# It includes models for Users, Records (beneficiaries), and PendingChanges for the approval workflow.

from datetime import datetime
from flask_login import UserMixin
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """
    Represents a user in the system.
    Can have either 'admin' or 'user' role.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum('admin', 'user', name='user_roles'), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Relationships ---
    # Defines the records created by this user.
    created_records = db.relationship('Record', foreign_keys='Record.created_by_user_id', backref='creator', lazy='dynamic')
    # Defines the change requests made by this user.
    pending_changes = db.relationship('PendingChange', foreign_keys='PendingChange.user_id', backref='requester', lazy='dynamic')
    # Defines the change requests reviewed by this user (admin only).
    reviewed_changes = db.relationship('PendingChange', foreign_keys='PendingChange.reviewed_by', backref='reviewer', lazy='dynamic')

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Returns True if the user has the 'admin' role."""
        return self.role == 'admin'

class Record(db.Model):
    """
    Represents a beneficiary record in the system.
    Each record can be a head of household or a family member linked to a head of household.
    """
    __tablename__ = 'records'

    # --- Basic Information ---
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    grandfather_name = db.Column(db.String(100), nullable=False)
    family_name = db.Column(db.String(100), nullable=False)
    id_passport_number = db.Column(db.String(50), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('ذكر', 'أنثى', name='gender_types'), nullable=False)
    marital_status = db.Column(db.Enum('أعزب', 'متزوج', 'أرمل', 'مطلق', name='marital_status_types'), nullable=False)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.Text)

    # --- Metadata ---
    status = db.Column(db.Enum('مكتمل', 'بحاجة لمراجعة', 'غير نشط', name='status_types'), nullable=False, default='بحاجة لمراجعة')
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

    # --- Relationships ---
    # Defines the pending changes associated with this record.
    pending_changes = db.relationship('PendingChange', backref='record', lazy='dynamic', foreign_keys='PendingChange.record_id')

    # Self-referential relationship for head of household structure.
    # A record can be a head of household (head_of_household_id is NULL) or a family member.
    head_of_household_id = db.Column(db.Integer, db.ForeignKey('records.id'), nullable=True)
    # Defines the list of family members for a head of household.
    family_members = db.relationship('Record',
                                     backref=db.backref('head_of_household', remote_side=[id]),
                                     lazy='dynamic',
                                     foreign_keys='Record.head_of_household_id'
                                    )

    # --- Dynamic Properties ---
    @property
    def full_name(self):
        """Returns the full name of the beneficiary."""
        return f"{self.first_name} {self.father_name} {self.grandfather_name} {self.family_name}"

    @property
    def status_english(self):
        """Translates the status from Arabic to English."""
        status_map = {
            'مكتمل': 'Completed',
            'بحاجة لمراجعة': 'Needs Review',
            'غير نشط': 'Inactive'
        }
        return status_map.get(self.status, self.status)

    @property
    def age(self):
        """Calculates the age of the beneficiary based on date of birth."""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    @property
    def family_members_count(self):
        """
        Dynamically calculates the number of family members for a head of household.
        Returns 0 for non-heads of household. This avoids data inconsistency.
        """
        if self.head_of_household_id is None:
            return self.family_members.count()
        return 0

class PendingChange(db.Model):
    """
    Represents a change request (update or delete) submitted by a regular user.
    These changes must be approved or rejected by an admin.
    """
    __tablename__ = 'pending_changes'

    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('records.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    change_type = db.Column(db.Enum('update', 'delete', name='change_types'), nullable=False)
    # For 'update' changes, this stores a JSON string of the new data.
    changed_data = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'approved', 'rejected', name='pending_status_types'), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
