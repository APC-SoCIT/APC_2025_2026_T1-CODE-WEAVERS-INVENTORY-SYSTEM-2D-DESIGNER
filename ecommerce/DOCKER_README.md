# Docker Setup for E-commerce Application

This guide explains how to run the Django e-commerce application using Docker and Docker Compose.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Clone the repository and navigate to the project directory:**
   ```bash
   cd ecommerce
   ```

2. **Build and run the application:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Open your browser and go to `http://localhost:8000`

### Option 2: Using Docker only (SQLite)

1. **Build the Docker image:**
   ```bash
   docker build -t ecommerce-app .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 ecommerce-app
   ```

## Configuration Options

### Environment Variables

Create a `.env` file in the project root or use the provided `.env.docker` file:

```bash
cp .env.docker .env
```

Key environment variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `POSTGRES_DB`: PostgreSQL database name
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password

### Database Options

#### Option 1: PostgreSQL (Default in docker-compose.yml)
The docker-compose.yml includes a PostgreSQL service. Data is persisted in a Docker volume.

#### Option 2: SQLite (Simpler setup)
To use SQLite instead of PostgreSQL:

1. Edit `docker-compose.yml` and remove the `db` service
2. Remove `depends_on: - db` from the web service
3. Update the `DATABASES` setting in your Django settings

## Docker Services

### Web Service (Django Application)
- **Port:** 8000
- **Volumes:** 
  - Source code (for development)
  - Static files
  - Media files

### Database Service (PostgreSQL)
- **Port:** 5432
- **Volume:** Persistent PostgreSQL data

## Development vs Production

### Development Setup
```bash
# Use the default docker-compose.yml
docker-compose up --build
```

### Production Setup
1. Set `DEBUG=False` in your environment variables
2. Update `SECRET_KEY` to a secure value
3. Configure proper `ALLOWED_HOSTS`
4. Consider using a reverse proxy (Nginx)

## Useful Commands

### Database Management
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic

# Access Django shell
docker-compose exec web python manage.py shell
```

### Container Management
```bash
# View logs
docker-compose logs web

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build

# Run in background
docker-compose up -d
```

### Database Access
```bash
# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d ecommerce_db
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Change the port in docker-compose.yml
   ports:
     - "8001:8000"  # Use port 8001 instead
   ```

2. **Database connection errors:**
   - Ensure the database service is running
   - Check environment variables
   - Wait for the database to fully initialize

3. **Static files not loading:**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

4. **Permission errors:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

### Logs and Debugging
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f web
```

## File Structure

```
ecommerce/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Multi-service setup
├── .dockerignore           # Files to exclude from build
├── docker-settings.py      # Docker-specific Django settings
├── .env.docker            # Docker environment variables
├── requirements.txt        # Python dependencies
└── DOCKER_README.md       # This file
```

## Security Notes

- Change default passwords in production
- Use environment variables for sensitive data
- Set `DEBUG=False` in production
- Configure proper `ALLOWED_HOSTS`
- Use HTTPS in production with proper SSL certificates

## Performance Tips

- Use Docker volumes for persistent data
- Consider using Redis for caching in production
- Use a reverse proxy (Nginx) for static files in production
- Monitor container resource usage

For more information about the application itself, refer to the main README.md file.