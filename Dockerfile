FROM python:3.13-alpine

# Install system dependencies
RUN apk add --no-cache \
    curl \
    build-base \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

# Install UV for fast dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv && \
    chmod +x /usr/local/bin/uv

WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./

# Install Python dependencies with UV
RUN uv sync --frozen --no-dev

# Copy source code
COPY server.py ./

# Create non-root user with specific UID
RUN adduser -D -u 1000 appuser

# Change ownership of the app directory to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV GOOGLE_SEARCH_ENGINE_ID=
ENV GOOGLE_SERVICE_ACCOUNT_FILE=
ENV GOOGLE_SERVICE_ACCOUNT_BASE64=
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:${PATH}"

# Expose MCP server port
EXPOSE 3000

# Run the MCP server in HTTP mode for container deployment
CMD ["python", "server.py", "--transport", "http", "--host", "0.0.0.0", "--port", "3000"]