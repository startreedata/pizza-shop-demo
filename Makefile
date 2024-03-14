all: build run

build:
	docker compose build --no-cache
	
run:
	docker compose up -d

	@echo "Waiting for Pinot Controller to be ready..."
	@while true; do \
		STATUS_CODE=$$(curl -s -o /dev/null -w '%{http_code}' \
			'http://localhost:9000/health'); \
		if [ "$$STATUS_CODE" -eq 200 ]; then \
			break; \
		fi; \
		sleep 2; \
		echo "Waiting for Pinot Controller..."; \
	done
	@echo "🍷 Pinot Controller is ready."

	@echo "Waiting for Pinot Broker to be ready..."
	@while true; do \
		STATUS_CODE=$$(curl -s -o /dev/null -w '%{http_code}' \
			'http://localhost:8099/health'); \
		if [ "$$STATUS_CODE" -eq 200 ]; then \
			break; \
		fi; \
		sleep 1; \
		echo "Waiting for Pinot Broker..."; \
	done
	@echo "🍷 Pinot Broker is ready to receive queries."
	
	@echo "🪲 Waiting for Kafka to be ready..."
	@while ! nc -z localhost 9092; do \
		sleep 1; \
		echo "Waiting for Kafka..."; \
	done
	@echo "🪲 Kafka is ready."
    	
	@printf "Pinot Query UI - \033[4mhttp://localhost:9000\033[0m\n"
	@printf "Streamlit Dashboard - \033[4mhttp://localhost:8502\033[0m"
	
stop:
	docker compose down -v