"""Calculate SHA-256 hashes for a controlled set of sample files."""

import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_EVIDENCE_DIR = PROJECT_DIR / "evidence"
DEFAULT_MANIFEST_PATH = PROJECT_DIR / "output" / "hash_manifest.csv"

MANIFEST_FIELDS = [
    "file_name",
    "file_size_bytes",
    "sha256",
    "recorded_at_utc",
]


def calculate_sha256(file_path: Path) -> str:
    """Return the SHA-256 hash of a file, reading it in chunks."""
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def create_manifest(
    evidence_dir: Path,
    manifest_path: Path,
) -> int:
    """Hash regular files and write their details to a CSV manifest."""
    evidence_dir = evidence_dir.resolve()
    manifest_path = manifest_path.resolve()

    if not evidence_dir.is_dir():
        raise NotADirectoryError(
            f"Evidence directory not found: {evidence_dir}"
        )

    # Avoid writing the manifest inside the evidence directory.
    if manifest_path.is_relative_to(evidence_dir):
        raise ValueError(
            "The manifest must be outside the evidence directory."
        )

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    file_count = 0

    with manifest_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=MANIFEST_FIELDS,
        )
        writer.writeheader()

        for file_path in sorted(evidence_dir.rglob("*")):
            if file_path.is_symlink() or not file_path.is_file():
                continue

            relative_name = file_path.relative_to(
                evidence_dir
            ).as_posix()

            writer.writerow({
                "file_name": relative_name,
                "file_size_bytes": file_path.stat().st_size,
                "sha256": calculate_sha256(file_path),
                "recorded_at_utc": datetime.now(
                    timezone.utc
                ).isoformat(),
            })

            file_count += 1

    return file_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a SHA-256 manifest for sample files."
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=DEFAULT_EVIDENCE_DIR,
        help="Directory containing the sample files.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help="Path where the CSV manifest will be written.",
    )
    args = parser.parse_args()

    count = create_manifest(
        args.evidence_dir,
        args.manifest,
    )

    print(f"Files hashed: {count}")
    print(f"Manifest saved to: {args.manifest.resolve()}")


if __name__ == "__main__":
    main()
