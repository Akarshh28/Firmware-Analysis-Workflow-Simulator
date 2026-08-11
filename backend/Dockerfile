FROM ubuntu:24.04

# Avoid tzdata interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install system dependencies
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    binutils \
    wget \
    curl \
    git \
    build-essential \
    libffi-dev \
    libssl-dev \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Binwalk and other extraction tools
RUN apt-get update && apt-get install -y binwalk cabextract unzip file && rm -rf /var/lib/apt/lists/*

# Fail the build immediately (not silently at runtime) if binwalk isn't
# actually usable after install.
RUN which binwalk && binwalk --help > /dev/null

# Verify other required extraction/analysis tools exist
RUN which cabextract && which unzip && which objdump && which strings

# Set up Python virtual environment
RUN python3.12 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set up working directory
WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure entrypoint is executable
RUN chmod +x entrypoint.sh

# Expose FastAPI port
EXPOSE 8000

# Run entrypoint
ENTRYPOINT ["./entrypoint.sh"]
