# 🚀 Finance-Hub Setup Guide

Complete setup instructions for local development.

## Prerequisites

### Required Software
- **Node.js** 20+ ([Download](https://nodejs.org/))
- **Python** 3.11+ ([Download](https://www.python.org/))
- **PostgreSQL** 15+ ([Download](https://www.postgresql.org/))
- **Git** ([Download](https://git-scm.com/))

### Optional (Recommended)
- **Docker** & Docker Compose ([Download](https://www.docker.com/))
- **VS Code** with Python and TypeScript extensions

---

## Option 1: Docker Setup (Recommended)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/finance-hub.git
cd finance-hub
```

### 2. Start Services
```bash
# Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Option 2: Manual Setup

### Backend Setup

#### 1. Navigate to Backend Directory
```bash
cd backend
```

#### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: If `ta-lib` installation fails, you may need to install system dependencies:

**macOS (Homebrew)**:
```bash
brew install ta-lib
```

**Ubuntu/Debian**:
```bash
sudo apt-get install libta-lib-dev
```

**Windows**: Download from [TA-Lib releases](https://github.com/mrjbq7/ta-lib#windows)

#### 4. Setup PostgreSQL Database

**Create Database**:
```bash
# Connect to PostgreSQL
psql -U postgres

# In psql shell:
CREATE DATABASE finance_hub;
\q
```

#### 5. Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
# Minimum required:
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/finance_hub
SECRET_KEY=your-secret-key-generate-a-random-one
```

#### 6. Run Database Migrations
```bash
# Create initial migration
alembic revision --autogenerate -m "Initial tables"

# Apply migrations
alembic upgrade head
```

#### 7. Test Data Fetching (Optional)
```bash
# Test stock data fetching
python -m app.services.data_fetcher
```

#### 8. Start Backend Server
```bash
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs to see API documentation.

---

### Frontend Setup

#### 1. Navigate to Frontend Directory
```bash
cd frontend
```

#### 2. Install Dependencies
```bash
npm install
```

If you encounter errors, try:
```bash
npm install --legacy-peer-deps
```

#### 3. Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env.local

# Edit .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 4. Start Development Server
```bash
npm run dev
```

Visit http://localhost:3000 to see the application.

---

## Verification

### Backend Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### Frontend Check
Open browser to http://localhost:3000 - you should see the Finance-Hub landing page.

### Database Check
```bash
# From backend directory with activated venv
python -c "from app.database import engine; print('Database connected!' if engine else 'Failed')"
```

---

## Development Workflow

### Backend Development
```bash
cd backend
source venv/bin/activate  # Activate venv
uvicorn app.main:app --reload  # Start with auto-reload
```

### Frontend Development
```bash
cd frontend
npm run dev  # Start with auto-reload
```

### Database Migrations
```bash
cd backend

# After changing models, create migration
alembic revision --autogenerate -m "Description of changes"

# Review generated migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests (when added)
cd frontend
npm test
```

---

## Common Issues & Solutions

### Issue: Port Already in Use
**Solution**: Change port in command
```bash
# Backend
uvicorn app.main:app --reload --port 8001

# Frontend
npm run dev -- -p 3001
```

### Issue: Database Connection Failed
**Solutions**:
1. Ensure PostgreSQL is running: `pg_ctl status`
2. Check DATABASE_URL in `.env`
3. Verify database exists: `psql -l`

### Issue: TA-Lib Installation Failed
**Solution**: Install system dependencies (see Backend Setup step 3)

### Issue: Module Not Found Errors
**Solutions**:
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (should be 3.11+)

### Issue: Next.js Build Errors
**Solutions**:
1. Delete `.next` folder and `node_modules`
2. Reinstall: `npm install --legacy-peer-deps`
3. Clear cache: `npm cache clean --force`

---

## Next Steps

1. ✅ Setup complete - application running
2. 📊 Test data fetching with sample stocks
3. 🔐 Implement authentication (future)
4. 🤖 Train ML models (future)
5. 📈 Build portfolio dashboard (future)

---

## Getting Help

- **Documentation**: Check README.md for feature overview
- **API Docs**: Visit http://localhost:8000/docs for API reference
- **Issues**: Create an issue on GitHub

---

**Happy Coding! 🚀**
