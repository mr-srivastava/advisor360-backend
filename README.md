# Advisor360 Backend

A modern FastAPI-based backend application for financial advisory platforms, designed to track commissions and manage partner relationships with comprehensive analytics and reporting capabilities.

## 🚀 Features

- **Commission Tracking**: Comprehensive commission management with financial year support
- **Partner Management**: Entity and partner relationship management
- **Dashboard Analytics**: Real-time metrics, growth tracking, and performance insights
- **Financial Year Support**: Indian financial year format (April-March) with automatic parsing
- **Clean Architecture**: Layered architecture with dependency injection and separation of concerns
- **Type-Safe API**: Full Pydantic validation and automatic OpenAPI documentation
- **Error Handling**: Structured error responses with comprehensive exception hierarchy
- **Database Integration**: Supabase PostgreSQL with repository pattern abstraction
- **Monitoring**: Built-in logging, metrics, and health checks
- **Middleware**: Request logging, error handling, and performance monitoring

## 🏗️ Architecture

The application follows **Clean Architecture** principles with clear separation of concerns. For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

### High-Level Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                     │
│                   Controllers & DTOs                       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                            │
│                  Business Logic                            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Domain Layer                              │
│              Entities & Value Objects                      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Repository Layer                            │
│                  Data Access                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

- **Dependency Injection**: Centralized container for service management
- **Repository Pattern**: Abstracted data access with interface-based design
- **Domain-Driven Design**: Rich domain entities and value objects
- **Service Layer**: Centralized business logic and orchestration
- **Exception Hierarchy**: Structured error handling with domain-specific exceptions

## 📋 Prerequisites

- **Python**: 3.9+ (recommended: 3.13)
- **Supabase Account**: For database and authentication
- **Environment Variables**: Supabase URL and API key

## 🛠️ Local Development Setup

### Prerequisites

- **Python 3.9+** (recommended: Python 3.13)
- **Pipenv** or **pip** with virtual environment
- **Supabase Account** for database
- **Git** for version control

### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd advisor360-backend

# 2. Install dependencies using Pipenv (recommended)
pipenv install
pipenv shell

# Alternative: Using pip and venv
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# 4. Start the development server
make dev
# Or manually: uvicorn app.main:app --reload
```

### Environment Configuration

Create a `.env` file in the root directory:

```bash
# Database Configuration (Required)
DATABASE_URL=https://your-project.supabase.co
DATABASE_KEY=your_supabase_anon_key

# Application Settings (Optional)
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=true
SECRET_KEY=your-secret-key-for-development

# CORS Settings (Optional)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Using Make Commands

The project includes a Makefile for common development tasks:

```bash
# Install dependencies
make install          # Production dependencies
make install-dev      # Development dependencies

# Development
make dev              # Start development server with hot reload
make start            # Start production server

# Code Quality
make format           # Format code with black and isort
make lint             # Run linting with ruff and mypy
make test             # Run tests with pytest
make check            # Run all quality checks

# Maintenance
make clean            # Clean cache files
make setup            # Complete development setup
make help             # Show all available commands
```

### 4. Database Setup

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Set up the following tables in your Supabase database:

```sql
-- Entity Types Table
CREATE TABLE entity_types (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Entities Table
CREATE TABLE entities (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type_id UUID REFERENCES entity_types(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Entity Transactions Table
CREATE TABLE entity_transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id UUID REFERENCES entities(id),
    month DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

3. Create the required RPC functions in Supabase (see Database Functions section below)

## 🚀 Running the Application

### Development Server

```bash
# Recommended: Using Make
make dev

# Alternative methods:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fastapi dev app/main.py
pipenv run uvicorn app.main:app --reload
```

### Available URLs

Once running, the application provides:

- **API Base**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Metrics**: http://localhost:8000/metrics

### Production Server

```bash
make start
# Or: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Development Workflow

```bash
# 1. Start development server
make dev

# 2. Make code changes (server auto-reloads)

# 3. Run quality checks
make check

# 4. Run tests
make test

# 5. Format code before committing
make format
```

## 📊 API Endpoints

### Dashboard

- `GET /dashboard/overview` - Get dashboard overview statistics
- `GET /dashboard/available-financial-years` - List available financial years
- `GET /dashboard/key-metrics/{financial_year}` - Get key metrics for a financial year
- `GET /dashboard/performance-metrics/{financial_year}` - Get performance metrics
- `GET /dashboard/recent-activities` - Get recent activities

### Partners

- `GET /partners/` - List all partners (with pagination and filtering)
- `GET /partners/types` - List entity types
- `GET /partners/{partner_id}` - Get specific partner

### Commissions

- `GET /commissions/` - List all commissions (with pagination and filtering)
- `GET /commissions/{commission_id}` - Get specific commission

### Health Check

- `GET /health` - Health check endpoint

## 🗄️ Database Functions

Create these RPC functions in your Supabase database:

