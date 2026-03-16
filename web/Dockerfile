FROM python:3.12-slim-trixie

# Install gosu for the entrypoint trick
RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create the user (we'll change its ID later via the entrypoint)
RUN useradd -m transformo

# Copy your requirements and app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Set the entrypoint
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# This tells Docker: "Run the script first, then start the app"
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "app.py"]