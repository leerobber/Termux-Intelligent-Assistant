```markdown
# Termux-Intelligent-Assistant Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill introduces the development patterns and coding conventions used in the Termux-Intelligent-Assistant repository. The project is written in Python and is designed to function as an intelligent assistant within the Termux environment. This guide covers file naming, import/export styles, commit conventions, and testing patterns to help you contribute effectively.

## Coding Conventions

### File Naming
- Use **camelCase** for file names.
  - Example: `voiceAssistant.py`, `commandParser.py`

### Import Style
- Use **relative imports** within the project.
  - Example:
    ```python
    from .utils import parseCommand
    ```

### Export Style
- Use **named exports** (explicitly define what is exported from modules).
  - Example:
    ```python
    def runAssistant():
        pass

    __all__ = ['runAssistant']
    ```

### Commit Messages
- Follow **conventional commits** with the `feat` prefix for new features.
  - Example:
    ```
    feat: add speech recognition to assistant module
    ```

## Workflows

### Adding a New Feature
**Trigger:** When you want to introduce a new capability to the assistant  
**Command:** `/add-feature`

1. Create a new Python file using camelCase (e.g., `newFeature.py`).
2. Implement the feature using relative imports as needed.
3. Export functions or classes using named exports (`__all__`).
4. Write or update corresponding test files (`newFeature.test.py`).
5. Commit your changes with a message starting with `feat:`.
6. Push your branch and open a pull request.

### Writing and Running Tests
**Trigger:** When you need to validate new or existing functionality  
**Command:** `/run-tests`

1. Create or update test files following the `*.test.*` pattern (e.g., `voiceAssistant.test.py`).
2. Write test cases for your modules.
3. Run tests using your preferred Python testing tool (e.g., `pytest`, `unittest`).
4. Review test results and fix any issues.

## Testing Patterns

- Test files use the `*.test.*` naming convention (e.g., `module.test.py`).
- The specific testing framework is not enforced; use your preferred Python testing tool.
- Example test file:
  ```python
  # voiceAssistant.test.py
  import unittest
  from .voiceAssistant import runAssistant

  class TestVoiceAssistant(unittest.TestCase):
      def test_run(self):
          self.assertIsNotNone(runAssistant())
  ```

## Commands
| Command        | Purpose                                      |
|----------------|----------------------------------------------|
| /add-feature   | Scaffold and commit a new feature            |
| /run-tests     | Run all test files matching `*.test.*`       |
```
