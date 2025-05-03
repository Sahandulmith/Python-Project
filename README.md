<p align="center">
  <a href="https://cse40.cse.uom.lk/codejam" target="blank"><img src="https://firebasestorage.googleapis.com/v0/b/profile-image-1c78a.appspot.com/o/codejam%2FCodeJameLogo.webp?alt=media&token=507a7f7b-e735-4952-ad04-d0a8f48a8f55" width="350" alt="CodeJam Logo" /></a>
</p>

# Python Project

A Flask-based REST API for bug tracking with authentication and team management.

## Features

- User authentication (register/login)
- JWT-based authentication
- Bug tracking system
- Team-based bug management
- Swagger API documentation
- Comprehensive test suite

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:
```
FLASK_APP=app.py
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///app.db
BACKEND_URL=http://localhost:8000
AUTH_KEY=your-auth-key-here
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Running the Application

Start the development server:
```bash
flask run
```

The API will be available at `http://localhost:5000`

## API Documentation

Swagger documentation is available at `http://localhost:5000/apidocs`

## Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token

### Bugs
- `GET /api/bugs` - Get all bugs
- `GET /api/bugs/<bug_id>` - Get a specific bug
- `POST /api/bugs` - Create a new bug
- `POST /api/bugs/<bug_id>/mark_fixed` - Mark a bug as fixed

## Environment Variables

- `FLASK_APP` - Main application file
- `FLASK_DEBUG` - Debug mode (True/False)
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key
- `DATABASE_URL` - Database connection URL
- `BACKEND_URL` - Backend service URL
- `AUTH_KEY` - Backend authentication key

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
