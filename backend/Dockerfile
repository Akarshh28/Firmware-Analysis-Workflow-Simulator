FROM ubuntu:24.04

# Avoid tzdata interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install system dependencies
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    binutils \
    tshark \
    qemu-user-static \
    default-jre \
    wget \
    curl \
    git \
    build-essential \
    libffi-dev \
    libssl-dev \
    radare2 \
    wkhtmltopdf \
    xvfb \
    fontconfig \
    xfonts-75dpi \
    xfonts-base \
    trufflehog \
    afl++ \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Binwalk (from source or apt, here apt has a basic version but pip is better)
# Note: standard apt binwalk works for extraction in most cases.
RUN apt-get update && apt-get install -y binwalk && rm -rf /var/lib/apt/lists/*

# Install Ghidra
RUN wget -q https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.0.3_build/ghidra_11.0.3_PUBLIC_20240410.zip -O ghidra.zip \
    && apt-get update && apt-get install -y unzip \
    && unzip ghidra.zip -d /opt/ \
    && rm ghidra.zip \
    && ln -s /opt/ghidra_11.0.3_PUBLIC/support/analyzeHeadless /usr/local/bin/analyzeHeadless

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
