"""
Import all generator modules to trigger field registration via side-effects.
The order here controls the display order in the UI.
"""
import app.generators.personal      # noqa: F401
import app.generators.contact       # noqa: F401
import app.generators.address       # noqa: F401
import app.generators.professional  # noqa: F401
import app.generators.account       # noqa: F401
import app.generators.financial     # noqa: F401
import app.generators.vehicle       # noqa: F401

from app.generators.registry import FIELD_REGISTRY, get_fields_by_category  # noqa: F401

__all__ = ['FIELD_REGISTRY', 'get_fields_by_category']
