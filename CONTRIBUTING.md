# Contributing to LocalDictionary

Thank you for your interest in contributing to **LocalDictionary**!

## How Can I Contribute?

### 1. Reporting Bugs
- Check the existing GitHub Issues to see if the problem has already been reported.
- If not, open a new issue with a clear title, description, and steps to reproduce.

### 2. Suggesting Vocabulary & Grammar Improvements
- Suggestions for new idioms, proverbs, colloquial phrases, or multi-sense definitions are always welcome!
- You can submit curated TSV/CSV datasets or add rules to `src/idiom_engine.py` or `src/grammar_data.py`.

### 3. Submitting Pull Requests
1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Install dependencies and run tests locally before pushing:
   ```bash
   pip install -r requirements-dev.txt
   python -B -m unittest discover -s tests -v
   ```
3. Commit your changes with clear, descriptive commit messages.
4. Push to your branch and submit a Pull Request to `main`.

## Code Style & Guidelines
- Follow standard Python PEP 8 formatting.
- Ensure all new features include corresponding test cases in `tests/`.
- Maintain 100% offline functionality: **No external cloud APIs or online network requirements** in runtime code.
