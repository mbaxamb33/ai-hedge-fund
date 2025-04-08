# Database configuration
DB_USER=hedgefund
DB_PASSWORD=secret123
DB_NAME=investment_saas
DB_PORT=5432
DB_CONTAINER=hedge_fund_db

.PHONY: postgres createdb dropdb migrateup migratedown setup-db init-db reset-db

# Start PostgreSQL container
postgres:
	docker run --name $(DB_CONTAINER) \
		-p $(DB_PORT):5432 \
		-e POSTGRES_USER=$(DB_USER) \
		-e POSTGRES_PASSWORD=$(DB_PASSWORD) \
		-e POSTGRES_DB=$(DB_NAME) \
		-d postgres:15-alpine

# Create the database
createdb:
	docker exec -it $(DB_CONTAINER) createdb --username=$(DB_USER) --owner=$(DB_USER) $(DB_NAME)

# Drop the database
dropdb:
	docker exec -it $(DB_CONTAINER) dropdb --username=$(DB_USER) $(DB_NAME)

# Stop and remove the container
postgres-down:
	docker stop $(DB_CONTAINER) && docker rm $(DB_CONTAINER)

# Run migrations up
migrateup:
	alembic upgrade head

# Run migrations down (revert all)
migratedown:
	alembic downgrade base

# Create a new migration
migration-create:
	alembic revision --autogenerate -m "$(name)"

# Database setup (for first-time setup)
setup-db: postgres
	@echo "Waiting for PostgreSQL to start..."
	@sleep 5
	python -m src.database.init_db --create

# Initialize database tables and data
init-db:
	python -m src.database.init_db

# Reset database (for development)
reset-db: postgres-down postgres
	@echo "Waiting for PostgreSQL to start..."
	@sleep 5
	python -m src.database.init_db --create

# Generate .env file
env-setup:
	@echo "DB_USER=$(DB_USER)" > .env
	@echo "DB_PASSWORD=$(DB_PASSWORD)" >> .env
	@echo "DB_HOST=localhost" >> .env
	@echo "DB_PORT=$(DB_PORT)" >> .env
	@echo "DB_NAME=$(DB_NAME)" >> .env
	@echo "SECRET_KEY=supersecretkey123456789abcdefghijklmnopqrstuvwxyz" >> .env
	@echo "FINANCIAL_DATASETS_API_KEY=your_api_key_here" >> .env
	@echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
	@echo "ANTHROPIC_API_KEY=your_anthropic_api_key_here" >> .env
	@echo "GROQ_API_KEY=your_groq_api_key_here" >> .env
	@echo "DEEPSEEK_API_KEY=your_deepseek_api_key_here" >> .env
	@echo "GOOGLE_API_KEY=your_google_api_key_here" >> .env
	@echo "API_PORT=8000" >> .env
	@echo "DEBUG=true" >> .env
	@echo "ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000" >> .env
	@echo "CACHE_EXPIRY_DAYS=30" >> .env
	@echo ".env file created successfully"

# Create docker-compose file
docker-compose-setup:
	@echo "version: '3.8'" > docker-compose.yml
	@echo "" >> docker-compose.yml
	@echo "services:" >> docker-compose.yml
	@echo "  db:" >> docker-compose.yml
	@echo "    image: postgres:15-alpine" >> docker-compose.yml
	@echo "    container_name: $(DB_CONTAINER)" >> docker-compose.yml
	@echo "    ports:" >> docker-compose.yml
	@echo "      - \"$(DB_PORT):5432\"" >> docker-compose.yml
	@echo "    environment:" >> docker-compose.yml
	@echo "      - POSTGRES_USER=$(DB_USER)" >> docker-compose.yml
	@echo "      - POSTGRES_PASSWORD=$(DB_PASSWORD)" >> docker-compose.yml
	@echo "      - POSTGRES_DB=$(DB_NAME)" >> docker-compose.yml
	@echo "    volumes:" >> docker-compose.yml
	@echo "      - postgres_data:/var/lib/postgresql/data" >> docker-compose.yml
	@echo "    restart: always" >> docker-compose.yml
	@echo "" >> docker-compose.yml
	@echo "  api:" >> docker-compose.yml
	@echo "    build: ." >> docker-compose.yml
	@echo "    container_name: hedge_fund_api" >> docker-compose.yml
	@echo "    ports:" >> docker-compose.yml
	@echo "      - \"8000:8000\"" >> docker-compose.yml
	@echo "    environment:" >> docker-compose.yml
	@echo "      - DB_HOST=db" >> docker-compose.yml
	@echo "      - DB_USER=$(DB_USER)" >> docker-compose.yml
	@echo "      - DB_PASSWORD=$(DB_PASSWORD)" >> docker-compose.yml
	@echo "      - DB_NAME=$(DB_NAME)" >> docker-compose.yml
	@echo "      - DB_PORT=5432" >> docker-compose.yml
	@echo "    depends_on:" >> docker-compose.yml
	@echo "      - db" >> docker-compose.yml
	@echo "    restart: always" >> docker-compose.yml
	@echo "" >> docker-compose.yml
	@echo "volumes:" >> docker-compose.yml
	@echo "  postgres_data:" >> docker-compose.yml
	@echo "docker-compose.yml file created successfully"

