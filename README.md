# Jarvis - Multi-Agent AI Assistant Demo

Jarvis is a sample repository demonstrating how to use the `autobots-devtools-shared-lib.dynagent` framework to build multi-agent AI applications. It showcases essential dynagent features including agent handoff, structured output schemas, and batch processing.

## Overview

Jarvis is a lightweight multi-agent system with three specialized agents:

- **Welcome Agent** - Default agent that greets users and routes to business agents
- **Joke Agent** - Tells jokes with structured output (batch-enabled)
- **Weather Agent** - Provides weather information with structured output

## Features

- **Multi-Agent Architecture**: Seamless handoff between specialized agents
- **Structured Outputs**: JSON schemas for type-safe agent responses
- **Batch Processing**: Process multiple requests in parallel (joke_agent)
- **Chainlit UI**: Interactive chat interface with OAuth support
- **Observability**: Langfuse integration for tracing and monitoring

## Architecture

```
┌─────────────────┐
│ Welcome Agent   │ ──┐
│  (Default)      │   │
└─────────────────┘   │
                      │ handoff
┌─────────────────┐   │
│  Joke Agent     │ ◄─┤
│  (Batch-enabled)│   │
└─────────────────┘   │
                      │
┌─────────────────┐   │
│ Weather Agent   │ ◄─┘
└─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.12+
- Google API Key (Gemini)
- Poetry (optional, for dependency management)

### Setup

1. **Clone the repository**

   ```bash
   cd autobots-agent-jarvis
   ```
2. **Install dependencies**

   ```bash
   # Using make (recommended)
   cd ..
   make install-dev  # Installs in parent venv

   # Or using poetry directly
   poetry install
   ```
3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```
4. **Run the application**

   ```bash
   # Using make
   make chainlit-dev

   # Or using the run script
   ./sbin/run_jarvis.sh

   # Or directly
   chainlit run src/autobots_agents_jarvis/servers/jarvis_ui.py --port 1337
   ```
5. **Open in browser**

   Navigate to http://localhost:1337

## Agent Descriptions

### Welcome Agent

The default entry point that:

- Greets users with a friendly message
- Explains available agents
- Routes to appropriate specialized agents

**Tools**: `handoff`, `get_agent_list`

### Joke Agent

Specialized in humor delivery:

- Tells jokes from multiple categories (programming, general, knock-knock, dad-joke)
- Returns structured JSON output
- Supports batch processing

**Tools**: `tell_joke`, `get_joke_categories`, `handoff`, `get_agent_list`

**Output Schema**: `configs/jarvis/schemas/joke-output.json`

**Batch-enabled**: Yes

### Weather Agent

Provides weather information:

- Current weather for supported cities
- Multi-day forecasts
- Structured JSON output with temperature, conditions, and forecasts

**Tools**: `get_weather`, `get_forecast`, `handoff`, `get_agent_list`

**Output Schema**: `configs/jarvis/schemas/weather-output.json`

## Batch Processing

The joke_agent supports batch processing for processing multiple joke requests in parallel:

```python
from autobots_agents_jarvis.services.jarvis_batch import jarvis_batch

prompts = [
    "Tell me a programming joke",
    "What's a funny dad joke?",
    "Give me a knock-knock joke",
]

result = jarvis_batch("joke_agent", prompts)

for record in result.results:
    if record.success:
        print(f"Record {record.index}: {record.output}")
    else:
        print(f"Record {record.index} failed: {record.error}")
```

### Running Batch Smoke Tests

```bash
cd src/autobots_agents_jarvis/services
python jarvis_batch.py
```

## Development

### Running Tests

```bash
# Run all tests with coverage
make test

# Run tests without coverage (faster)
make test-fast

# Run specific test
make test-one TEST=tests/unit/test_joke_service.py::test_get_joke_valid_category
```

### Code Quality

```bash
# Format code
make format

# Run linter
make lint

# Type checking
make type-check

# Run all checks
make all-checks
```

