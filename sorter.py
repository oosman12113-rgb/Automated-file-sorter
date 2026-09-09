from __future__ import annotations

import argparse
import json
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping


DEFAULT_CATEGORIES: Dict[str, list[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".csv", ".ppt", ".pptx"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".webm", ".m4v"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code": [".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".hpp", ".html", ".css", ".json", ".xml", ".sql"],
}


@dataclass(frozen=True)
class SortResult:
    moved: int = 0
    skipped: int = 0
    errors: int = 0


def load_categories(config_path: Path | None) -> Dict[str, list[str]]:
    """Load extension categories from JSON, or return defaults if no config is provided."""
    if config_path is None:
        return DEFAULT_CATEGORIES.copy()

    with config_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    categories: Dict[str, list[str]] = {}
    for category, extensions in raw.items():
        if not isinstance(category, str) or not isinstance(extensions, list):
            raise ValueError("Config must map category names to lists of file extensions.")

        normalized = []
        for extension in extensions:
            if not isinstance(extension, str):
                raise ValueError("Every file extension in the config must be a string.")
            extension = extension.strip().lower()
            if not extension.startswith("."):
                extension = "." + extension
            normalized.append(extension)

        categories[category] = normalized

    return categories


def build_extension_map(categories: Mapping[str, Iterable[str]]) -> Dict[str, str]:
    """Convert category->extensions data into extension->category lookup data."""
    extension_map: Dict[str, str] = {}
    for category, extensions in categories.items():
        for extension in extensions:
            extension_map[extension.lower()] = category
    return extension_map


def unique_destination(destination: Path) -> Path:
    """Return a non-conflicting path by appending (1), (2), etc. when necessary."""
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent

    counter = 1
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def should_ignore(
    path: Path,
    destination_root: Path,
    category_names: set[str],
    log_path: Path | None,
) -> bool:
    """Return True for files already inside sorter-created destination folders."""
    if log_path is not None and path.resolve() == log_path.resolve():
        return True

    try:
        relative = path.resolve().relative_to(destination_root.resolve())
    except ValueError:
        return False

    return bool(relative.parts and relative.parts[0] in category_names)


def sort_folder(
    source: Path,
    destination_root: Path | None = None,
    *,
    categories: Mapping[str, Iterable[str]] | None = None,
    dry_run: bool = False,
    recursive: bool = False,
    log_path: Path | None = None,
) -> SortResult:
    """
    Sort files into category folders.

    Unknown extensions are placed in an 'Other' folder.
    Existing filenames are preserved by generating a unique destination name.
    """
    source = source.expanduser().resolve()
    destination_root = (destination_root or source).expanduser().resolve()

    if not source.exists():
        raise FileNotFoundError(f"Source folder does not exist: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {source}")

    categories = categories or DEFAULT_CATEGORIES
    extension_map = build_extension_map(categories)
    category_names = set(categories.keys()) | {"Other"}

    moved = skipped = errors = 0

    iterator = source.rglob("*") if recursive else source.iterdir()

    for path in iterator:
        if not path.is_file():
            continue

        if should_ignore(path, destination_root, category_names, log_path):
            skipped += 1
            continue

        category = extension_map.get(path.suffix.lower(), "Other")
        category_dir = destination_root / category
        target = unique_destination(category_dir / path.name)

        try:
            if dry_run:
                logging.info("[DRY RUN] %s -> %s", path, target)
            else:
                category_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path), str(target))
                logging.info("Moved %s -> %s", path, target)
            moved += 1
        except OSError as exc:
            errors += 1
            logging.error("Could not move %s: %s", path, exc)

    return SortResult(moved=moved, skipped=skipped, errors=errors)


def configure_logging(log_path: Path | None, verbose: bool) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=handlers,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automatically organize files into folders based on file type."
    )
    parser.add_argument("source", type=Path, help="Folder containing files to sort.")
    parser.add_argument(
        "-d", "--destination",
        type=Path,
        default=None,
        help="Optional destination root. Defaults to the source folder."
    )
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=None,
        help="Optional JSON config file defining custom categories."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would happen without moving any files."
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Include files inside subfolders."
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=None,
        help="Optional path for a log file."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable more detailed console output."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(args.log, args.verbose)

    try:
        categories = load_categories(args.config)
        result = sort_folder(
            source=args.source,
            destination_root=args.destination,
            categories=categories,
            dry_run=args.dry_run,
            recursive=args.recursive,
            log_path=args.log,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        logging.error("%s", exc)
        raise SystemExit(1)

    action = "Would move" if args.dry_run else "Moved"
    print(
        f"{action}: {result.moved} file(s) | "
        f"Skipped: {result.skipped} | Errors: {result.errors}"
    )


if __name__ == "__main__":
    main()
