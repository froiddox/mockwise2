import json
from pathlib import Path

from models import FieldDef, Plugin


PLUGINS_DIR = Path(__file__).parent.parent / "Plugins"


def load_plugins() -> dict[str, Plugin]:
    plugins: dict[str, Plugin] = {}

    if not PLUGINS_DIR.exists():
        return plugins

    for json_path in sorted(PLUGINS_DIR.glob("*.json")):
        name = json_path.stem
        png_path = PLUGINS_DIR / f"{name}.png"

        if not png_path.exists():
            print(f"Warning: '{name}.json' has no matching '{name}.png' — skipped.")
            continue

        try:
            raw = json.loads(json_path.read_text(encoding="utf-8"))
            fields = [
                FieldDef(
                    field=entry["field"],
                    cor_x=int(entry["corX"]),
                    cor_y=int(entry["corY"]),
                    pause=float(entry["pause"]),
                )
                for entry in raw
            ]
        except (KeyError, ValueError, json.JSONDecodeError) as exc:
            print(f"Warning: failed to load plugin '{name}': {exc} — skipped.")
            continue

        key = name.strip().lower()
        plugins[key] = Plugin(name=name, image_path=str(png_path), fields=fields)

    return plugins
