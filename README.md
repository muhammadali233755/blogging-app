# Blogging API

A modern API for blog management built with FastAPI.

## Setup

1. Create a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create .env file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:
```bash
uvicorn main:app --reload
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest
```

3. Run linting:
```bash
flake8
black .
mypy .
```

## Security

- Authentication using JWT tokens
- Role-based access control
- Input validation
- Rate limiting
- CORS protection
- Security headers

