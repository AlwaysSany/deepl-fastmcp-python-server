# DeepL Translation MCP Server

This is a MCP server for the DeepL translation API. It is a simple server that can be used to translate text.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the server:

```bash
uv run mcp run main.py
```

Run the server in **development** mode:

```bash
uv run mcp dev main.py
```

## Running with Docker

### Build the Docker image

```bash
docker build -t deepl-fastmcp-server .
```

### Run the container

```bash
docker run -e DEEPL_AUTH_KEY=your_deepl_api_key -p 8000:8000 deepl-fastmcp-server
```

## Running with Docker Compose

1. Create a `.env` file in the project root with your DeepL API key:

```
DEEPL_AUTH_KEY=your_deepl_api_key
```

2. Start the service:

```bash
docker-compose up --build
```

This will build the image and start the server, mapping port 8000 on your host to the container.

### Use with Cursor

```json
{
  "mcpServers": {
    "deepl-fastmcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/deepl-fastmcp-python-server/.venv",
        "run",
        "--with",
        "mcp",
        "mcp",
        "run",
        "/path/to/deepl-fastmcp-python-server/main.py"
      ]
    }
  }
}
```