# Create a Dockerfile
dockerfile-setup:
	@echo "FROM python:3.11-slim" > Dockerfile
	@echo "" >> Dockerfile
	@echo "WORKDIR /app" >> Dockerfile
	@echo "" >> Dockerfile
	@echo "# Install system dependencies" >> Dockerfile
	@echo "RUN apt-get update && \\" >> Dockerfile
	@echo "    apt-get install -y --no-install-recommends \\" >> Dockerfile
	@echo "    build-essential \\" >> Dockerfile
	@echo "    libpq-dev \\" >> Dockerfile
	@echo "    && apt-get clean \\" >> Dockerfile
	@echo "    && rm -rf /var/lib/apt/lists/*" >> Dockerfile
	@echo "" >> Dockerfile
	@echo "# Copy requirements first to leverage Docker caching" >> Dockerfile
	@echo "COPY requirements.txt ." >> Dockerfile
	@echo "RUN pip install --no-cache-dir -r requirements.txt" >> Dockerfile
	@echo "" >> Dockerfile
	@echo "# Copy the rest of the application" >> Dockerfile
	@echo "COPY . ." >> Dockerfile
	@echo "" >> Dockerfile
	@echo "# Expose the port" >> Dockerfile
	@echo "EXPOSE 8000" >> Dockerfile
	@echo "" >> Dockerfile
	@echo "# Run the application" >> Dockerfile
	@echo "CMD [\"uvicorn\", \"src.main_api:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]" >> Dockerfile
	@echo "Dockerfile created successfully"

# Setup requirements.txt
requirements-setup:
	@echo "# Database" > requirements.txt
	@echo "sqlalchemy>=2.0.0" >> requirements.txt
	@echo "alembic>=1.7.0" >> requirements.txt
	@echo "psycopg2-binary>=2.9.0" >> requirements.txt
	@echo "" >> requirements.txt
	@echo "# API" >> requirements.txt
	@echo "fastapi>=0.95.0" >> requirements.txt
	@echo "uvicorn>=0.21.0" >> requirements.txt
	@echo "pydantic>=2.0.0" >> requirements.txt
	@echo "" >> requirements.txt
	@echo "# Authentication" >> requirements.txt
	@echo "python-jose[cryptography]>=3.3.0" >> requirements.txt
	@echo "passlib[bcrypt]>=1.7.4" >> requirements.txt
	@echo "python-multipart>=0.0.5" >> requirements.txt
	@echo "" >> requirements.txt
	@echo "# Utilities" >> requirements.txt
	@echo "python-dotenv>=0.21.0" >> requirements.txt
	@echo "pandas>=2.0.0" >> requirements.txt
	@echo "numpy>=1.24.0" >> requirements.txt
	@echo "requests>=2.28.0" >> requirements.txt
	@echo "" >> requirements.txt
	@echo "# LLM Dependencies" >> requirements.txt
	@echo "langchain>=0.0.300" >> requirements.txt
	@echo "langchain-openai>=0.0.2" >> requirements.txt
	@echo "langchain-anthropic>=0.0.1" >> requirements.txt
	@echo "langchain-google-genai>=0.0.3" >> requirements.txt
	@echo "langchain-groq>=0.0.1" >> requirements.txt
	@echo "langchain-deepseek>=0.0.1" >> requirements.txt
	@echo "langgraph>=0.0.20" >> requirements.txt
	@echo "requirements.txt file created successfully"

# Complete setup (all the needed files)
complete-setup: env-setup docker-compose-setup dockerfile-setup requirements-setup
	@echo "Configuration files created successfully. Next steps:"
	@echo "1. Review and modify any configuration files as needed"
	@echo "2. Run 'make setup-db' to start the database and initialize it"
	@echo "3. Run 'make migrateup' to apply database migrations"

# Start API server
start-api:
	uvicorn src.main_api:app --reload --host 0.0.0.0 --port 8000

# Start everything with docker-compose
start-docker:
	docker-compose up -d

# Stop everything with docker-compose
stop-docker:
	docker-compose down