```sql
-- Get total commissions
CREATE OR REPLACE FUNCTION get_total_commissions()
RETURNS DECIMAL AS $$
BEGIN
    RETURN COALESCE(SUM(amount), 0) FROM entity_transactions;
END;
$$ LANGUAGE plpgsql;

-- Get total commissions by month
CREATE OR REPLACE FUNCTION get_total_commissions_by_month(y INTEGER, m INTEGER)
RETURNS DECIMAL AS $$
BEGIN
    RETURN COALESCE(
        SUM(amount), 0
    ) FROM entity_transactions
    WHERE EXTRACT(YEAR FROM month) = y
    AND EXTRACT(MONTH FROM month) = m;
END;
$$ LANGUAGE plpgsql;

-- Get total commissions by financial year
CREATE OR REPLACE FUNCTION get_total_commissions_by_fy(fy TEXT)
RETURNS DECIMAL AS $$
DECLARE
    start_year INTEGER;
    end_year INTEGER;
BEGIN
    start_year := 2000 + CAST(SUBSTRING(fy FROM 3 FOR 2) AS INTEGER);
    end_year := start_year + 1;

    RETURN COALESCE(
        SUM(amount), 0
    ) FROM entity_transactions
    WHERE (EXTRACT(YEAR FROM month) = start_year AND EXTRACT(MONTH FROM month) >= 4)
       OR (EXTRACT(YEAR FROM month) = end_year AND EXTRACT(MONTH FROM month) <= 3);
END;
$$ LANGUAGE plpgsql;

-- Get available financial years
CREATE OR REPLACE FUNCTION get_financial_years()
RETURNS TABLE(financial_year TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        CASE
            WHEN EXTRACT(MONTH FROM month) >= 4 THEN
                'FY' || LPAD(EXTRACT(YEAR FROM month)::TEXT, 2, '0') || '-' ||
                LPAD((EXTRACT(YEAR FROM month) + 1)::TEXT, 2, '0')
            ELSE
                'FY' || LPAD((EXTRACT(YEAR FROM month) - 1)::TEXT, 2, '0') || '-' ||
                LPAD(EXTRACT(YEAR FROM month)::TEXT, 2, '0')
        END as financial_year
    FROM entity_transactions
    ORDER BY financial_year DESC;
END;
$$ LANGUAGE plpgsql;

-- Get monthly growth data
CREATE OR REPLACE FUNCTION get_monthly_growth_data(fy TEXT)
RETURNS TABLE(month TEXT, total DECIMAL, growth DECIMAL) AS $$
BEGIN
    RETURN QUERY
    WITH monthly_data AS (
        SELECT
            TO_CHAR(month, 'Month') as month_name,
            SUM(amount) as monthly_total
        FROM entity_transactions
        WHERE (EXTRACT(YEAR FROM month) = 2000 + CAST(SUBSTRING(fy FROM 3 FOR 2) AS INTEGER)
               AND EXTRACT(MONTH FROM month) >= 4)
           OR (EXTRACT(YEAR FROM month) = 2000 + CAST(SUBSTRING(fy FROM 3 FOR 2) AS INTEGER) + 1
               AND EXTRACT(MONTH FROM month) <= 3)
        GROUP BY EXTRACT(MONTH FROM month), TO_CHAR(month, 'Month')
        ORDER BY EXTRACT(MONTH FROM month)
    )
    SELECT
        TRIM(month_name) as month,
        monthly_total as total,
        CASE
            WHEN LAG(monthly_total) OVER (ORDER BY EXTRACT(MONTH FROM month)) > 0 THEN
                ((monthly_total - LAG(monthly_total) OVER (ORDER BY EXTRACT(MONTH FROM month))) /
                 LAG(monthly_total) OVER (ORDER BY EXTRACT(MONTH FROM month))) * 100
            ELSE 0
        END as growth
    FROM monthly_data;
END;
$$ LANGUAGE plpgsql;

-- Get entity breakdown
CREATE OR REPLACE FUNCTION get_entity_breakdown(fy TEXT)
RETURNS TABLE(entity_id UUID, entity_name TEXT, total DECIMAL, percentage DECIMAL) AS $$
DECLARE
    start_year INTEGER;
    end_year INTEGER;
    total_amount DECIMAL;
BEGIN
    start_year := 2000 + CAST(SUBSTRING(fy FROM 3 FOR 2) AS INTEGER);
    end_year := start_year + 1;

    SELECT SUM(amount) INTO total_amount
    FROM entity_transactions
    WHERE (EXTRACT(YEAR FROM month) = start_year AND EXTRACT(MONTH FROM month) >= 4)
       OR (EXTRACT(YEAR FROM month) = end_year AND EXTRACT(MONTH FROM month) <= 3);

    RETURN QUERY
    SELECT
        e.id as entity_id,
        e.name as entity_name,
        COALESCE(SUM(et.amount), 0) as total,
        CASE
            WHEN total_amount > 0 THEN (COALESCE(SUM(et.amount), 0) / total_amount) * 100
            ELSE 0
        END as percentage
    FROM entities e
    LEFT JOIN entity_transactions et ON e.id = et.entity_id
    WHERE (EXTRACT(YEAR FROM et.month) = start_year AND EXTRACT(MONTH FROM et.month) >= 4)
       OR (EXTRACT(YEAR FROM et.month) = end_year AND EXTRACT(MONTH FROM et.month) <= 3)
       OR et.month IS NULL
    GROUP BY e.id, e.name
    ORDER BY total DESC;
END;
$$ LANGUAGE plpgsql;
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_dashboard.py

# Run tests in watch mode (with pytest-watch)
ptw

# Run tests with verbose output
pytest -v
```

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_services/      # Service layer tests
│   ├── test_repositories/  # Repository tests
│   └── test_domain/        # Domain entity tests
├── integration/            # Integration tests
│   ├── test_api/          # API endpoint tests
│   └── test_database/     # Database integration tests
└── fixtures/              # Test fixtures and data
```

## 📝 API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔧 Configuration

### Environment Variables

| Variable       | Description                    | Required | Default       |
| -------------- | ------------------------------ | -------- | ------------- |
| `DATABASE_URL` | Supabase project URL           | Yes      | -             |
| `DATABASE_KEY` | Supabase anon key              | Yes      | -             |
| `ENVIRONMENT`  | Environment (dev/staging/prod) | No       | `development` |
| `DEBUG`        | Enable debug mode              | No       | `false`       |

| `LOG_LEVEL`

### CORS Configuration

The application is configured to allow requests from:
| Logging level | No | `INFO` |
| `SECRET_KEY` | Secret key for security | No | `dev-secret` |
| `CORS_ORIGINS` | Allowed CORS origins | No | `localhost` |
| `DATABASE_TIMEOUT`| Database connection timeout | No | `30` |

### Configuration Management

The application uses Pydantic Settings for configuration management with automatic validation:

```python
# app/core/config/app_config.py
from app.core.config.app_config import get_config

