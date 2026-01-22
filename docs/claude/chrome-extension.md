# Claude Code Chrome Extension Integration

## Overview

Claude Code integrates with the [Claude in Chrome](https://support.claude.com/en/articles/12012173-getting-started-with-claude-in-chrome) browser extension to enable browser automation directly from the terminal. This allows Claude to interact with web pages, take screenshots, read console logs, and automate browser tasks.

## Requirements

- Google Chrome browser
- Claude in Chrome extension (v1.0.36+)
- Claude Code CLI (v2.0.73+)
- Paid Claude plan (Pro, Team, or Enterprise)

## Setup

### 1. Update Claude Code
```bash
claude update
```

### 2. Start with Chrome enabled
```bash
claude --chrome
```

### 3. Verify connection
```bash
/chrome
```

## Available Tools

Run `/mcp` and click into `claude-in-chrome` to see the full list of MCP tools. Key capabilities include:

| Category | Capabilities |
|----------|-------------|
| **Navigation** | Open pages, manage tabs, go back/forward |
| **Interaction** | Click elements, type text, fill forms, scroll |
| **Reading** | Access console logs, DOM state, network requests |
| **Control** | Resize windows, record GIFs |
| **Session** | Leverage existing browser login state |

## Common Commands

### Test Local Web Applications
```
Open localhost:8000/web/todos and check if the todo items render correctly.
Take a screenshot of the result.
```

### Debug with Console Logs
```
Open the page and check the console for any JavaScript errors.
```

### Extract DOM Structure
```
Get the HTML structure of the main content area.
```

### Take Screenshots
```
Take a screenshot of the current page.
```

### Record Demo GIF
```
Record a GIF showing the filter functionality.
```

## Usage for This Project

When developing this Workflowy Flow app, use the Chrome extension to:

1. **Verify UI rendering** - Take screenshots to confirm colors, layouts, and styling
2. **Test interactions** - Click buttons, fill filters, drag kanban cards
3. **Debug issues** - Read console logs for errors
4. **Inspect DOM** - Check HTML structure for correct rendering

### Example Workflow
```bash
# Start Claude Code with Chrome
mise exec -- claude --chrome

# In Claude Code, ask to test the app:
> Open localhost:8000/web/todos and take a screenshot
> Click the Refresh button and wait for loading to complete
> Filter for "supplier" and take a screenshot of the results
> Check the console for any errors
```

## Troubleshooting

### Extension Not Detected
1. Verify extension version 1.0.36+ is installed
2. Verify Claude Code version 2.0.73+ (`claude --version`)
3. Ensure Chrome is running with the extension enabled
4. Run `/chrome` and select "Reconnect extension"
5. Restart both Claude Code and Chrome

### Browser Not Responding
1. Check for blocking modal dialogs (alerts, confirms)
2. Ask Claude to create a new tab
3. Restart Chrome extension (disable/re-enable in chrome://extensions)

### Screenshot Fails
There's a known bug where screenshots fail with "Cannot access a chrome-extension:// URL". Workaround:
- Ensure you're on a regular webpage (not chrome:// or extension pages)
- Try refreshing the page first
- Create a new tab and navigate to the URL

## Architecture

- Uses Chrome's **Native Messaging API** for CLI-to-Chrome communication
- Requires **visible browser window** (no headless mode)
- **Shares browser login state** - works with authenticated sites
- Opens **new tabs** rather than taking over existing ones

## Limitations

- **Beta status**: Google Chrome only (not Brave, Arc, or other Chromium browsers)
- WSL (Windows Subsystem for Linux) not supported
- Modal dialogs (alerts, prompts) block automation

## References

- [Claude Code Chrome Docs](https://code.claude.com/docs/en/chrome)
- [Getting Started with Claude in Chrome](https://support.claude.com/en/articles/12012173-getting-started-with-claude-in-chrome)
- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) (alternative for advanced debugging)
