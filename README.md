# DeepL MCP Server

A Model Context Protocol (MCP) server that provides translation capabilities using the DeepL API using python and fastmcp.


## Working Demo


<video src="https://private-user-images.githubusercontent.com/3911298/452408725-04acb3c8-f37b-43a9-8b6f-249843a052ed.webm?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDkyMzI2NzYsIm5iZiI6MTc0OTIzMjM3NiwicGF0aCI6Ii8zOTExMjk4LzQ1MjQwODcyNS0wNGFjYjNjOC1mMzdiLTQzYTktOGI2Zi0yNDk4NDNhMDUyZWQud2VibT9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA2MDYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNjA2VDE3NTI1NlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWM5NTJiMjhjMWVlODM0ZDVlMzMyNzgzNGE5NmRhZTI0YjQ5OGI5NzUzMWFkZTkxNzU0MDJkNDRmZWMwYTk1Y2ImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.Kp9OyvzESVW_ml5tQhg1U5Fh_rFar78HDv0uXPaVAkU" controls width="100%"></video>

## Features

- Translate text between numerous languages
- Rephrase text using DeepL's capabilities
- Access to all DeepL API languages and features
- Automatic language detection
- Formality control for supported languages
- Batch translation and document translation
- Usage and quota reporting
- Translation history and usage analysis
- **Support for multiple MCP transports**: stdio, SSE, and Streamable HTTP

## Installation

### Standard (Local) Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AlwaysSany/deepl-fastmcp-python-server.git
   cd deepl-fastmcp-python-server
   ```

2. **Install [uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) (recommended) or use pip:**

    With **pip**,
    
    ```bash 
    pip install uv 
    ```

    With **pipx**,
    ```bash
    pipx install uv
    ```

3. **Install dependencies:**

    ```bash
    uv sync
    ```

4. **Set your environment variables:**

    Create a `.env` file or export `DEEPL_AUTH_KEY` in your shell.You can do this by running the following command and then update the `.env` file with your DeepL API key:


    ```bash
    cp .env.example .env
    ```
 
    Example `.env` file,

    ```bash
    DEEPL_AUTH_KEY=your_deepl_api_key
    ```

5. **Run the server:**

    **Normal** mode:

    ```bash
    uv run python main.py --transport stdio
    ```

    To run with **Streamable HTTP** transport (recommended for web deployments):

    ```bash
    uv run python main.py --transport streamable-http --host 127.0.0.1 --port 8000
    ```

    To run with **SSE** transport:

    ```bash
    uv run python main.py --transport sse --host 127.0.0.1 --port 8000
    ```

    **Development** mode:

    ```bash
    uv run mcp dev main.py
    ```

It will show some messages in the terminal like this:

> Spawned stdio transport Connected MCP client to backing server transport

> Created web app transport

> Set up MCP proxy

> 🔍 MCP Inspector is up and running at http://127.0.0.1:6274 

**MCP Inspector**,

![MCP Inspector](assets/mcp-inspector.png)


### Dockerized Installation

1. **Build the Docker image:**
   ```bash
   docker build -t deepl-fastmcp-server .
   ```

2. **Run the container:**
   ```bash
   docker run -e DEEPL_AUTH_KEY=your_deepl_api_key -p 8000:8000 deepl-fastmcp-server
   ```

### Docker Compose

1. **Create a `.env` file in the project root:**
   ```
   DEEPL_AUTH_KEY=your_deepl_api_key
   ```

2. **Start the service:**
   ```bash
   docker compose up --build
   ```
   This will build the image and start the server, mapping port 8000 on your host to the container.

---

## Configuration

### DeepL API Key

You'll need a DeepL API key to use this server. You can get one by signing up at [DeepL API](https://www.deepl.com/pro-api?utm_source=github&utm_medium=github-mcp-server-readme). With a DeepL API Free account you can translate up to 500,000 characters/month for free.

**Required environment variables:**
- `DEEPL_AUTH_KEY` (required): Your DeepL API key.
- `DEEPL_SERVER_URL` (optional): Override the DeepL API endpoint (default: `https://api-free.deepl.com`).

### MCP Transports

This server supports the following MCP transports:
- **Stdio**: Default transport for local usage.
- **SSE (Server-Sent Events)**: Ideal for real-time event-based communication.
- **Streamable HTTP**: Suitable for HTTP-based streaming applications.

To configure these transports, ensure your environment supports the required protocols and dependencies.

---

## Usage


### Use with Cursor IDE,

Click on `File` > `Preferences` > `Cursor Settings` > `MCP` > `MCP Servers` > `Add new global MCP server`

and paste the following json:

```json
{
  "mcpServers": {
    "deepl-fastmcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/yourdeepl-fastmcp-python-server/.venv",
        "run",
        "--with",
        "mcp",
        "python",
        "/path/to/your/deepl-fastmcp-python-server/main.py",
        "--transport",
        "streamable-http",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
      ]
    }
  }
}
```

**Note**: To use Streamable HTTP or SSE transports with Cursor IDE, change the `"--transport", "stdio"` line to `"--transport", "streamable-http", "--host", "127.0.0.1", "--port", "8000"` or `"--transport", "sse", "--host", "127.0.0.1", "--port", "8000"` respectively, and adjust the host and port as needed.

