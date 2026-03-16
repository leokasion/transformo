FROM python:3.12-slim-trixie

# Install gosu and conversion tools (ffmpeg for media, alien for pkgs)
RUN apt-get update && apt-get install -y gosu ffmpeg alien fakeroot && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create internal user
RUN useradd -m transformo

# We do this as root so we can create system directories
RUN mkdir -p /var/lib/rpm && \
    chown -R transformo:transformo /var/lib/rpm && \
    rpm --initdb
    
# Copy dependencies
COPY requirements.txt .

# Copy requirements and logic
RUN pip install --no-cache-dir -r requirements.txt

# Copy script and add permission handler
COPY worker.py .
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# The worker entrypoint will use the same UID/GID logic
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
# This tells entrypoint.sh what to exec as transformo user
CMD ["python", "worker.py"]