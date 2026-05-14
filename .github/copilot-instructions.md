<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

## Project: mcp (MCP Server)

- **Stack:** Python 3.11+, FastAPI
- **Critical rule:** Never add a command to the allowlist without explicit user confirmation
- **Every new allowed command must document:** Purpose · Risk level (read-only/write/destructive) · Who/what triggers it
- **Secrets:** `.env` always gitignored; no credentials in source files
- **CHANGELOG:** Update for every meaningful change; commit to `main`

For full coding standards see workspace `docs/CODING_STANDARDS.md`.