**Cursor Settings**,

![Cursor MCP Server](assets/mcp-cursor-settings.png)


## Use with Claude Desktop

This MCP server integrates with Claude Desktop to provide translation capabilities directly in your conversations with Claude.

### Configuration Steps

1. Install Claude Desktop if you haven't already
2. Create or edit the Claude Desktop configuration file:

   - On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - On Windows: `%AppData%\Claude\claude_desktop_config.json`
   - On Linux: `~/.config/Claude/claude_desktop_config.json`

3. Add the DeepL MCP server configuration:

```json
{
  "mcpServers": {
    "deepl-fastmcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/yourdeepl-fastmcp-python-server/.venv",
        "run",
        "--with",
        "mcp",
        "python",
        "/path/to/your/deepl-fastmcp-python-server/main.py",
        "--transport",
        "streamable-http",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
      ]
    }
  }
}
```

**Note**: To use Streamable HTTP or SSE transports with Claude Desktop, change the `"--transport", "stdio"` line to `"--transport", "streamable-http", "--host", "127.0.0.1", "--port", "8000"` or `"--transport", "sse", "--host", "127.0.0.1", "--port", "8000"` respectively, and adjust the host and port as needed.

---

## Available Tools

This server provides the following tools:

- `translate_text`: Translate text to a target language
- `rephrase_text`: Rephrase text in the same or different language
- `get_source_languages`: Get list of available source languages for translation
- `get_target_languages`: Get list of available target languages for translation
- `get_usage`: Check DeepL API usage and limits
- `batch_translate`: Translate multiple texts in a single request
- `translate_document`: Translate a document file using DeepL API
- `detect_language`: Detect the language of given text
- `get_glossary_languages`: Get supported language pairs for glossaries
- `get_translation_history`: Get recent translation operation history
- `analyze_usage_patterns`: Analyze translation usage patterns from history

### Tool Details

<details>
  <summary>🖼️ Click to see the tool details
  
#### translate_text
Translate text between languages using the DeepL API.
- Parameters:
  - `text`: The text to translate
  - `target_language`: Target language code (e.g., 'EN', 'DE', 'FR', 'ES', 'IT', 'JA', 'ZH')
  - `source_language` (optional): Source language code
  - `formality` (optional): Controls formality level ('less', 'more', 'default', 'prefer_less', 'prefer_more')
  - `preserve_formatting` (optional): Whether to preserve formatting
  - `split_sentences` (optional): How to split sentences
  - `tag_handling` (optional): How to handle tags

#### rephrase_text
Rephrase text in the same or different language using the DeepL API.
- Parameters:
  - `text`: The text to rephrase
  - `target_language`: Language code for rephrasing
  - `formality` (optional): Desired formality level
  - `context` (optional): Additional context for better rephrasing

#### batch_translate
Translate multiple texts in a single request.
- Parameters:
  - `texts`: List of texts to translate
  - `target_language`: Target language code
  - `source_language` (optional): Source language code
  - `formality` (optional): Formality level
  - `preserve_formatting` (optional): Whether to preserve formatting

#### translate_document
Translate a document file using DeepL API.
- Parameters:
  - `file_path`: Path to the document file
  - `target_language`: Target language code
  - `output_path` (optional): Output path for translated document
  - `formality` (optional): Formality level
  - `preserve_formatting` (optional): Whether to preserve document formatting

#### detect_language
Detect the language of given text using DeepL.
- Parameters:
  - `text`: Text to analyze for language detection

#### get_source_languages
- No parameters required. See tool output for details. 
#### get_target_languages
- No parameters required. See tool output for details.
#### get_usage
- No parameters required. See tool output for details.
#### get_glossary_languages
- No parameters required. See tool output for details.
#### get_translation_history
- No parameters required. See tool output for details.
#### analyze_usage_patterns
- No parameters required. See tool output for details.
  
</summary></


## Supported Languages

The DeepL API supports a wide variety of languages for translation. You can use the `get_source_languages` and `get_target_languages` tools to see all currently supported languages.

Some examples of supported languages include:

- English (en, en-US, en-GB)
- German (de)
- Spanish (es)
- French (fr)
- Italian (it)
- Japanese (ja)
- Chinese (zh)
- Portuguese (pt-BR, pt-PT)
- Russian (ru)
- And many more

---

## Debugging

For debugging information, visit the [MCP debugging documentation](https://modelcontextprotocol.io/docs/tools/debugging).

## Error Handling

If you encounter errors with the DeepL API, check the following:

- Verify your API key is correct
- Make sure you're not exceeding your API usage limits
- Confirm the language codes you're using are supported

---

## License

MIT

## TODOs
- [ ] Add more test cases
- [ ] Add more features
- [ ] Add more documentation
- [ ] Add more security features
- [ ] Add more logging
- [ ] Add more monitoring
- [ ] Add more performance optimization

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

See more at [Contributing](https://github.com/AlwaysSany/deepl-fastmcp-python-server/blob/main/CONTRIBUTING.md)

## Contact

- Author: [Sany Ahmed](https://github.com/sany2k8)
- Email: sany2k8@gmail.com

## Links

- [DeepL API Documentation](https://www.deepl.com/docs-api?utm_source=github&utm_medium=github-mcp-server-readme)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/docs/)
