# AdMatch AI MVP

Three-party AI Agent advertising matching platform using Google Gemini API.

## Overview

AdMatch AI is a proof-of-concept platform that demonstrates AI-powered matching between advertisers and content creators, with audience feedback integration. The system uses multiple Gemini models with different thinking levels for various tasks.

### Participants

**Advertisers (3)**
- **BrewLab Coffee** - Specialty coffee brand targeting urban professionals
- **CloudDesk SaaS** - Cloud collaboration platform for tech teams
- **NatureStep Skincare** - Organic skincare brand for eco-conscious consumers

**Creators (3)**
- **Ken (lifestyle)** - Lifestyle blogger focusing on coffee culture and urban exploration
- **Mia (sustainability)** - Environmental content creator focused on zero-waste living
- **DevTalk (tech)** - Developer-focused channel with tutorials and tool reviews

**Audiences (3)**
- Each creator has a distinct audience with different acceptance thresholds

## Project Structure

```
socialMediaMarket/
├── main.py                 # Orchestrator - runs all 4 flows
├── model_router.py         # Dynamic model selection + API logging
├── agents/
│   ├── __init__.py
│   ├── advertiser_agent.py # PRO/HIGH for analysis
│   ├── creator_agent.py    # PRO/HIGH for analysis
│   └── audience_agent.py   # FLASH_LITE/LOW for scoring
├── engine/
│   ├── __init__.py
│   ├── embedding.py        # Embedding generation (EMBED model)
│   └── matching.py         # Cosine similarity + weighted matrix
├── negotiation/
│   ├── __init__.py
│   └── negotiation.py      # 3-round negotiation flow
├── report/
│   ├── __init__.py
│   └── generator.py        # Markdown report (PRO/MEDIUM)
├── data/
│   ├── __init__.py
│   └── scenarios.py        # Hard-coded test data (Chinese)
├── requirements.txt
└── README.md
```

## Model Configuration

| Task | Model | thinking_level |
|------|-------|----------------|
| Agent deep analysis (Flow 1) | `gemini-3.1-pro-preview` | HIGH |
| Embedding description gen | `gemini-3-flash-preview` | MEDIUM |
| Embedding vectorization | `gemini-embedding-2-preview` | N/A |
| Negotiation dialogue | `gemini-3.1-pro-preview` | MEDIUM |
| Audience scoring | `gemini-3.1-flash-lite-preview` | LOW |
| Audience intervention | `gemini-3.1-flash-lite-preview` | LOW |
| Report generation | `gemini-3.1-pro-preview` | MEDIUM |

## Four Core Flows

### Flow 1: Agent Deep Analysis
Each agent (Advertiser/Creator) analyzes their role using PRO/HIGH and outputs structured JSON profiles with:
- Campaign/content summary
- Ideal partner traits
- Negotiation priorities
- Embedding description text

### Flow 2: Embedding & Matching Matrix
- Generate embedding descriptions with FLASH/MEDIUM
- Vectorize with EMBED model
- Compute 3x3 raw cosine similarity matrix
- Apply weighted scoring (embedding: 40%, audience: 25%, budget: 20%, values: 15%)
- Output 3x3 weighted comprehensive matrix
- Display ASCII heatmaps
- Select top 3 matches for negotiation

### Flow 3: Negotiation Simulation
For each top 3 match:
- **Round 1**: Advertiser offers (PRO/MEDIUM)
- **Round 2**: Creator responds (PRO/MEDIUM)
- **Round 3**: Final terms (PRO/MEDIUM)
- After each round: Audience scores (FLASH_LITE/LOW)
- If score < threshold: Audience intervention warning
- Outcome: SUCCESS / FAILED / AUDIENCE_REJECTED

### Flow 4: Final Report
- Generate comprehensive markdown report (PRO/MEDIUM)
- Save to `report.md`
- Sections: Executive Summary, Profiles, Matrices, Negotiations, Statistics

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Set API key (Windows)
set GEMINI_API_KEY=your_api_key_here

# Set API key (Linux/Mac)
export GEMINI_API_KEY=your_api_key_here

# Run the MVP
python main.py
```

## Expected Outcomes

Based on scenario design:
- **CloudDesk + DevTalk**: High match (tech), tolerant audience → SUCCESS
- **NatureStep + Mia**: High match but strict audience (0.45 threshold) → AUDIENCE_REJECTED
- **BrewLab + Ken**: Moderate match → Variable outcome

## Error Handling

- Exponential backoff retry (max 3 attempts): 1s → 2s → 4s
- Graceful degradation: If one agent fails, continue with others
- All API calls logged with model name + thinking_level

## Technical Notes

- Uses `google-genai` SDK (NOT deprecated `google-generativeai`)
- ThinkingConfig format: `types.ThinkingConfig(thinking_level="HIGH/MEDIUM/LOW")`
- Never sets temperature parameter
- Never uses thinking_budget with thinking_level

## Output Files

- `report.md` - Comprehensive matching and negotiation report
- Console output - Real-time progress and ASCII heatmaps

## License

MIT License
