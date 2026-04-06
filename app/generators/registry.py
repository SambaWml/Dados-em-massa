from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any, Optional


@dataclass
class FilterOption:
    key: str
    label: str
    type: str  # 'select', 'number', 'text'
    options: Optional[List[Dict]] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    default: Optional[Any] = None

    def to_dict(self) -> Dict:
        d = {
            'key': self.key,
            'label': self.label,
            'type': self.type,
            'default': self.default,
        }
        if self.options:
            d['options'] = self.options
        if self.min_value is not None:
            d['min'] = self.min_value
        if self.max_value is not None:
            d['max'] = self.max_value
        return d


@dataclass
class FieldDefinition:
    key: str
    label: str
    category: str
    category_label: str
    generator: Callable
    dependencies: List[str] = field(default_factory=list)
    filter_options: List[FilterOption] = field(default_factory=list)
    description: str = ""
    icon: str = "fas fa-tag"

    def to_dict(self) -> Dict:
        return {
            'key': self.key,
            'label': self.label,
            'category': self.category,
            'category_label': self.category_label,
            'dependencies': self.dependencies,
            'filter_options': [f.to_dict() for f in self.filter_options],
            'description': self.description,
            'icon': self.icon,
        }


# Global registry — populated when generator modules are imported
FIELD_REGISTRY: Dict[str, FieldDefinition] = {}

# Preserves insertion order for category display
_CATEGORY_ORDER: List[str] = []


def register_field(field_def: FieldDefinition) -> None:
    FIELD_REGISTRY[field_def.key] = field_def
    if field_def.category not in _CATEGORY_ORDER:
        _CATEGORY_ORDER.append(field_def.category)


def get_fields_by_category() -> List[Dict]:
    categories: Dict[str, Dict] = {}
    for fd in FIELD_REGISTRY.values():
        if fd.category not in categories:
            categories[fd.category] = {
                'key': fd.category,
                'label': fd.category_label,
                'fields': [],
            }
        categories[fd.category]['fields'].append(fd.to_dict())
    return [categories[k] for k in _CATEGORY_ORDER if k in categories]
