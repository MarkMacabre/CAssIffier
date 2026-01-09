# Contributing to CAssIffier

Thank you for your interest in contributing to CAssIffier!

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/CAssIffier.git
cd CAssIffier
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install in development mode:
```bash
pip install -e .
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to all functions and classes
- Keep functions focused and modular
- Add type hints where appropriate

## Testing

Before submitting a PR:

1. Test your changes manually:
```bash
python -m cassiffier.main test_samples -o output
```

2. Ensure imports work:
```bash
python -c "from cassiffier import *"
```

3. Test the training script if you modified training code:
```bash
python train_model.py data/training
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Test your changes thoroughly
4. Commit with clear, descriptive messages
5. Push to your fork
6. Create a Pull Request with:
   - Clear description of the changes
   - Why the changes are needed
   - How to test the changes

## Areas for Contribution

- **New audio features**: Additional features for better classification
- **Improved classifiers**: Better ML models or rule-based logic
- **Additional categories**: Support for more sound types
- **Performance optimization**: Faster feature extraction or classification
- **UI improvements**: Better terminal output or optional GUI
- **Documentation**: Examples, tutorials, or improved docs
- **Bug fixes**: Always welcome!

## Design Principles

When contributing, keep these principles in mind:

- **Determinism over cleverness**: Predictable results
- **Transparency over automation**: Clear logging and user control
- **Trust over magic**: No hidden behaviors
- **Local-first**: No cloud dependencies
- **Performance**: Efficient with resources

## Questions?

Open an issue for discussion before starting major changes.
