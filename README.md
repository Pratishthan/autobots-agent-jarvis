# Jarvis - Multi-Domain Multi-Agent AI Application

Jarvis is a demonstration repository showcasing how to use the `autobots-devtools-shared-lib.dynagent` framework to build **multi-domain multi-agent AI applications**. It demonstrates production-ready architectural patterns for organizing multiple business domains with shared and domain-specific code.

## Overview

Jarvis demonstrates a **multi-domain architecture** with three independent business domains, each with specialized multi-agent systems:

### 🤖 **Jarvis Domain** (General Assistant)
- **Welcome Agent** - Routes to joke or weather agents
- **Joke Agent** - Humor delivery with structured output (batch-enabled)
- **Weather Agent** - Weather information with forecasts

### 🎧 **Customer Support Domain**
- **Support Coordinator** - Routes to ticket or knowledge base agents
- **Ticket Agent** - Create, update, search support tickets (batch-enabled)
- **Knowledge Agent** - Search knowledge base and retrieve articles

### 💼 **Sales Domain**
- **Sales Coordinator** - Routes to lead qualification or product agents
- **Lead Qualification Agent** - Qualify leads with intelligent scoring (batch-enabled)
- **Product Recommendation Agent** - Product catalog and recommendations

## Key Features

- **Multi-Domain Architecture**: Three independent domains running simultaneously on different ports
- **Domain Isolation**: Clean separation between domain-specific and shared code
- **Code Reusability**: Shared validation tools used across all domains
- **Multi-Agent Systems**: Each domain has specialized agents with handoff capabilities
- **Structured Outputs**: JSON schemas for type-safe agent responses
- **Batch Processing**: Parallel request processing for qualified agents
- **Chainlit UI**: Interactive chat interface per domain
- **Observability**: Langfuse integration for tracing and monitoring

## Architecture

### Multi-Domain Structure

```
autobots-agents-jarvis/
├── agent_configs/          # Agent configurations per domain
│   ├── jarvis/            # Jarvis domain config
│   ├── customer-support/  # Customer support domain config
│   └── sales/             # Sales domain config
│
├── src/autobots_agents_jarvis/
│   ├── common/            # SHARED code across all domains
│   │   ├── tools/         # Shared validation tools
│   │   ├── services/      # Shared service patterns
│   │   └── utils/         # Shared utilities
│   │
│   └── domains/           # DOMAIN-SPECIFIC code
│       ├── jarvis/        # Jarvis implementation
│       ├── customer_support/  # Customer support implementation
│       └── sales/         # Sales implementation
```

### Domain Pattern

Each domain follows the same structure:
```
domains/{name}/
├── server.py      # Chainlit server entry point
├── tools.py       # LangChain @tool wrappers
└── services.py    # Business logic layer
```

### Agent Mesh Architecture

```
🤖 JARVIS (Port 2337)          🎧 CUSTOMER SUPPORT (Port 1338)     💼 SALES (Port 1339)
┌─────────────────┐            ┌─────────────────┐                ┌─────────────────┐
│ Welcome Agent   │            │  Coordinator    │                │  Coordinator    │
│  (Default)      │            │   (Default)     │                │   (Default)     │
└─────────────────┘            └─────────────────┘                └─────────────────┘
        │                              │                                   │
    ┌───┴───┐                     ┌────┴────┐                         ┌────┴────┐
    │       │                     │         │                         │         │
┌───▼─┐  ┌──▼──┐            ┌────▼──┐  ┌──▼───┐                ┌────▼──┐  ┌──▼───┐
│Joke │  │Weather│          │Ticket │  │KB    │                │Lead  │  │Product│
│Agent│  │Agent  │          │Agent  │  │Agent │                │Agent │  │Agent  │
└─────┘  └───────┘          └───────┘  └──────┘                └──────┘  └───────┘
```

## Quick Start

### Prerequisites

- Python 3.12+
- Google API Key (Gemini) or Anthropic API Key (Claude)
- Poetry (optional, for dependency management)

### Setup

1. **Clone the repository**

   ```bash
   cd autobots-agents-jarvis
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
   # Edit .env and add your GOOGLE_API_KEY or ANTHROPIC_API_KEY
   ```

### Running Domains

#### Option 1: Run All Domains Simultaneously (Recommended)

```bash
# Launch all three domains at once
make chainlit-all

# Or use the script directly
./sbin/run_all_domains.sh
```

Then open in browser:
- 🤖 **Jarvis**: http://localhost:2337
- 🎧 **Customer Support**: http://localhost:1338
- 💼 **Sales**: http://localhost:1339

Press `Ctrl+C` to stop all domains.

#### Option 2: Run Individual Domains

```bash
# Run Jarvis only (port 2337)
make chainlit-dev
# OR: ./sbin/run_jarvis.sh

# Run Customer Support only (port 1338)
make chainlit-customer-support
# OR: ./sbin/run_customer_support.sh

# Run Sales only (port 1339)
make chainlit-sales
# OR: ./sbin/run_sales.sh
```

## Domain Descriptions

### 🤖 Jarvis Domain (Port 2337)

**Purpose**: General-purpose AI assistant for jokes and weather

**Agents**:
- **welcome_agent** (default) - Routes users to joke or weather agents
- **joke_agent** (batch-enabled) - Tells categorized jokes with structured output
- **weather_agent** - Provides weather info and forecasts

**Tools**: `tell_joke`, `get_joke_categories`, `get_weather`, `get_forecast`

