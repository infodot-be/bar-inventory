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

Edit the Django settings for production:

```bash
nano ~/bar-inventory/code/bar_inventory/settings.py
```

Make these changes:

```python
# Add your PythonAnywhere domain to ALLOWED_HOSTS
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com', 'your-custom-domain.com']

# Note: SECRET_KEY and DEBUG will be set via environment variables in WSGI file
# For free tier, use SQLite (keep DJANGO_ENV=dev)
# For paid tier with MySQL, set DJANGO_ENV=prod and configure database credentials
```

### 7. Set Up Static Files

```bash
cd ~/bar-inventory/code

# Collect static files
python manage.py collectstatic --noinput
```

Update settings.py to add:

```python
STATIC_ROOT = '/home/yourusername/bar-inventory/code/static'
STATIC_URL = '/static/'
```

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

1. In the Web tab, click on the WSGI configuration file link
2. Replace the entire contents with:

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

# For production, you might want to set DJANGO_ENV
# os.environ['DJANGO_ENV'] = 'dev'  # or 'prod' if using MySQL

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

**Important:** Replace `yourusername` with your actual PythonAnywhere username.

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
2. Run `collectstatic` again
3. Check file permissions: `chmod -R 755 ~/bar-inventory/code/static`

### Database Errors

1. Ensure migrations have been run
2. Check database credentials in settings.py
3. For MySQL, verify database exists in Databases tab

### 500 Internal Server Error

1. Check error log in Web tab
2. Enable DEBUG temporarily to see detailed errors
3. Check WSGI configuration file for syntax errors

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

- [ ] Set `DEBUG` environment variable to `'False'` in WSGI file
- [ ] Generated and set unique `SECRET_KEY` in WSGI file (use https://djecrety.ir/)
- [ ] Added proper domains to `ALLOWED_HOSTS` in settings.py
- [ ] Database credentials are secure (set in WSGI file, not in code)
- [ ] Admin account has strong password
- [ ] Regular backups configured
- [ ] HTTPS enabled (automatic on PythonAnywhere)

## Custom Domain Setup (Paid Plans)

If you want to use a custom domain:

1. Go to Web tab
2. Add custom domain in "Domain names" section
3. Update DNS records at your domain registrar:
   - Add CNAME record pointing to `yourusername.pythonanywhere.com`
4. Update `ALLOWED_HOSTS` in settings.py
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

## Support

- PythonAnywhere Help: https://help.pythonanywhere.com/
- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/
- Django Documentation: https://docs.djangoproject.com/

## Additional Resources

- [PythonAnywhere Django Tutorial](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
