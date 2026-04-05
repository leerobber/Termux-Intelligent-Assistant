```markdown
# Termux-Intelligent-Assistant Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill covers the development patterns and conventions used in the Termux-Intelligent-Assistant repository. The project is written in Python and is designed to function without a specific framework, focusing on building an intelligent assistant for the Termux environment. You'll learn about the project's coding style, commit practices, and how to contribute effectively.

## Coding Conventions

### File Naming
- Use **snake_case** for all file names.
  - Example: `voice_handler.py`, `command_parser.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import parse_command
    from .core import Assistant
    ```

### Export Style
- Use **named exports** for functions and classes.
  - Example:
    ```python
    def handle_input(input_text):
        ...
    class Assistant:
        ...
    ```

### Commit Messages
- Use mixed commit types, often prefixed with `fix` or `refactor`.
- Keep commit messages concise (average 51 characters).
  - Example:
    ```
    fix: handle empty input in command parser
    refactor: modularize speech recognition logic
    ```

## Workflows

### Code Contribution
**Trigger:** When adding new features or fixing bugs  
**Command:** `/contribute`

1. Create a new branch for your changes.
2. Follow the coding conventions for file naming, imports, and exports.
3. Write or update tests as needed (see Testing Patterns).
4. Commit changes with a descriptive message, using `fix:` or `refactor:` as appropriate.
5. Push your branch and open a pull request.

### Bug Fixing
**Trigger:** When addressing a reported bug  
**Command:** `/bugfix`

1. Identify the bug and create a branch named `fix/<short-description>`.
2. Locate the relevant code and apply the fix.
3. Add or update a test to cover the bug scenario.
4. Commit with a `fix:` prefix.
5. Push and submit a pull request.

### Refactoring
**Trigger:** When improving code structure without changing functionality  
**Command:** `/refactor`

1. Create a branch named `refactor/<short-description>`.
2. Refactor code, maintaining existing behavior.
3. Ensure all tests pass.
4. Commit with a `refactor:` prefix.
5. Push and open a pull request.

## Testing Patterns

- Test files follow the pattern `*.test.*` (e.g., `assistant.test.py`).
- The specific testing framework is not specified; check existing test files for structure.
- Place tests alongside implementation files or in a dedicated `tests/` directory if present.
- Example test file:
  ```python
  # assistant.test.py
  from .assistant import Assistant

  def test_assistant_response():
      assistant = Assistant()
      assert assistant.respond("hello") == "Hi, how can I help you?"
  ```

## Commands
| Command      | Purpose                                      |
|--------------|----------------------------------------------|
| /contribute  | Start a new code contribution workflow       |
| /bugfix      | Begin a bug fixing workflow                  |
| /refactor    | Initiate a code refactoring workflow         |
```
