# check-latex-math
A pre-commit hook that validates LaTex math blocks in your codebase.

To use it, you can add this to your pre-commit config file:

```
- repo: https://github.com/frazane/check-latex-math
  rev: v0.1.0
  hooks:
  - id: check-latex-math
    args: ["directory1/", "directory2/", "*.py", "*.md"]
```

and edit the arguments to your use case.
