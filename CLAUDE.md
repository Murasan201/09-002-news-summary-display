# Claude Code Rules

## Project Commands

### Development
- `npm run dev` - Start development server
- `npm run build` - Build the project
- `npm run lint` - Run linter
- `npm run typecheck` - Run TypeScript type checking
- `npm test` - Run tests

### Git Workflow
- Default branch: `main`
- Create feature branches from `main`
- Run lint and typecheck before committing
- **CRITICAL: Security Check Before Commit**
  - ⚠️ **ALWAYS verify no sensitive information before git add/commit**
  - Check for API keys, tokens, passwords, or credentials
  - Verify `.env`, `.mcp.json`, and other config files are in `.gitignore`
  - Review all staged files with `git diff --cached`
  - Never commit files containing secrets to version control

## Code Style
- Follow existing code conventions in the project
- Use TypeScript for type safety
- No comments unless specifically requested
- Follow security best practices

## Security Requirements

### API Key Management
- **MANDATORY: Use Environment Variables for All API Keys**
  - ✅ Store API keys in `.env` file (for application config)
  - ✅ Store API keys in `.mcp.json` file (for MCP tools config)
  - ❌ NEVER hardcode API keys in source code
  - ❌ NEVER commit `.env` or `.mcp.json` files to Git

### Pre-Commit Security Checklist
Before every `git add` and `git commit`:
1. ✅ Verify `.gitignore` includes all sensitive files:
   - `.env`
   - `.mcp.json`
   - `*.key`
   - `credentials.json`
   - Any files containing secrets
2. ✅ Run `git status` and review all files to be committed
3. ✅ Run `git diff --cached` to inspect actual changes
4. ✅ Search for potential secrets: API keys, tokens, passwords
5. ✅ Confirm no accidental inclusion of config files with credentials

### Emergency Response for Leaked Credentials
If credentials are accidentally committed:
1. **Immediately revoke/regenerate** the leaked credentials
2. Remove from Git history using `git filter-branch`
3. Force push to overwrite remote history
4. Clean up refs and garbage collect
5. Verify complete removal with `git log --all` and `git grep`

## Project Goals
This is a news summary bulletin board application project for programming beginners.

## Implementation Guidelines
- **Simplicity First**: Keep implementation as simple and understandable as possible
- **Educational Purpose**: Code should be readable by programming beginners
- **Minimal Dependencies**: Use only essential libraries
- **Single File**: Implement in one Python file for easy understanding
- **Clear Comments**: Add explanatory comments for beginners (Japanese preferred)
- **Error Handling**: Simple but effective error handling with clear messages
- **Step-by-Step Logic**: Break down complex operations into clear, sequential steps

## Project Structure
- Single Python file implementation
- `.env` file for API keys (⚠️ MUST be in `.gitignore`)
- `.mcp.json` file for MCP tools API keys (⚠️ MUST be in `.gitignore`)
- Clear function separation for each major feature
- Beginner-friendly variable and function names

## Repository Information
- GitHub Repository: https://github.com/Murasan201/09-001-news-summary-display
- Default branch: `main`

## MCP Tools Integration

### Available MCP Tools
This project has access to advanced MCP (Model Context Protocol) tools that should be actively utilized:

#### 1. Google Search (Gemini API)
- **Tool**: `mcp__gemini-google-search__google_search`
- **Purpose**: Search for up-to-date information on the web
- **Use Cases**:
  - Verify latest API specifications (e.g., OpenAI GPT-5-mini features)
  - Research RSS feed formats and best practices
  - Find solutions to technical problems
  - Check for library updates and breaking changes
  - Validate hardware specifications and compatibility
- **When to Use**:
  - When documentation needs verification
  - When encountering unfamiliar errors
  - When checking if libraries/APIs have been updated
  - Before implementing features based on potentially outdated information

#### 2. Serena (Semantic Analysis)
- **Tool**: Serena MCP
- **Purpose**: Semantic analysis for context compression
- **Use Cases**:
  - Analyzing existing documentation efficiently
  - Understanding complex codebases
  - Compressing large context for better processing
  - Extracting key concepts from technical documents
- **When to Use**:
  - When reading large documentation files
  - When analyzing code structure and relationships
  - When summarizing technical specifications

### MCP Usage Guidelines
- **Proactive Use**: Don't wait for errors - verify information proactively
- **Verification First**: When uncertain about API specifications or features, search first
- **Context Optimization**: Use Serena to compress context when dealing with large documents
- **Stay Current**: Technology changes rapidly - always verify you're using the latest information
- **Combine Tools**: Use Google Search for latest info, then Serena to analyze and compress results

### Example Workflows
1. **API Integration**: Search for latest API docs → Verify model names and parameters → Implement
2. **Library Usage**: Search for current library versions → Check breaking changes → Update code
3. **Documentation Review**: Use Serena to analyze docs → Extract key patterns → Apply to code
4. **Troubleshooting**: Search for error messages → Find solutions → Implement fixes