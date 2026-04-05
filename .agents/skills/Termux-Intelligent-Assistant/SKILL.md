```markdown
# Termux-Intelligent-Assistant Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill introduces the development patterns and conventions used in the Termux-Intelligent-Assistant Python codebase. You'll learn how to structure files, write imports and exports, follow commit message styles, and understand basic testing patterns. This guide is ideal for contributors who want to maintain consistency and quality in this repository.

## Coding Conventions

### File Naming
- Use **snake_case** for all Python files.
  - Example: `main_module.py`, `voice_handler.py`

### Import Style
- Prefer **relative imports** within the package.
  - Example:
    ```python
    from .utils import parse_command
    from .models import AssistantModel
    ```

### Export Style
- Use **named exports** (explicitly listing what is exported).
  - Example:
    ```python
    __all__ = ['Assistant', 'VoiceHandler']
    ```

### Commit Messages
- Mixed types, with some using the `fix` prefix.
- Average commit message length: ~46 characters.
  - Example:
    ```
    fix: handle edge case in command parsing
    ```

## Workflows

### Adding a New Feature
**Trigger:** When you want to introduce new functionality.
**Command:** `/add-feature`

1. Create a new Python file using snake_case (e.g., `new_feature.py`).
2. Implement your feature, using relative imports for any shared modules.
3. Add named exports if your module provides reusable classes or functions.
4. Write or update tests in a corresponding `*.test.*` file.
5. Commit changes, optionally using a descriptive prefix (e.g., `feat:`).

### Fixing a Bug
**Trigger:** When you need to resolve an issue or bug.
**Command:** `/fix-bug`

1. Locate the relevant file(s) using snake_case naming.
2. Apply your fix, maintaining relative import style.
3. Update or add tests to cover the bug fix.
4. Commit with a message starting with `fix:`, describing the change.

### Writing and Running Tests
**Trigger:** When adding new code or verifying existing functionality.
**Command:** `/run-tests`

1. Write tests in files matching the `*.test.*` pattern (e.g., `voice_handler.test.py`).
2. Use your preferred testing framework (none detected; choose one if needed).
3. Run tests manually or with your chosen test runner.
4. Ensure all tests pass before merging changes.

## Testing Patterns

- Test files follow the `*.test.*` naming convention.
  - Example: `assistant.test.py`
- No specific testing framework detected; you may use `unittest`, `pytest`, or another Python testing tool.
- Place tests alongside the modules they cover or in a dedicated tests directory.

## Commands
| Command      | Purpose                                      |
|--------------|----------------------------------------------|
| /add-feature | Start the workflow for adding a new feature  |
| /fix-bug     | Begin the process of fixing a bug            |
| /run-tests   | Run all test files in the repository         |
```
