FROM python:3.10-slim

# Install dependencies
RUN pip install --no-cache-dir selenium webdriver-manager requests

# Copy the script into the container
WORKDIR /app
COPY yogonet_scraper.py /app/yogonet_scraper.py

# Command to run the scraper
CMD ["python", "yogonet_scraper.py"]
