"""
Validation module initialization.

This module loads all available validators into the strategy registry.
"""

from pathlib import Path
from loguru import logger

from llm_call.core.strategies import registry

# Import all validator modules to ensure they register themselves
try:
    from llm_call.core.validation.builtin_strategies import basic_validators
    logger.info("Loaded basic validators")
except Exception as e:
    logger.error(f"Failed to load basic validators: {e}")

try:
    from llm_call.core.validation.builtin_strategies import ai_validators
    logger.info("Loaded AI validators")
except Exception as e:
    logger.error(f"Failed to load AI validators: {e}")

try:
    from llm_call.core.validation.builtin_strategies import advanced_validators
    logger.info("Loaded advanced validators")
except Exception as e:
    logger.error(f"Failed to load advanced validators: {e}")

# Also discover any validators in this directory
try:
    validation_dir = Path(__file__).parent / "builtin_strategies"
    if validation_dir.exists():
        registry.discover_strategies(validation_dir)
        logger.info(f"Discovered validators in {validation_dir}")
except Exception as e:
    logger.warning(f"Failed to discover validators: {e}")

# Log what's available
available = registry.list_all()
logger.info(f"Total validators available: {len(available)}")
for validator in available:
    logger.debug(f"  - {validator['name']}: {validator['class']}")

__all__ = ['registry']