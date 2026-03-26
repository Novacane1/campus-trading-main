# Campus Trading System Backend

Built with Flask, PostgreSQL, and Redis.

## Technology Stack
- **Web Framework**: Flask (RESTful API)
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Cache**: Redis (Session & Ranking)

## Prerequisites
- Python 3.8+
- PostgreSQL
- Redis

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Initialization**:
   Ensure PostgreSQL is running and create a database named `campus_trading`.
   Make sure you are in the `backend` directory and your virtual environment is activated.
   Then run:
   ```bash
   export FLASK_APP=run.py
   flask init-db
   ```

3. **Run the Application**:
   ```bash
   python run.py
   ```
   The backend will start at `http://localhost:5001`.

## API Documentation
- `POST /api/auth/register`: User registration
- `POST /api/auth/login`: User login
- `GET /api/items`: List all items (with filters)
- `POST /api/items/publish`: Publish a new item
- `GET /api/items/<id>`: Get item details
- `POST /api/orders`: Create a new order
- `GET /api/stats/overview`: Get system statistics
