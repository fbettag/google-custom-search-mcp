# Google Custom Search MCP Server

An async Python MCP (Model Context Protocol) server that provides access to Google Custom Search API using service account authentication.

## Features

- **google_search**: Perform Google Custom Search queries with configurable result count
- **Service Account Auth**: Uses Google Service Account authentication (required since API keys are deprecated)
- **Dual Authentication Support**: File path for local dev, base64 for CI/CD
- **Live Integration Tests**: Real tests against Google Custom Search API
- **FastMCP Integration**: Uses the latest FastMCP Python SDK
- **Docker Support**: Alpine Linux-based Docker image for minimal footprint
- **UV Compatibility**: Modern Python packaging with UV

## Quick Start

### Prerequisites

1. **Google Service Account**: Create a service account in [Google Cloud Console](https://console.cloud.google.com/)
2. **Custom Search Engine ID**: Create a Custom Search Engine at [Programmable Search Engine](https://programmablesearchengine.google.com/about/)
3. **Enable Custom Search API**: Enable the API for your Google Cloud project

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd google-custom-search-mcp

# Install with UV
uv sync

# Set environment variables
export GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/your/service-account-key.json
export GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# Run the server
uv run google-custom-search-mcp
```

### For CI/CD (Base64 encoded service account)

```bash
# Encode your service account JSON file to base64
base64 -i your-service-account-key.json -w 0 > service-account-base64.txt

# Use base64 encoded credential
export GOOGLE_SERVICE_ACCOUNT_BASE64=$(cat service-account-base64.txt)
export GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# Run the server
uv run google-custom-search-mcp
```

### Quick Setup with Claude CLI

```bash
# Using file path (local development)
claude mcp add google-custom-search \
  -s user \
  uv run google-custom-search-mcp \
  -e GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/service-account-key.json \
  -e GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# Using base64 (CI/CD)
claude mcp add google-custom-search \
  -s user \
  uv run google-custom-search-mcp \
  -e GOOGLE_SERVICE_ACCOUNT_BASE64=your-base64-encoded-json \
  -e GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
```

## Claude Desktop Setup (Manual)

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "google-custom-search": {
      "command": "uv",
      "args": ["run", "google-custom-search-mcp"],
      "env": {
        "GOOGLE_SERVICE_ACCOUNT_FILE": "/path/to/your/service-account-key.json",
        "GOOGLE_SEARCH_ENGINE_ID": "your-search-engine-id"
      }
    }
  }
}
```

## Setting Up Google Service Account

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Custom Search API

### 2. Create Service Account

1. Navigate to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Fill in name and description
4. Grant appropriate roles (Custom Search API needs CSE role)
5. Click "Create Key" and download JSON key file

### 3. Create Custom Search Engine

1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/about/)
2. Click "Add" to create a new search engine
3. Configure your search preferences
4. Get the Search Engine ID from the control panel

### 4. Set Environment Variables

**Local Development (File Path):**
```bash
export GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/your/service-account-key.json
export GOOGLE_SEARCH_ENGINE_ID=your_actual_search_engine_id_here
```

**CI/CD (Base64 Encoded):**
```bash
# Encode service account JSON to base64
base64 -i your-service-account-key.json -w 0 > service-account-base64.txt

export GOOGLE_SERVICE_ACCOUNT_BASE64=$(cat service-account-base64.txt)
export GOOGLE_SEARCH_ENGINE_ID=your_actual_search_engine_id_here
```

## Available Functions

### Google Search

```python
google_search({
  query: "Your search query",
  num_results?: 10  # Optional, 1-100 (default: 10)
})
```

**Response Format:**
```json
{
  "results": [
    {
      "title": "Result Title",
      "link": "https://example.com",
      "snippet": "Result description...",
      "display_link": "example.com"
    }
  ],
  "total_results": 100,
  "search_time": 0.5
}
```

## Docker Usage

### Build Image

```bash
docker build -t google-custom-search-mcp .
```

### Run Container

```bash
# Using file mount
docker run -it --rm \
  -v /path/to/service-account-key.json:/app/service-account-key.json \
  -e GOOGLE_SERVICE_ACCOUNT_FILE=/app/service-account-key.json \
  -e GOOGLE_SEARCH_ENGINE_ID=your-engine-id \
  google-custom-search-mcp

# Using base64 environment variable
docker run -it --rm \
  -e GOOGLE_SERVICE_ACCOUNT_BASE64=your-base64-encoded-json \
  -e GOOGLE_SEARCH_ENGINE_ID=your-engine-id \
  google-custom-search-mcp
```

## Helm Chart Installation

The Helm chart allows you to deploy the MCP server to Kubernetes easily.

### Install from GitHub Repository

You can install directly from the GitHub repository without needing Artifact Hub:

```bash
# Add the repository
helm repo add google-custom-search-mcp https://raw.githubusercontent.com/fbettag/google-custom-search-mcp/main/charts/

# Install the chart
helm install google-custom-search-mcp google-custom-search-mcp/google-custom-search-mcp \
  --set google.searchEngineId="your-search-engine-id" \
  --set serviceAccount.base64.value="$(base64 -i your-service-account.json -w 0)"
```

### Install from Local Chart

```bash
# Navigate to the chart directory
cd charts/google-custom-search-mcp

# Install with custom values
helm install google-custom-search-mcp . \
  --set google.searchEngineId="your-search-engine-id" \
  --set serviceAccount.base64.value="$(base64 -i your-service-account.json -w 0)"
```

### Using Values File

Create a `values-prod.yaml` file:

```yaml
# values-prod.yaml
replicaCount: 2

google:
  searchEngineId: "your-search-engine-id"

serviceAccount:
  base64:
    enabled: true
    value: "your-base64-encoded-service-account-json"

resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"
```

Install with values file:

```bash
helm install google-custom-search-mcp . -f values-prod.yaml
```

### Upgrade Existing Deployment

```bash
helm upgrade google-custom-search-mcp . \
  --set google.searchEngineId="your-search-engine-id" \
  --set serviceAccount.base64.value="$(base64 -i your-service-account.json -w 0)"
```

### Uninstall

```bash
helm uninstall google-custom-search-mcp
```

### Chart Configuration

The Helm chart supports various configuration options:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Docker image repository | `your-username/google-custom-search-mcp` |
| `image.tag` | Docker image tag | `latest` |
| `google.searchEngineId` | Google Custom Search Engine ID | `""` |
| `serviceAccount.base64.enabled` | Use base64 encoded service account | `true` |
| `serviceAccount.base64.value` | Base64 encoded service account JSON | `""` |
| `serviceAccount.existingFile.enabled` | Use file mount for service account | `false` |
| `serviceAccount.existingFile.path` | Path to service account file | `""` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `3000` |
| `resources.requests` | Resource requests | `memory: 64Mi, cpu: 50m` |
| `resources.limits` | Resource limits | `memory: 128Mi, cpu: 100m` |

## GitHub CI/CD Setup

### Repository Secrets

Add these secrets to your GitHub repository:

1. `GOOGLE_SERVICE_ACCOUNT_BASE64`: Base64 encoded service account JSON file
2. `GOOGLE_SEARCH_ENGINE_ID`: Your Custom Search Engine ID

### Encoding Service Account for GitHub

```bash
# Encode service account JSON to base64 (no line wraps)
base64 -i your-service-account-key.json -w 0

# Copy the output and add as GitHub secret GOOGLE_SERVICE_ACCOUNT_BASE64
```

## Development

### Setup Development Environment

```bash
# Clone and setup
uv sync --dev

# Run live integration tests (requires valid credentials)
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=server --cov-report=html

# Linting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy server.py
```

### Testing

Tests perform **live integration testing** with the actual Google Custom Search API. You must set:

```bash
export GOOGLE_SERVICE_ACCOUNT_BASE64=your-base64-encoded-json
export GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Path to service account JSON file | Either this or base64 |
| `GOOGLE_SERVICE_ACCOUNT_BASE64` | Base64 encoded service account JSON | Either this or file path |
| `GOOGLE_SEARCH_ENGINE_ID` | Custom Search Engine ID | Yes |

## API Limits and Pricing

- Google Custom Search API provides 100 search queries per day for free
- Additional queries require billing setup
- Service accounts have the same quota limits as user accounts
- Refer to [Google Custom Search Pricing](https://developers.google.com/custom-search/v1/overview#pricing)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the [Google Custom Search documentation](https://developers.google.com/custom-search/v1/overview)
2. Review existing GitHub issues
3. Create a new issue with detailed information