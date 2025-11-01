# Product Explorer - Quick Start Guide

## Installation

No installation needed! The tool uses your existing dependencies from the main project.

## Usage

```bash
cd explore_product
python explore.py <product_url>
```

## Example

```bash
python explore.py https://www.spinstack.dev/
```

## What Happens

1. **Creates temporary email** via AgentMail
2. **Signs up** for the product automatically
3. **Handles verification** (clicks email links or enters codes)
4. **Explores thoroughly** - navigates all sections, tries features
5. **Documents everything** - saves comprehensive report

## Output

Two files are generated in `outputs/`:

### 1. Report (TXT)
Human-readable analysis with:
- Product description and purpose
- All discovered user actions
- Step-by-step navigation instructions
- Test account credentials

### 2. Data (JSON)
Structured data including:
- All metadata
- Recording URL
- Raw analysis output

## Live Monitoring

Watch the browser in real-time! The tool prints a live URL:

```
📺 WATCH LIVE
================================================================================
https://live.browser-use.com?wss=...
================================================================================
```

## Recording

After completion, get a permanent recording:

```
📺 Recording: https://cloud.browser-use.com/share/...
```

## Tips

- **Wait for completion** - Thorough exploration takes 2-5 minutes
- **Watch the live session** - See exactly what the AI discovers
- **Review the recording** - Verify findings by watching the replay
- **Check test credentials** - Use them to manually verify

## Requirements

API keys in parent `.env` file:
- `AGENTMAIL_API_KEY`
- `BROWSER_USE_API_KEY`
- `OPENAI_API_KEY`

## Example Output

See `EXAMPLE_OUTPUT.md` for a real Spinstack.dev analysis!

## Troubleshooting

### Product doesn't allow signup
Some products have aggressive bot detection. Check the recording to see what happened.

### Exploration seems short
The agent tries to be thorough but may miss features. Watch the recording to see coverage.

### Rate limits
Browser-Use Cloud has rate limits. The tool automatically retries with backoff.

---

**That's it! Give it any product URL and get comprehensive documentation.**

