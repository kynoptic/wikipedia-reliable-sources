# Slash commands reference

Detailed best practices and patterns for creating effective slash commands.

> **Note**: Slash commands use Claude Code format only. They are not distributed via agent-playbook's multi-platform build process. This reference shows the standard Claude Code format for creating commands in any project.

## Structure and format

### Minimal command

```markdown
---
description: Brief description of what this command does
---

Your prompt or instructions here.
```

### Full-featured command

```markdown
---
description: Brief description of what this command does
allowed-tools: Bash(git:*), Read, Grep
argument-hint: <file-path> [options]
---

Your prompt or instructions here.

Use $ARGUMENTS for all arguments or $1, $2, etc. for specific positional arguments.
```

## Frontmatter fields

### description (required)

**Critical**: This field is required for the `SlashCommand` tool to function properly.

**Best practices**:

- Keep it concise (1-2 sentences)
- Use active voice
- Describe what the command does, not how
- Examples:
  - ✅ "Reviews pull request for code quality and standards compliance"
  - ✅ "Generates unit tests for the specified file"
  - ❌ "This command helps you review PRs"
  - ❌ "Use this to create tests"

### allowed-tools (optional)

Restricts which tools Claude can use when executing this command.

**Syntax**:

- `Bash(git:*)` - Allow all git commands
- `Bash(git status:*), Bash(git diff:*)` - Allow specific git commands
- `Read, Grep, Glob` - Allow specific tools

**Use when**:

- Command should be read-only (use `Read, Grep, Glob` only)
- Command should only execute specific operations
- You want to prevent accidental destructive actions

**Examples**:

```yaml
# Read-only code review
allowed-tools: Read, Grep, Glob

# Git status only
allowed-tools: Bash(git status:*), Bash(git diff:*), Read

# Safe test execution
allowed-tools: Bash(npm test:*), Bash(pytest:*), Read
```

### argument-hint (optional)

Displays hint text for command arguments in the UI.

**Best practices**:

- Use angle brackets for required: `<file-path>`
- Use square brackets for optional: `[options]`
- Be descriptive but concise
- Examples:
  - `<file-path>` - Single required argument
  - `<source> <destination>` - Multiple required arguments
  - `<file-path> [--verbose]` - Required with optional flag
  - `[test-name]` - Single optional argument

## Argument handling

### All arguments as one string

Use `$ARGUMENTS` to capture all arguments:

```markdown
---
description: Runs tests matching the pattern
argument-hint: [test-pattern]
---

Run tests matching pattern: $ARGUMENTS

If no pattern provided, run all tests.
```

### Positional arguments

Use `$1`, `$2`, etc. for specific arguments:

```markdown
---
description: Compares two files
argument-hint: <file1> <file2>
---

Compare these two files:
- First file: $1
- Second file: $2

Show differences in unified diff format.
```

### Dynamic file references

Use `@` prefix for file references:

```markdown
---
description: Reviews the specified file
argument-hint: <file-path>
---

@$1

Review the file above for:
- Code quality
- Best practices
- Potential bugs
```

## Command patterns

### Code review command

```markdown
---
description: Reviews pull request for quality and standards compliance
allowed-tools: Bash(git:*), Read, Grep, Glob
---

1. Run `git diff main...[@CURRENT_BRANCH]` to see changes
2. Review all modified files for:
   - Code quality and clarity
   - Test coverage
   - Documentation updates
   - Breaking changes
3. Provide actionable feedback with file:line references
```

### Test generation command

```markdown
---
description: Generates unit tests for the specified file
argument-hint: <file-path>
allowed-tools: Read, Write, Bash(npm test:*)
---

@$1

Generate comprehensive unit tests for the file above:
- Test all public methods
- Include edge cases
- Follow test naming: `test_should_<behavior>_when_<condition>`
- Write tests in the same language/framework
- Place in appropriate test directory
```

### Documentation command

```markdown
---
description: Updates README with recent changes
allowed-tools: Read, Edit, Bash(git log:*)
---

1. Read current README.md
2. Run `git log -10 --oneline` to see recent changes
3. Update README sections:
   - Installation (if dependencies changed)
   - Usage (if API changed)
   - Changelog (add recent features/fixes)
4. Follow project documentation style
```

### Quick reference command

```markdown
---
description: Shows git commands cheatsheet
---

# Git commands cheatsheet

## Common operations
- `git status` - Show working tree status
- `git add <file>` - Stage changes
- `git commit -m "message"` - Commit changes
- `git push` - Push to remote

## Branching
- `git branch` - List branches
- `git checkout -b <name>` - Create and switch to branch
- `git merge <branch>` - Merge branch

## History
- `git log --oneline` - Compact history
- `git diff` - Show changes
```

## Best practices

### Do

- **Keep it simple** - One file, one purpose
- **Be specific** - Clear, actionable instructions
- **Use constraints** - Restrict tools when appropriate
- **Test thoroughly** - Try with different arguments
- **Document arguments** - Use `argument-hint` for clarity

### Don't

- **Don't make it complex** - If you need multiple files, use a skill
- **Don't be vague** - "Review the code" vs "Review for security vulnerabilities"
- **Don't allow all tools** - Be explicit about `allowed-tools`
- **Don't forget edge cases** - Handle missing arguments gracefully

## When to upgrade to a skill

Upgrade from slash command to skill when:

1. **Multiple files needed** - Templates, scripts, reference docs
2. **Team standardization** - Workflow should be consistent across team
3. **Automatic discovery** - Should trigger without explicit command
4. **Progressive disclosure** - Need to reference detailed information on demand

## Troubleshooting

### Command not appearing

- Check `description` field is present (required)
- Verify file is in `.claude/commands/` or `~/.claude/commands/`
- Ensure filename ends with `.md`
- Restart Claude Code or reload project

### Arguments not working

- Use `$ARGUMENTS` for all args or `$1`, `$2` for specific
- Check `argument-hint` matches your usage
- Test with and without arguments

### Tool restrictions not working

- Verify `allowed-tools` syntax
- Use exact tool names (case-sensitive)
- Check Bash command patterns: `Bash(command:*)`

## Examples by use case

### Personal productivity

```markdown
---
description: Quick commit with conventional commit message
argument-hint: <type> <message>
---

Stage all changes and commit with message: "$1: $2"

Use conventional commit format.
```

### Code quality

```markdown
---
description: Runs linter and fixes auto-fixable issues
allowed-tools: Bash(npm run lint:*), Bash(eslint:*)
---

1. Run linter: `npm run lint`
2. Auto-fix: `npm run lint -- --fix`
3. Report remaining issues
```

### Project setup

```markdown
---
description: Scaffolds new component directory
argument-hint: <component-name>
---

Create directory structure for component: $1

- `src/components/$1/`
- `src/components/$1/index.ts`
- `src/components/$1/$1.tsx`
- `src/components/$1/$1.test.tsx`
- `src/components/$1/$1.module.css`

Use project conventions and TypeScript.
```
