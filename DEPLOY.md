# Deploying Bar Inventory to PythonAnywhere

This guide provides step-by-step instructions for deploying the Bar Inventory Management System to PythonAnywhere.

## Prerequisites

- A PythonAnywhere account (Free or paid)
- The code repository at: https://github.com/infodot-be/bar-inventory/
- Basic knowledge of Linux command line

## Deployment Steps

### 1. Create PythonAnywhere Account

1. Go to [PythonAnywhere](https://www.pythonanywhere.com/)
2. Sign up for an account (Free or paid plan)
3. Note: Free accounts have some limitations (no HTTPS on custom domains, daily quota)

### 2. Open a Bash Console

1. Log in to your PythonAnywhere dashboard
2. Click on "Consoles" tab
3. Start a new "Bash" console

### 3. Clone the Repository

```bash
cd ~
git clone https://github.com/infodot-be/bar-inventory.git
cd bar-inventory
```

### 4. Create Virtual Environment

```bash
# Create virtual environment with Python 3.10 or higher
mkvirtualenv --python=/usr/bin/python3.10 bar-inventory

# If mkvirtualenv doesn't work, use:
python3.10 -m venv ~/bar-inventory-venv
source ~/bar-inventory-venv/bin/activate
```

### 5. Install Dependencies

```bash
# Make sure virtual environment is activated
workon bar-inventory  # or: source ~/bar-inventory-venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If you encounter issues with `mysqlclient` on the free tier, you can:
- Use SQLite (default for dev mode)
- Or upgrade to a paid plan for MySQL support

### 6. Configure Settings

**Note:** You do not need to manually edit `settings.py` for production. All configuration (SECRET_KEY, DEBUG, ALLOWED_HOSTS, security settings, database credentials) will be set via environment variables in the WSGI file (step 10).

The settings.py file is already configured to read from environment variables with sensible defaults for development.

### 7. Set Up Static Files

**Note:** STATIC_ROOT will be configured via environment variable in the WSGI file (step 10).

Collect static files:

```bash
cd ~/bar-inventory/code
python manage.py collectstatic --noinput
```

**Note:** This step may fail if STATIC_ROOT is not set yet. If it does, skip for now and run it again after configuring the WSGI file (step 10) and reloading the web app.

### 8. Run Database Migrations

```bash
cd ~/bar-inventory/code

# Run migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 9. Configure Web App on PythonAnywhere

1. Go to the "Web" tab in your PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose "Manual configuration" (not Django wizard)
4. Select Python 3.10

### 10. Configure WSGI File

**This is the most important step for security!** All production settings are configured here.

1. In the Web tab, click on the WSGI configuration file link
2. Replace the entire contents with the configuration below
3. **Important replacements to make:**
   - Replace `yourusername` with your actual PythonAnywhere username (4 places)
   - Generate a unique SECRET_KEY at https://djecrety.ir/ and replace the placeholder
   - Update domain names to match your actual domain(s)
   - If using MySQL, uncomment and configure the database settings at the bottom

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/bar-inventory/code'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'bar_inventory.settings'

# Set SECRET_KEY (generate a new one at https://djecrety.ir/)
os.environ['SECRET_KEY'] = 'your-production-secret-key-here-replace-with-generated-key'

# Set DEBUG to False for production
os.environ['DEBUG'] = 'False'

# Set ALLOWED_HOSTS (comma-separated list of domains)
os.environ['ALLOWED_HOSTS'] = 'yourusername.pythonanywhere.com'
# For multiple domains: 'yourusername.pythonanywhere.com,custom-domain.com'

# Static files directory (required for collectstatic)
os.environ['STATIC_ROOT'] = '/home/yourusername/bar-inventory/code/static'

# Security settings for production
# Note: PythonAnywhere provides HTTPS on *.pythonanywhere.com domains automatically
os.environ['SESSION_COOKIE_SECURE'] = 'True'  # HTTPS only cookies
os.environ['CSRF_COOKIE_SECURE'] = 'True'  # HTTPS only CSRF cookies
os.environ['SECURE_SSL_REDIRECT'] = 'True'  # Redirect HTTP to HTTPS
os.environ['SECURE_HSTS_SECONDS'] = '31536000'  # 1 year HSTS
os.environ['SECURE_HSTS_INCLUDE_SUBDOMAINS'] = 'True'
os.environ['SECURE_HSTS_PRELOAD'] = 'True'

# CSRF Protection: Add your domains with https:// prefix (required for POST requests)
os.environ['CSRF_TRUSTED_ORIGINS'] = 'https://yourusername.pythonanywhere.com'
# If you have a custom domain, add it (comma-separated):
# os.environ['CSRF_TRUSTED_ORIGINS'] = 'https://yourusername.pythonanywhere.com,https://your-custom-domain.com'

# Token expiration (optional, default is 3600 seconds = 1 hour)
# Reduce this value for higher security environments
# os.environ['PASSWORD_RESET_TIMEOUT'] = '3600'

# Database configuration
# For FREE tier: Use SQLite (default, no configuration needed)
# For PAID tier with MySQL: Uncomment and configure below
# os.environ['DJANGO_ENV'] = 'prod'
# os.environ['DB_HOST'] = 'yourusername.mysql.pythonanywhere-services.com'
# os.environ['DB_NAME'] = 'yourusername$bar_inventory'
# os.environ['DB_USER'] = 'yourusername'
# os.environ['DB_PASSWORD'] = 'your-secure-database-password'

# Activate virtual environment
activate_this = '/home/yourusername/.virtualenvs/bar-inventory/bin/activate_this.py'
# OR if using venv:
# activate_this = '/home/yourusername/bar-inventory-venv/bin/activate_this.py'

with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Security Checklist for WSGI Configuration:**

Before proceeding, verify you have:
- [ ] Generated unique SECRET_KEY from https://djecrety.ir/ (never use the default!)
- [ ] Set DEBUG='False' for production
- [ ] Set ALLOWED_HOSTS to your actual domain(s) only (remove generic values)
- [ ] Enabled all security settings (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE, etc.)
- [ ] Set CSRF_TRUSTED_ORIGINS with https:// prefix for your actual domain(s)
- [ ] Configured database credentials if using MySQL
- [ ] Replaced ALL instances of 'yourusername' with your actual PythonAnywhere username
- [ ] Saved the file

**Important:** Replace `yourusername` with your actual PythonAnywhere username.

**Security Checklist for WSGI Configuration:**

Before proceeding, verify you have:
- [ ] Generated unique SECRET_KEY from https://djecrety.ir/ (never use the default!)
- [ ] Set DEBUG='False' for production
- [ ] Set ALLOWED_HOSTS to your actual domain(s) only (e.g., 'yourusername.pythonanywhere.com')
- [ ] Enabled all security settings (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE, SECURE_SSL_REDIRECT, HSTS)
- [ ] Set CSRF_TRUSTED_ORIGINS with https:// prefix (e.g., 'https://yourusername.pythonanywhere.com')
- [ ] Configured database credentials if using MySQL (paid tier only)
- [ ] Replaced ALL instances of 'yourusername' with your actual PythonAnywhere username
- [ ] Saved the WSGI configuration file

**Note on Security Settings:**
- All HTTPS/SSL security settings are enabled by default in the configuration above
- PythonAnywhere provides automatic HTTPS for *.pythonanywhere.com domains
- These settings ensure cookies are only sent over HTTPS and implement HSTS for long-term security
- For custom domains, you'll need to configure SSL certificates separately

### 11. Configure Static Files Mapping

In the Web tab, under "Static files" section:

| URL | Directory |
|-----|-----------|
| /static/ | /home/yourusername/bar-inventory/code/static |

### 12. Configure Virtual Environment

In the Web tab, under "Virtualenv" section:

Enter the path to your virtual environment:
```
/home/yourusername/.virtualenvs/bar-inventory
```
or
```
/home/yourusername/bar-inventory-venv
```

### 13. Reload Web App

1. Click the green "Reload" button at the top of the Web tab
2. Visit your site: `https://yourusername.pythonanywhere.com`

## Optional: MySQL Configuration (Paid Plans Only)

If you have a paid PythonAnywhere account and want to use MySQL:

### 1. Create MySQL Database

1. Go to the "Databases" tab
2. Create a new database (e.g., `yourusername$bar_inventory`)
3. Note the database name, username, and password

### 2. Update Settings

```python
# In settings.py, ensure DJANGO_ENV can be set via environment
DJANGO_ENV = os.environ.get('DJANGO_ENV', 'dev')
```

### 3. Set Environment Variable in WSGI

```python
# In your WSGI file, add:
os.environ['SECRET_KEY'] = 'your-production-secret-key-here'
os.environ['DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = 'yourusername.pythonanywhere.com,your-custom-domain.com'

# Security settings for production
os.environ['SESSION_COOKIE_SECURE'] = 'True'
os.environ['CSRF_COOKIE_SECURE'] = 'True'
os.environ['SECURE_SSL_REDIRECT'] = 'True'
os.environ['SECURE_HSTS_SECONDS'] = '31536000'
os.environ['SECURE_HSTS_INCLUDE_SUBDOMAINS'] = 'True'
os.environ['SECURE_HSTS_PRELOAD'] = 'True'
os.environ['CSRF_TRUSTED_ORIGINS'] = 'https://yourusername.pythonanywhere.com,https://your-custom-domain.com'

# MySQL database configuration
os.environ['DJANGO_ENV'] = 'prod'
os.environ['DB_HOST'] = 'yourusername.mysql.pythonanywhere-services.com'
os.environ['DB_NAME'] = 'yourusername$bar_inventory'
os.environ['DB_USER'] = 'yourusername'
os.environ['DB_PASSWORD'] = 'your-database-password'
```

### 4. Run Migrations

```bash
cd ~/bar-inventory/code
python manage.py migrate
python manage.py createsuperuser
```

## Initial Setup After Deployment

### 1. Access Admin Panel

1. Visit: `https://yourusername.pythonanywhere.com/admin`
2. Log in with the superuser account you created

### 2. Configure Application

1. **Add Unit Types**
   - Go to Unit Types
   - Add: Barrel (50L), Tray (12L), Bottle (0.5L), etc.

2. **Add Locations**
   - Go to Locations
   - Create your bar locations (Main Bar, Pool Area, etc.)

3. **Add Beverages**
   - Go to Beverages
   - Add beverages with:
     - Name
     - Unit type
     - Liters per unit
     - Available locations
     - Alarm minimum
     - Color for charts

4. **Create Location Users** (Optional)
   - Go to Users
   - Create users for each location
   - Assign them to specific locations

## Troubleshooting

### Static Files Not Loading

1. Check static files mapping in Web tab
2. Verify STATIC_ROOT is set correctly in settings.py
3. Run `collectstatic` again: `python manage.py collectstatic --noinput`
4. Check file permissions: `chmod -R 755 ~/bar-inventory/code/static`
5. Clear browser cache

### CSRF/Cookie Issues

If you see CSRF token errors or login issues:

1. **Check CSRF_TRUSTED_ORIGINS:**
   - Must include `https://` prefix
   - Must match your actual domain exactly
   - Example: `'https://yourusername.pythonanywhere.com'`

2. **Verify Security Settings:**
   - If testing locally without HTTPS, temporarily set:
     - `SESSION_COOKIE_SECURE = 'False'`
     - `CSRF_COOKIE_SECURE = 'False'`
   - **Never do this in production!**

3. **Check ALLOWED_HOSTS:**
   - Must include your domain without protocol
   - Example: `'yourusername.pythonanywhere.com'`

### HTTP Redirect Loop

If you get endless redirects after enabling SECURE_SSL_REDIRECT:

1. PythonAnywhere handles HTTPS automatically for *.pythonanywhere.com
2. Verify you're accessing via https:// not http://
3. Clear browser cache and cookies
4. Check Web tab shows "HTTPS: Enabled"

### Database Errors

1. Ensure migrations have been run
2. Check database credentials in settings.py
3. For MySQL, verify database exists in Databases tab

### 500 Internal Server Error

1. Check error log in Web tab (very important!)
2. Common causes:
   - Missing or invalid SECRET_KEY in WSGI
   - Syntax error in WSGI configuration
   - Missing environment variables
   - Import errors in code
3. Temporarily enable DEBUG to see detailed errors:
   - Set `os.environ['DEBUG'] = 'True'` in WSGI
   - Reload web app
   - **Remember to set back to 'False' after fixing!**
4. Check WSGI configuration file for syntax errors
5. Verify all required environment variables are set

### Authentication/Token Login Issues

If token login links don't work:

1. **Check Token Expiration:**
   - Tokens expire after 1 hour by default
   - Generate a new token link

2. **Verify User is Active:**
   - Check in admin that user account is active
   - Inactive users cannot log in via tokens

3. **Check Logs:**
   - View error log in PythonAnywhere Web tab
   - Look for authentication failures

4. **ALLOWED_HOSTS Configuration:**
   - Token generation uses `request.build_absolute_uri()`
   - Requires correct ALLOWED_HOSTS setting

### Import Errors

1. Verify virtual environment path in Web tab
2. Check all dependencies are installed: `pip list`
3. Ensure project path is in sys.path in WSGI file

## Updating the Application

To update your deployed application:

```bash
# SSH into PythonAnywhere console
cd ~/bar-inventory

# Pull latest changes
git pull origin main

# Activate virtual environment
workon bar-inventory

# Install any new dependencies
pip install -r requirements.txt

# Run migrations
cd code
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Reload web app (from dashboard or using API)
```

Then reload your web app from the Web tab.

## Security Checklist

Before going live, verify:

- [ ] Set `DEBUG` environment variable to `'False'` in WSGI file
- [ ] Generated and set unique `SECRET_KEY` in WSGI file (use https://djecrety.ir/)
- [ ] Set `ALLOWED_HOSTS` with your actual domain(s) in WSGI file (comma-separated, no wildcards)
- [ ] Enable HTTPS security settings: `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT`
- [ ] Configure HSTS headers for long-term HTTPS enforcement (31536000 seconds = 1 year)
- [ ] Set `CSRF_TRUSTED_ORIGINS` with HTTPS URLs (must include https:// prefix)
- [ ] Database credentials are secure (set in WSGI file, not in code)
- [ ] Admin account has strong password (12+ characters, mixed case, numbers, symbols)
- [ ] Review and monitor authentication logs for suspicious activity
- [ ] Token links expire after 1 hour (PASSWORD_RESET_TIMEOUT default)
- [ ] Regular backups configured and tested
- [ ] HTTPS enabled (automatic on PythonAnywhere *.pythonanywhere.com domains)
- [ ] All instances of 'yourusername' replaced with actual username
- [ ] No sensitive data committed to version control

**For comprehensive security guidance, see [SECURITY.md](SECURITY.md)**
- [ ] HTTPS enabled (automatic on PythonAnywhere)

## Custom Domain Setup (Paid Plans)

If you want to use a custom domain:

1. Go to Web tab
2. Add custom domain in "Domain names" section
3. Update DNS records at your domain registrar:
   - Add CNAME record pointing to `yourusername.pythonanywhere.com`
4. Update `ALLOWED_HOSTS` environment variable in WSGI file to include your custom domain
5. Reload web app

## Backup Strategy

### Manual Backup

```bash
# Backup SQLite database
cd ~/bar-inventory/code
cp db.sqlite3 ~/backups/db.sqlite3.$(date +%Y%m%d)

# For MySQL
mysqldump -u yourusername -p yourusername$bar_inventory > ~/backups/backup_$(date +%Y%m%d).sql
```

### Scheduled Backups

Create a scheduled task in PythonAnywhere:

```bash
#!/bin/bash
cd /home/yourusername/bar-inventory/code
cp db.sqlite3 /home/yourusername/backups/db.sqlite3.$(date +\%Y\%m\%d)
```

Schedule this daily in the "Tasks" tab.

## Quick Reference

### Environment Variables (Set in WSGI file)

**Required for Production:**
```python
SECRET_KEY='...'                    # Generate at https://djecrety.ir/
DEBUG='False'                       # Must be False in production
ALLOWED_HOSTS='domain.com'          # Your actual domain(s), comma-separated
STATIC_ROOT='/path/to/static'       # Absolute path for collected static files
```

**Security Settings (Recommended):**
```python
SESSION_COOKIE_SECURE='True'        # HTTPS only session cookies
CSRF_COOKIE_SECURE='True'           # HTTPS only CSRF tokens
SECURE_SSL_REDIRECT='True'          # Force HTTPS
SECURE_HSTS_SECONDS='31536000'      # 1 year HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS='True'
SECURE_HSTS_PRELOAD='True'
CSRF_TRUSTED_ORIGINS='https://domain.com'  # Include https:// prefix
```

**Database (MySQL - Paid plans only):**
```python
DJANGO_ENV='prod'
DB_HOST='username.mysql.pythonanywhere-services.com'
DB_NAME='username$bar_inventory'
DB_USER='username'
DB_PASSWORD='...'
DB_PORT='3306'
```

**Optional:**
```python
PASSWORD_RESET_TIMEOUT='3600'       # Token expiration (default 1 hour)
```

### Common PythonAnywhere Commands

```bash
# Reload web app
touch /var/www/yourusername_pythonanywhere_com_wsgi.py

# View error logs
tail -f /var/log/yourusername.pythonanywhere.com.error.log

# Run Django management commands
cd ~/bar-inventory/code
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# Update from git
cd ~/bar-inventory
git pull origin main
```

### Important Paths

- **Project directory:** `/home/yourusername/bar-inventory`
- **Code directory:** `/home/yourusername/bar-inventory/code`
- **Virtual environment:** `/home/yourusername/.virtualenvs/bar-inventory`
- **Static files:** `/home/yourusername/bar-inventory/code/static`
- **WSGI file:** `/var/www/yourusername_pythonanywhere_com_wsgi.py`
- **Error logs:** `/var/log/yourusername.pythonanywhere.com.error.log`

## Support

- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **PythonAnywhere Forums:** https://www.pythonanywhere.com/forums/
- **Django Documentation:** https://docs.djangoproject.com/
- **Project Repository:** https://github.com/infodot-be/bar-inventory/

## Additional Resources

### Documentation
- [PythonAnywhere Django Tutorial](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [Project Security Guide](SECURITY.md) - Comprehensive security documentation for this project

### Tools
- [Django Secret Key Generator](https://djecrety.ir/) - Generate secure SECRET_KEY
- [SSL Server Test](https://www.ssllabs.com/ssltest/) - Test your HTTPS configuration
- [Security Headers](https://securityheaders.com/) - Check your security headers

### PythonAnywhere-Specific
- [PythonAnywhere Security](https://help.pythonanywhere.com/pages/security/)
- [Working with Git on PythonAnywhere](https://help.pythonanywhere.com/pages/ExternalVCS/)
- [Setting up MySQL](https://help.pythonanywhere.com/pages/MySQL/)
- [Scheduled Tasks](https://help.pythonanywhere.com/pages/ScheduledTasks/)

---

**Last Updated:** January 14, 2026

**Deployment Checklist:** Before going live, review the Security Checklist above and [SECURITY.md](SECURITY.md)
