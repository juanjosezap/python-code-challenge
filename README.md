# python-code-challenge
Scraping and Ingest (Advanced)

# Overview
Overview
This script is designed to scrape news articles from the Yogonet website using Selenium WebDriver. It extracts relevant information from each article, including title, kicker, link, and image source, and stores it in a list of dictionaries. The script also includes functions for post-processing the scraped data, including counting words starting with capital letters and extracting entities using spaCy.


Container Setup
====================

Our project uses Docker containers to manage dependencies and ensure consistency across different environments. Here's an overview of how the containers are set up:

docker-compose.yml
```yml
version: "3.8"

services:
  selenium:
    image: selenium/standalone-chrome
    container_name: selenium
    ports:
      - "4444:4444"
    shm_size: "4g"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4444/wd/hub/status"]
      interval: 5s
      retries: 10
      start_period: 10s
    environment:
      - SE_NODE_SESSION_TIMEOUT=600  # Increase session timeout to 10 minutes
      - SE_SESSION_REQUEST_TIMEOUT=600
      - SE_SESSION_RETRY_INTERVAL=2

  scraper:
    build: .
    container_name: selenium_scraper
    depends_on:
      selenium:
        condition: service_healthy
    environment:
      - SELENIUM_URL=http://selenium:4444/wd/hub
```

# Build the Containers
To build the containers, run the following command.

```bash
docker-compose build
```
# Running the Containers
To run the containers, simply execute the following command:

```bash
docker-compose up
```

This will start both containers and allow you to access the Selenium server at http://localhost:4444/wd/hub. The Python application will also start scraping data from Yogonet using the Selenium server.