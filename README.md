# Bar Inventory Management System

A mobile-friendly Django application for managing bar beverage inventory across multiple locations. The application uses HTMX for smooth SPA-like interactions and Bootstrap for responsive design.

## Features

- **Multi-location support**: Manage inventory across multiple bar locations
- **Unit conversion**: Track beverages in barrels, trays, or bottles with automatic liter conversion
- **Mobile-optimized**: Responsive design optimized for smartphone use
- **Real-time updates**: HTMX-powered interface for smooth, page-refresh-free updates
- **Quick adjustments**: Fast increment/decrement buttons for rapid stock counting
- **Admin panel**: Full Django admin for managing beverages, locations, and unit types

## Technology Stack

- Django 5.0+
- Bootstrap 5.3
- HTMX 1.9
- SQLite (development) / MySQL 8.0 (production)
- Docker & Docker Compose

## Installation

### Option 1: Docker (Recommended)

#### Development Mode (SQLite)

```bash
# Start the application with SQLite
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create a superuser
docker-compose exec web python manage.py createsuperuser
```

Visit http://localhost:8332 to access the application.

#### Production Mode (MySQL)

```bash
# Edit docker-compose.yml and change DJANGO_ENV to prod:
# environment:
#   - DJANGO_ENV=prod

# Start services (includes MySQL)
docker-compose up -d

# Wait for MySQL to be ready, then run migrations
docker-compose exec web python manage.py migrate

# Create a superuser
docker-compose exec web python manage.py createsuperuser
```

### Option 2: Local Development (Without Docker)

#### 1. Set up virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

#### 3. Run migrations

```bash
cd code
python manage.py makemigrations
python manage.py migrate
```

#### 4. Create a superuser

```bash
python manage.py createsuperuser
```

#### 5. Run the development server

```bash
python manage.py runserver
```

Visit http://localhost:8000 to access the application.

## Initial Setup

### 1. Access the admin panel

Go to http://localhost:8000/admin and log in with your superuser credentials.

### 2. Configure Unit Types

Add unit types with their liter conversions:
- **Barrel**: e.g., 50 liters
- **Tray**: e.g., 12 liters (for a tray of bottles)
- **Bottle**: e.g., 0.5 liters

### 3. Add Locations

Create your bar locations:
- Main Bar
- Pool Area
- VIP Section
- etc.

### 4. Add Beverages

Create beverages with:
- Name (e.g., "Heineken")
- Unit type (Barrel/Tray/Bottle)
- Available locations (select which locations stock this beverage)

## Usage

### Mobile Interface

1. **Select Location**: Choose the location where you're counting stock
2. **View Inventory**: See all beverages available at that location with current stock
3. **Update Stock**:
   - Use **+** and **-** buttons for quick adjustments
   - Tap the **pencil icon** to enter exact quantities
4. **View Totals**: See stock in both units and liters automatically

### Admin Interface

Use the admin panel to:
- Add/edit/delete beverages, locations, and unit types
- View stock reports
- Manage which beverages are available at which locations

## Model Structure

### Location
- Name and description
- Active status

### UnitType
- Unit name (Barrel/Tray/Bottle)
- Liters per unit

### Beverage
- Name and description
- Unit type
- Available locations (many-to-many)

### Stock
- Beverage and location
- Quantity (in units)
- Automatically calculates liters
- Tracks last update time

## Configuration

### Environment Variables

The application uses the following environment variables:

- **DJANGO_ENV**: Set to `prod` for production (MySQL) or `dev` for development (SQLite). Default: `dev`
- **DB_HOST**: MySQL host. Default: `db`
- **DB_NAME**: MySQL database name. Default: `bar_inventory`
- **DB_USER**: MySQL username. Default: `bar_user`
- **DB_PASSWORD**: MySQL password. Default: `bar_password`
- **DB_PORT**: MySQL port. Default: `3306`

### Database Configuration

The application automatically selects the database based on `DJANGO_ENV`:

- **Development (`DJANGO_ENV=dev`)**: Uses SQLite (file-based, no setup required)
- **Production (`DJANGO_ENV=prod`)**: Uses MySQL (requires MySQL service)

To switch between databases, simply change the `DJANGO_ENV` variable in docker-compose.yml.

## Production Deployment

For production deployment:

1. Set `DJANGO_ENV=prod` in docker-compose.yml
2. Set `DEBUG = False` in settings.py
3. Configure `ALLOWED_HOSTS` with your domain
4. Generate a secure `SECRET_KEY`
5. Change default MySQL passwords in docker-compose.yml
6. Configure static file serving
7. Use a production WSGI server (gunicorn, uWSGI)
8. Set up HTTPS with reverse proxy (nginx/Apache)
9. Set up regular database backupsucture

```
bar_inventory/
├── bar_inventory/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventory/              # Main app
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── urls.py            # URL routing
│   └── admin.py           # Admin configuration
├── templates/
│   ├── base.html          # Base template
│   └── inventory/         # App templates
├── manage.py
└── requirements.txt
```

### Customization

- Modify unit types in the admin panel
- Adjust liter conversion factors per unit type
- Customize styling in base.html
- Add additional fields to models as needed

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Generate a secure `SECRET_KEY`
4. Set up a production database (PostgreSQL recommended)
5. Configure static file serving
6. Use a production WSGI server (gunicorn, uWSGI)
7. Set up HTTPS

## License

This project is provided as-is for bar inventory management purposes.

## Support

For issues or questions, refer to the Django documentation at https://docs.djangoproject.com/