### Pre-commit Hooks

```bash
# Install hooks
make install-hooks

# Run manually
make pre-commit
```

## Configuration

### Agent Configuration

Agents are configured in `configs/jarvis/agents.yaml`:

```yaml
agents:
  joke_agent:
    prompt: "01-joke"
    output_schema: "joke-output.json"
    batch_enabled: true
    approach: "direct"
    tools:
      - "tell_joke"
      - "get_joke_categories"
      - "handoff"
      - "get_agent_list"
```

### Environment Variables

See `.env.example` for all available configuration options:

- `DYNAGENT_CONFIG_ROOT_DIR` - Path to agent configs (default: `configs/jarvis`)
- `GOOGLE_API_KEY` - Required for Gemini LLM
- `LANGFUSE_*` - Optional observability configuration
- `OAUTH_GITHUB_*` - Optional GitHub OAuth for authentication

## Project Structure

```
autobots-agent-jarvis/
├── src/autobots_agents_jarvis/
│   ├── agents/
│   │   └── jarvis_tools.py          # Tool implementations
│   ├── config/
│   │   └── settings.py              # Pydantic settings
│   ├── services/
│   │   ├── joke_service.py          # Joke data service
│   │   ├── weather_service.py       # Weather data service
│   │   └── jarvis_batch.py          # Batch processing
│   ├── utils/
│   │   └── formatting.py            # Output formatters
│   └── jarvis_ui.py                # Chainlit app entry point
├── configs/jarvis/
│   ├── agents.yaml                  # Agent definitions
│   ├── prompts/                     # Agent prompt templates
│   │   ├── 00-welcome.md
│   │   ├── 01-joke.md
│   │   └── 02-weather.md
│   └── schemas/                     # Output JSON schemas
│       ├── joke-output.json
│       └── weather-output.json
├── tests/
│   ├── unit/                        # Unit tests
│   └── integration/                 # Integration tests
├── pyproject.toml                   # Package configuration
└── README.md                        # This file
```

## Extending Jarvis

### Adding a New Agent

1. **Define the agent** in `configs/jarvis/agents.yaml`
2. **Create prompt** in `configs/jarvis/prompts/`
3. **Add output schema** (if needed) in `configs/jarvis/schemas/`
4. **Implement tools** in `src/autobots_agents_jarvis/agents/jarvis_tools.py`
5. **Register tools** in `register_jarvis_tools()`
6. **Add tests** in `tests/`

### Adding a New Tool

```python
from langchain.tools import ToolRuntime, tool
from autobots_devtools_shared_lib.dynagent.models.state import Dynagent

@tool
def my_new_tool(runtime: ToolRuntime[None, Dynagent], param: str) -> str:
    """Tool description for the LLM."""
    session_id = runtime.state.get("session_id", "default")
    # Your implementation here
    return "Result"

# Then register in register_jarvis_tools()
```

## Docker Support

```bash
# Build image
make docker-build

# Run container
make docker-run

# Use docker-compose
make docker-up
```

## Troubleshooting

### Tests failing with import errors

Make sure to install the package in development mode:

```bash
cd ..
make install-dev
```

### Agent not found errors

Check that `DYNAGENT_CONFIG_ROOT_DIR` points to `configs/jarvis`:

```bash
export DYNAGENT_CONFIG_ROOT_DIR=configs/jarvis
```

### Missing Google API key

Set your API key in `.env`:

```
GOOGLE_API_KEY=your-actual-key-here
```

## License

MIT

## Contributing

Jarvis is a demonstration project. For contributions to the dynagent framework itself, please visit the `autobots-devtools-shared-lib` repository.

## Resources

- [Dynagent Framework Documentation](../autobots-devtools-shared-lib/README.md)
- [Chainlit Documentation](https://docs.chainlit.io)
- [Langfuse Observability](https://langfuse.com)
