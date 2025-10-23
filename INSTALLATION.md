# Installation Guide - Beneficiary Management System

## System Requirements

### Software Prerequisites
- Python 3.11 or higher
- PostgreSQL 13+ (or compatible database)
- Git (for version control)
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

### Hardware Requirements
- Minimum 2GB RAM
- 500MB free disk space
- Internet connection for CDN resources (Font Awesome, Chart.js)

## Installation Options

### Option 1: Local Development Setup

#### Step 1: Prepare Environment
```bash
# Create project directory
mkdir beneficiary-management-system
cd beneficiary-management-system

# Extract project files here
# (Copy all files from the zip archive)
```

#### Step 2: Install Python Dependencies
```bash
# Using pip
pip install flask flask-sqlalchemy werkzeug openpyxl reportlab python-dateutil psycopg2-binary gunicorn

# Or using requirements.txt (if provided)
pip install -r requirements.txt
```

#### Step 3: Database Setup

**PostgreSQL Installation:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql postgresql-server postgresql-contrib

# macOS (using Homebrew)
brew install postgresql
```

**Create Database:**
```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql

-- Create database and user
CREATE DATABASE beneficiary_db;
CREATE USER beneficiary_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE beneficiary_db TO beneficiary_user;
\q
```

#### Step 4: Environment Configuration
```bash
# Set environment variables
export DATABASE_URL="postgresql://beneficiary_user:your_password_here@localhost:5432/beneficiary_db"
export SESSION_SECRET="your-secure-random-secret-key-min-32-chars"

# For persistent settings, add to ~/.bashrc or ~/.zshrc
echo 'export DATABASE_URL="postgresql://beneficiary_user:your_password_here@localhost:5432/beneficiary_db"' >> ~/.bashrc
echo 'export SESSION_SECRET="your-secure-random-secret-key-min-32-chars"' >> ~/.bashrc
source ~/.bashrc
```

#### Step 5: Initialize and Run
```bash
# Initialize database (automatic on first run)
python main.py

# Or run with Gunicorn for production
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 main:app
```

### Option 2: Docker Setup (Alternative)

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "main:app"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/beneficiary_db
      - SESSION_SECRET=your-secret-key-here
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=beneficiary_db
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Initial Setup and Testing

### Step 1: Access the Application
1. Open browser and navigate to: `http://localhost:5000`
2. You should see the login page

### Step 2: Default Login Credentials
```
Admin Account:
Username: admin
Password: admin123

Regular User Account:
Username: user
Password: user123
```

### Step 3: Verify Functionality
1. **Login Test**: Log in with admin credentials
2. **Dashboard**: Check statistics display correctly
3. **Add Beneficiary**: Create a test beneficiary record
4. **User Switching**: Logout and login as regular user
5. **Approval Workflow**: Edit a record as user, then approve as admin
6. **Reports**: Verify charts display with sample data
7. **Export**: Test Excel export functionality

## Configuration Options

### Database Configuration
```python
# In app.py, modify these settings:
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,        # Recycle connections every 5 minutes
    "pool_pre_ping": True,      # Validate connections before use
    "pool_size": 10,            # Connection pool size
    "max_overflow": 20          # Max overflow connections
}
```

### Session Configuration
```python
# Security settings
app.config['SESSION_COOKIE_SECURE'] = True     # HTTPS only (production)
app.config['SESSION_COOKIE_HTTPONLY'] = True   # Prevent XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=4)  # Session timeout
```

### File Upload Limits
```python
# Add to app.py for import functionality
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
```

## Production Deployment

### Environment Variables
```bash
# Production environment
export FLASK_ENV=production
export DATABASE_URL="postgresql://user:pass@prod-host:5432/beneficiary_db"
export SESSION_SECRET="cryptographically-secure-secret-key"

# Optional optimizations
export SQLALCHEMY_ENGINE_OPTIONS='{"pool_size": 20, "max_overflow": 40}'
```

### Nginx Configuration (Optional)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Systemd Service (Linux)
```ini
# /etc/systemd/system/beneficiary-app.service
[Unit]
Description=Beneficiary Management System
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=beneficiary-app
WorkingDirectory=/path/to/app
Environment=DATABASE_URL=postgresql://user:pass@localhost/beneficiary_db
Environment=SESSION_SECRET=your-secret-key
ExecStart=/usr/local/bin/gunicorn --bind unix:/run/beneficiary-app/socket --workers 4 main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

## Security Hardening

### Database Security
1. **Use dedicated database user** with minimal privileges
2. **Enable SSL connections** for database
3. **Regular backups** with encryption
4. **Network restrictions** (firewall rules)

### Application Security
1. **Strong session secrets** (minimum 32 characters)
2. **HTTPS in production** (SSL/TLS certificates)
3. **Regular security updates** for dependencies
4. **Input validation** (already implemented)
5. **Rate limiting** (add nginx/reverse proxy rules)

### File Security
```bash
# Set proper file permissions
chmod 644 *.py *.html *.css *.js
chmod 600 config_files_with_secrets
chmod 755 directories
```

## Backup and Maintenance

### Database Backup
```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/beneficiary-db"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > "$BACKUP_DIR/backup_$DATE.sql"

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

### Log Management
```bash
# Configure log rotation
sudo nano /etc/logrotate.d/beneficiary-app

# Add configuration:
/var/log/beneficiary-app/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
```

## Troubleshooting

### Common Issues

**Database Connection Errors:**
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Test connection
psql $DATABASE_URL

# Check logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

**Permission Errors:**
```bash
# Check file permissions
ls -la /path/to/app

# Fix ownership
sudo chown -R www-data:www-data /path/to/app
```

**Import/Export Issues:**
```bash
# Check disk space
df -h

# Check Python packages
pip list | grep -E "(openpyxl|reportlab)"

# Test file permissions
touch /tmp/test.xlsx && rm /tmp/test.xlsx
```

**Performance Issues:**
```bash
# Check system resources
htop
iostat 1 5

# Database performance
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity;"

# Application logs
tail -f application.log
```

### Debug Mode
For development debugging:
```python
# In main.py
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Health Check Endpoint
Add to routes.py:
```python
@app.route('/health')
def health_check():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return {'status': 'healthy'}, 200
    except:
        return {'status': 'unhealthy'}, 500
```

## Migration from Development to Production

1. **Environment Setup**: Configure production environment variables
2. **Database Migration**: Export dev data, import to production
3. **Static Files**: Configure proper serving (nginx/apache)
4. **Security**: Enable HTTPS, set secure headers
5. **Monitoring**: Set up logging and monitoring
6. **Backup**: Configure automated backups
7. **Testing**: Perform full functionality testing

## Support and Maintenance

### Regular Tasks
- **Weekly**: Check application logs
- **Monthly**: Update dependencies
- **Quarterly**: Security audit
- **Annually**: Full system review

### Monitoring
- Database performance
- Application response times
- Error rates
- Resource usage
- Security events

This installation guide provides a complete setup process for the Beneficiary Management System. Follow the steps carefully and test each component to ensure proper functionality.