# Advisor360 Backend

A modern FastAPI-based backend application for financial advisory platforms, designed to track commissions and manage partner relationships with comprehensive analytics and reporting capabilities.

## 🚀 Features

- **Commission Tracking**: Comprehensive commission management with financial year support
- **Partner Management**: Entity and partner relationship management
- **Dashboard Analytics**: Real-time metrics, growth tracking, and performance insights
- **Financial Year Support**: Indian financial year format (April-March) with automatic parsing
- **Type-Safe API**: Full Pydantic validation and automatic OpenAPI documentation
- **Error Handling**: Structured error responses with proper HTTP status codes
- **Database Integration**: Supabase PostgreSQL with real-time capabilities

## 🏗️ Architecture

The application follows a clean, layered architecture:

```
app/
├── main.py                 # FastAPI application entry point
├── core/                   # Core configuration and error handling
│   ├── config.py          # Pydantic Settings configuration
│   ├── exceptions.py      # Custom exception classes
│   └── error_handlers.py  # Error handling middleware
├── db/                     # Database layer
│   └── supabase.py        # Supabase client configuration
├── api/                    # API route handlers
│   ├── dashboard.py       # Dashboard endpoints
│   ├── commissions.py     # Commission endpoints
│   └── partners.py        # Partner endpoints
├── services/               # Business logic layer
│   ├── dashboard.py       # Dashboard business logic
│   ├── commissions.py     # Commission business logic
│   └── partners.py        # Partner business logic
├── models/                 # Data models
│   ├── base.py            # Base models and common fields
│   ├── database.py        # Database entity models
│   ├── api/               # API-specific models
│   │   ├── requests.py    # Request validation models
│   │   ├── responses.py   # Response models
│   │   └── common.py      # Common API models
│   └── commissions.py     # Commission-specific models
└── utils/                  # Utility functions
    └── date_utils.py      # Date and financial year utilities
```

## 📋 Prerequisites

- **Python**: 3.9+ (recommended: 3.13)
- **Supabase Account**: For database and authentication
- **Environment Variables**: Supabase URL and API key

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd advisor360-backend
```

### 2. Python Environment Setup

#### Option A: Using Pipenv (Recommended)

```bash
# Install pipenv if you don't have it
pip install pipenv

# Install dependencies
pipenv install

# Activate the virtual environment
pipenv shell
```

#### Option B: Using pip and venv

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Optional Settings
DEBUG=false
LOG_LEVEL=INFO
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

-- Insert sample entity types
INSERT INTO entity_types (name) VALUES
    ('Mutual Funds'),
    ('Life Insurance'),
    ('Health Insurance'),
    ('General Insurance');
```

3. Create the required RPC functions in Supabase (see Database Functions section below)

## 🚀 Running the Application

### Development Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Using FastAPI CLI
fastapi dev app/main.py

# Using pipenv
pipenv run uvicorn app.main:app --reload
```

The API will be available at:

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
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
# Run tests (when test files are added)
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_dashboard.py
```

## 📝 API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔧 Configuration

### Environment Variables

| Variable       | Description          | Required | Default |
| -------------- | -------------------- | -------- | ------- |
| `SUPABASE_URL` | Supabase project URL | Yes      | -       |
| `SUPABASE_KEY` | Supabase anon key    | Yes      | -       |
| `DEBUG`        | Enable debug mode    | No       | `false` |
| `LOG_LEVEL`    | Logging level        | No       | `INFO`  |

### CORS Configuration

The application is configured to allow requests from:

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

- ✅ Enhanced Pydantic models with comprehensive validation
- ✅ Added structured error handling and custom exceptions
- ✅ Implemented request/response models for all endpoints
- ✅ Added pagination and filtering capabilities
- ✅ Enhanced API documentation with detailed descriptions
- ✅ Improved type safety throughout the application
- ✅ Added health check endpoint
- ✅ Comprehensive input validation and error responses

---

**Built with ❤️ using FastAPI, Pydantic, and Supabase**
