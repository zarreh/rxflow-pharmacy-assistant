.PHONY: install run test clean format type-check docs docs-serve docs-build docker-build docker-run docker-run-detached docker-push docker-clean docker-rebuild deploy-local deploy-server

install:
	poetry install

run:
	poetry run streamlit run app.py

test:
	poetry run pytest tests/

format:
	poetry run black rxflow/ tests/ app.py --line-length 88
	poetry run isort rxflow/ tests/ app.py --profile black

type-check:
	poetry run mypy rxflow/ --ignore-missing-imports --show-error-codes

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	pip install -r requirements-docs.txt
	mkdocs serve

docs-serve:
	mkdocs serve --dev-addr 127.0.0.1:8000

docs-build:
	pip install -r requirements-docs.txt
	mkdocs build

# Docker commands
docker-build:
	docker build -t zarreh/rxflow-pharmacy-assistant:2.0.0 .
	docker tag zarreh/rxflow-pharmacy-assistant:2.0.0 zarreh/rxflow-pharmacy-assistant:latest

docker-run:
	docker-compose up

docker-run-detached:
	docker-compose up -d

docker-push:
	docker push zarreh/rxflow-pharmacy-assistant:2.0.0
	docker push zarreh/rxflow-pharmacy-assistant:latest

docker-clean:
	docker-compose down
	docker rmi zarreh/rxflow-pharmacy-assistant:2.0.0 zarreh/rxflow-pharmacy-assistant:latest 2>/dev/null || true
	docker system prune -f

docker-rebuild:
	docker-compose down
	docker build --no-cache -t zarreh/rxflow-pharmacy-assistant:2.0.0 .
	docker tag zarreh/rxflow-pharmacy-assistant:2.0.0 zarreh/rxflow-pharmacy-assistant:latest
	docker-compose up

# Deployment commands
deploy-local:
	@echo "🚀 Deploying from LOCAL side after changes..."
	@echo "📝 Step 1: Building and pushing Docker image..."
	./build-and-push.sh
	@echo "🔄 Step 2: Restarting local container with new image..."
	docker-compose down
	docker-compose up -d
	@echo "✅ Local deployment complete! App running at http://localhost:8080"

deploy-server:
	@echo "🌐 Deploying on SERVER side..."
	@echo "📥 Step 1: Pulling latest code from GitHub..."
	git pull origin main
	@echo "🐳 Step 2: Pulling updated Docker image..."
	docker pull zarreh/rxflow-pharmacy-assistant:latest
	@echo "🔄 Step 3: Restarting container with new image..."
	docker-compose down
	docker-compose up -d
	@echo "🏥 Step 4: Checking deployment status..."
	docker ps | grep rxflow || echo "❌ Container not running!"
	@echo "✅ Server deployment complete!"
