# Google Ads AI System with ADK Integration

A production-ready backend API system that integrates with Google's Agent Development Kit (ADK) for building sophisticated AI agents. Uses the latest 2025 APIs including Google Gen AI SDK, Google Ads API, Firebase, and FastAPI.

## Quick Start

### Prerequisites

- Python 3.9+
- Google Cloud Project
- Firebase Project  
- Google Ads API Developer Token
- Chrome Browser (for extension)

### Installation

1. **Clone and Setup**
```bash
git clone <your-repo>
cd google-ads-ai-system
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Setup Firebase**
```bash
python scripts/setup_firebase.py
# Follow the instructions to configure Firebase
```

4. **Setup Google Ads API**
```bash
python scripts/setup_google_ads.py
# Follow the instructions to get API credentials
```

5. **Run the Application**
```bash
python main.py
```

Visit `http://localhost:8000/docs` for API documentation.

## System Architecture

```
┌─────────────────────────────────────────────────┐
│                ADK No-Code UI                   │
│  (Client creates agents visually)               │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────┼───────────────────────────────┐
│           Infrastructure Agents                 │
│  ┌─────────────────┐  ┌─────────────────────┐   │
│  │  Google Ads     │  │   Gemini AI         │   │
│  │  Tools          │  │   Tools             │   │
│  └─────────────────┘  └─────────────────────┘   │
└─────────────────┼───────────────────────────────┘
                  │
┌─────────────────┼───────────────────────────────┐
│              FastAPI Backend                    │
│  ┌─────────────────────────────────────────┐   │
│  │  Auth │ Users │ Google Ads │ AI │ Data │   │
│  └─────────────────────────────────────────┘   │
└─────────────────┼───────────────────────────────┘
                  │
┌─────────────────┼───────────────────────────────┐
│          External Services                      │
│  Firebase │ Google Ads API │ Gemini AI         │
└─────────────────────────────────────────────────┘
```

## Key Features

- **Google Gen AI SDK 1.0.0**: Gemini 2.5 Pro/Flash models
- **Firebase Admin SDK 6.9.0**: Authentication & Firestore
- **Google Ads API 25.0.0**: Latest advertising API
- **FastAPI 0.115.0**: Modern async Python framework
- **Chrome Extension Manifest V3**: Latest extension standard
- **ADK Integration**: Infrastructure agents provide tools for client-created agents
- **Chrome Extension**: Contextual AI assistance on Google Ads pages

## Project Structure

```
google-ads-ai-system/
├── main.py                 # FastAPI application
├── requirements.txt        # Dependencies
├── .env                   # Environment variables
├── config/                # Configuration
├── core/                  # Core services (Auth, AI, Ads)
├── models/                # Data models
├── routers/               # API endpoints
├── services/              # Business logic
├── agents/                # ADK infrastructure agents
├── chrome_extension/      # Browser extension
├── scripts/               # Setup & deployment scripts
└── tests/                 # Test files
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/chrome-extension` - Extension authentication
- `POST /api/v1/auth/google-ads/connect` - Connect Google Ads account
- `GET /api/v1/auth/me` - Get current user

### Google Ads
- `GET /api/v1/google-ads/accounts` - List connected accounts
- `GET /api/v1/google-ads/campaigns` - Get campaigns
- `GET /api/v1/google-ads/performance/{campaign_id}` - Campaign performance
- `POST /api/v1/google-ads/campaigns` - Create campaign

### AI Services
- `POST /api/v1/ai/generate-ad-copy` - Generate ad copy
- `POST /api/v1/ai/analyze-performance` - Analyze performance
- `POST /api/v1/ai/contextual-assist` - Contextual AI assistance

### Agents
- `GET /api/v1/agents/available` - List available agents
- `POST /api/v1/agents/session` - Create agent session
- `POST /api/v1/agents/{agent_id}/run` - Run agent
- `POST /api/v1/agents/custom` - Deploy custom agent

## Building Agents with ADK

### Infrastructure Agents (Pre-built)
```python
# Available tools for client agents
- get_user_google_ads_campaigns
- get_campaign_performance  
- generate_ad_copy_with_ai
- analyze_campaign_performance_with_ai
- create_new_campaign
```

### Client Agent Creation (No-Code)
1. Access ADK web UI: `http://localhost:8000/adk/web`
2. Select infrastructure tools
3. Configure agent behavior
4. Test with sample data
5. Deploy to production

### Sample Client Agent
```python
from google.adk.agents import Agent
from agents.base_infrastructure_agent import INFRASTRUCTURE_TOOLS

campaign_manager = Agent(
    name="campaign_manager",
    model="gemini-2.5-flash",
    instruction="You are a Google Ads campaign manager...",
    tools=INFRASTRUCTURE_TOOLS
)
```

## Chrome Extension Setup

### Load Extension
1. Open `chrome://extensions/`
2. Enable Developer mode
3. Click "Load unpacked"
4. Select `chrome_extension/` folder

### Configure API Endpoint
Update `background.js`:
```javascript
this.API_BASE = 'https://your-domain.com/api/v1';
```

### Test Authentication
1. Click extension icon
2. Sign in with Google
3. Grant Google Ads permissions
4. Verify connection in popup

## Deployment

### Local Development
```bash
python main.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# ADK UI: http://localhost:8000/adk/web
```

### Docker Deployment
```bash
docker-compose up --build
```

### Google Cloud Run
```bash
python scripts/deploy.py
```

## Security

### Authentication Flow
1. User signs in via Chrome extension
2. Extension gets Google OAuth token
3. Backend verifies token with Firebase
4. User data stored in Firestore
5. Google Ads API calls use stored tokens

### Security Features
- Firebase Authentication
- Firestore security rules
- API rate limiting
- CORS configuration
- Environment variable security

## Testing

```bash
# Run tests
pytest

# Test specific modules
pytest tests/test_auth.py
pytest tests/test_google_ads.py
```

## Environment Variables

```bash
# Core API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
API_VERSION=v1

# Google Cloud & Gemini
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True
GEMINI_API_KEY=your-gemini-api-key

# Firebase
FIREBASE_PROJECT_ID=your-firebase-project-id
GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json

# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=your-developer-token
GOOGLE_ADS_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=your-client-secret
GOOGLE_ADS_REFRESH_TOKEN=your-refresh-token

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ADK Configuration
ADK_AGENTS_DIR=./agents
ADK_SESSION_DB_URL=sqlite:///./sessions.db
ADK_WEB_ENABLED=True
```

## Development

### Setting Up Development Environment
```bash
# 1. Clone repository
git clone <repository-url>
cd google-ads-ai-system

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment template
cp .env.example .env
# Edit .env with your configuration

# 5. Run setup scripts
python scripts/setup_firebase.py
python scripts/setup_google_ads.py

# 6. Start development server
python main.py
```

### Code Quality
- **Black**: Code formatting (`black .`)
- **isort**: Import sorting (`isort .`)
- **flake8**: Linting (`flake8 .`)
- **mypy**: Type checking (`mypy .`)

## License

This software is proprietary and confidential. All rights reserved.

Copyright (c) 2025. Unauthorized copying, distribution, modification, or use of this software is strictly prohibited.