config = get_config()
print(f"Environment: {config.environment}")
print(f"Database URL: {config.database_url}")
```

- `https://advisor360.vercel.app` (production)
- `http://localhost:3000` (local development)
- `http://127.0.0.1:3000` (local development)

## 🚀 Deployment

### Using Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Railway

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

### Using Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Set environment variables in Vercel dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the error logs for debugging

## 🔄 Recent Updates

### Architecture Refactor (Latest)

- ✅ **Clean Architecture Implementation**: Complete refactor to layered architecture
- ✅ **Dependency Injection**: Centralized DI container with interface-based design
- ✅ **Repository Pattern**: Abstracted data access with Supabase implementation
- ✅ **Service Layer**: Centralized business logic and orchestration
- ✅ **Domain-Driven Design**: Rich domain entities and value objects
- ✅ **Exception Hierarchy**: Structured error handling with domain-specific exceptions
- ✅ **Middleware Stack**: Request logging, error handling, and metrics collection
- ✅ **Configuration Management**: Environment-based configuration with validation

### Previous Updates

- ✅ Enhanced Pydantic models with comprehensive validation
- ✅ Added structured error handling and custom exceptions
- ✅ Implemented request/response models for all endpoints
- ✅ Added pagination and filtering capabilities
- ✅ Enhanced API documentation with detailed descriptions
- ✅ Improved type safety throughout the application
- ✅ Added health check endpoint
- ✅ Comprehensive input validation and error responses

## 🔧 Extending Functionality

### Adding New Features

The application follows Clean Architecture principles. To add new functionality:

1. **Create Domain Entity** (if needed)

   ```python
   # app/domain/new_entity.py
   @dataclass
   class NewEntity:
       id: str
       name: str
       # Add domain logic methods
   ```

2. **Create Repository Interface**

   ```python
   # app/repositories/interfaces/new_repository.py
   class INewRepository(ABC):
       @abstractmethod
       async def get_by_id(self, id: str) -> Optional[NewEntity]:
           pass
   ```

3. **Implement Repository**

   ```python
   # app/repositories/supabase/new_repository.py
   class SupabaseNewRepository(INewRepository):
       # Implementation
   ```

4. **Create Service**

   ```python
   # app/services/new_service.py
   class NewService(INewService):
       def __init__(self, repo: INewRepository):
           self.repo = repo
   ```

5. **Register in DI Container**

   ```python
   # app/core/bootstrap.py
   container.register(INewRepository, SupabaseNewRepository)
   container.register(INewService, NewService)
   ```

6. **Create API Endpoints**
   ```python
   # app/api/new_endpoints.py
   @router.get("/new-resource")
   async def get_resource(service: NewServiceDep):
       return await service.get_all()
   ```

For detailed guidance, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 📚 Documentation

- **[Architecture Guide](ARCHITECTURE.md)**: Detailed architecture documentation and extension guide
- **[API Documentation](http://localhost:8000/docs)**: Interactive Swagger UI (when server is running)
- **[ReDoc](http://localhost:8000/redoc)**: Alternative API documentation
- **[Development Guide](DEVELOPMENT.md)**: Development workflow and best practices (if available)

---

**Built with ❤️ using FastAPI, Pydantic, and Supabase**
