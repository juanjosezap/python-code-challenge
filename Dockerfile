FROM python:3.10-slim

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the script into the container
WORKDIR /app
COPY yogonet_scraper.py /app/yogonet_scraper.py

RUN python -m spacy download en_core_web_sm
# Command to run the scraper
CMD ["python", "yogonet_scraper.py"]
