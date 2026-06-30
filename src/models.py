from dataclasses import dataclass


@dataclass
class FieldDef:
    field: str
    cor_x: int
    cor_y: int
    pause: float


@dataclass
class Plugin:
    name: str
    image_path: str
    fields: list[FieldDef]


@dataclass
class TestCase:
    values: dict[str, str]   # field name -> cell value or event token
    row_index: int = 0       # 1-based Excel row number; 0 = unknown (tests)