**Mock Data**: 4 joke categories, 6 cities with weather data

### 🎧 Customer Support Domain (Port 1338)

**Purpose**: Customer service with ticket management and knowledge base

**Agents**:
- **support_coordinator** (default) - Routes to ticket or knowledge agents
- **ticket_agent** (batch-enabled) - Create, update, search tickets
- **knowledge_agent** - Search KB articles and retrieve full content

**Tools**: `create_ticket`, `update_ticket`, `search_tickets`, `search_knowledge_base`, `get_article`, `validate_email` (shared), `validate_phone` (shared), `validate_url` (shared)

**Mock Data**: In-memory tickets (TKT-1001+), 4 KB articles (KB001-KB004)

### 💼 Sales Domain (Port 1339)

**Purpose**: Lead qualification and product recommendations

**Agents**:
- **sales_coordinator** (default) - Routes to lead qualification or product agents
- **lead_qualification_agent** (batch-enabled) - Qualify leads with scoring
- **product_recommendation_agent** - Product catalog and recommendations

**Tools**: `qualify_lead`, `get_lead_score`, `get_product_catalog`, `recommend_products`, `check_inventory`

**Mock Data**: In-memory leads (LEAD-5001+), 6 products across 3 tiers (Enterprise/SMB/Starter)

## Shared vs Domain-Specific Code Pattern

This repository demonstrates how to organize code for multi-domain applications:

### Shared Code (`common/`)

Code available to **all domains**:

```python
# common/tools/validation_tools.py - Used by any domain
@tool
def validate_email(email: str) -> str:
    """Validate email format. Available to all domains."""
    # ...

@tool
def validate_phone(phone: str) -> str:
    """Validate phone number. Available to all domains."""
    # ...
```

**Location**: `src/autobots_agents_jarvis/common/`
- `common/tools/` - Shared validation tools
- `common/services/` - Shared service patterns
- `common/utils/` - Shared formatting utilities

### Domain-Specific Code (`domains/{name}/`)

Code unique to **one domain**:

```python
# domains/customer_support/tools.py - Customer Support only
@tool
def create_ticket(runtime: ToolRuntime[None, Dynagent], title: str, description: str) -> str:
    """Create support ticket. Customer Support domain only."""
    # ...
```

**Pattern**:
- Each domain in `src/autobots_agents_jarvis/domains/{name}/`
- Each has: `server.py`, `tools.py`, `services.py`
- Domains opt-in to shared tools by calling `register_validation_tools()`

### Example: Customer Support Using Both

```python
# domains/customer_support/server.py
from autobots_agents_jarvis.common.tools.validation_tools import register_validation_tools
from autobots_agents_jarvis.domains.customer_support.tools import register_customer_support_tools

# Register both shared and domain-specific tools
register_validation_tools()  # ← SHARED (email, phone, URL validators)
register_customer_support_tools()  # ← DOMAIN-SPECIFIC (tickets, KB)
```

## Batch Processing

Three agents across domains support batch processing for parallel request handling:

### Jarvis Domain - `joke_agent`

```python
from autobots_agents_jarvis.domains.jarvis.jarvis_batch import jarvis_batch

prompts = [
    "Tell me a programming joke",
    "What's a funny dad joke?",
    "Give me a knock-knock joke",
]

result = jarvis_batch("joke_agent", prompts)

for record in result.results:
    if record.success:
        print(f"Record {record.index}: {record.output}")
```

### Customer Support Domain - `ticket_agent`

Batch process ticket operations:
```python
from autobots_devtools_shared_lib.dynagent import batch_invoker

prompts = [
    "Create a ticket for login issue with high priority",
    "Create a ticket for billing question",
]

result = batch_invoker("ticket_agent", prompts)
```

### Sales Domain - `lead_qualification_agent`

Batch qualify multiple leads:
```python
from autobots_devtools_shared_lib.dynagent import batch_invoker

prompts = [
    "Qualify lead: Acme Corp, budget $100K, timeline 2 months, 50 users",
    "Qualify lead: Small Biz Inc, budget $5K, timeline 6 months, 3 users",
]

result = batch_invoker("lead_qualification_agent", prompts)
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
autobots-agents-jarvis/
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
from autobots_devtools_shared_lib.dynagent import Dynagent

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

## Domain Summary

| Domain | Port | Default Agent | Batch Agent | Key Features |
|--------|------|---------------|-------------|--------------|
| 🤖 **Jarvis** | 2337 | welcome_agent | joke_agent | Jokes (4 categories), Weather (6 cities) |
| 🎧 **Customer Support** | 1338 | support_coordinator | ticket_agent | Tickets, Knowledge Base (4 articles), Shared validation tools |
| 💼 **Sales** | 1339 | sales_coordinator | lead_qualification_agent | Lead scoring (hot/warm/cold), Product catalog (6 products, 3 tiers) |

**Quick Access URLs** (when running `make chainlit-all`):
- http://localhost:2337 - Jarvis
- http://localhost:1338 - Customer Support
- http://localhost:1339 - Sales

## License

MIT

## Contributing

Jarvis is a demonstration project showcasing multi-domain multi-agent architecture patterns. For contributions to the dynagent framework itself, please visit the `autobots-devtools-shared-lib` repository.

## Resources

- [Dynagent Framework Documentation](../autobots-devtools-shared-lib/README.md)
- [Chainlit Documentation](https://docs.chainlit.io)
- [Langfuse Observability](https://langfuse.com)
