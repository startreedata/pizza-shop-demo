all: build run

build:
	docker compose build --no-cache
	
run:
	docker compose up -d
	@printf "Pinot Query UI - \033[4mhttp://localhost:9000\033[0m\n"
	@printf "Streamlit Dashboard - \033[4mhttp://localhost:8502\033[0m"
	
stop:
	docker compose down -v