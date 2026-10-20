"""Verify sample files against a previously generated manifest."""

import argparse
import csv
from pathlib import Path

from scripts.hash_files import (
    DEFAULT_EVIDENCE_DIR,
    DEFAULT_MANIFEST_PATH,
    calculate_sha256,
)


def verify_manifest(
    evidence_dir: Path,
    manifest_path: Path,
) -> list[dict[str, str]]:
    """Compare current files with the recorded manifest."""
    evidence_dir = evidence_dir.resolve()
    manifest_path = manifest_path.resolve()

    if not evidence_dir.is_dir():
        raise NotADirectoryError(
            f"Evidence directory not found: {evidence_dir}"
        )

    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"Manifest not found: {manifest_path}"
        )

    results = []

    with manifest_path.open(
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        required_fields = {
            "file_name",
            "file_size_bytes",
            "sha256",
        }

        if not required_fields.issubset(
            set(reader.fieldnames or [])
        ):
            raise ValueError("Manifest is missing required columns.")

        for record in reader:
            relative_path = Path(record["file_name"])

            # Only allow paths relative to the evidence directory.
            if (
                relative_path.is_absolute()
                or ".." in relative_path.parts
            ):
                raise ValueError(
                    f"Unsafe path in manifest: {record['file_name']}"
                )

            file_path = (
                evidence_dir / relative_path
            ).resolve()

            if not file_path.is_relative_to(evidence_dir):
                raise ValueError(
                    f"Path escapes evidence directory: "
                    f"{record['file_name']}"
                )

            if not file_path.is_file() or file_path.is_symlink():
                status = "MISSING"
            else:
                actual_size = file_path.stat().st_size
                actual_hash = calculate_sha256(file_path)

                if (
                    actual_size == int(record["file_size_bytes"])
                    and actual_hash == record["sha256"]
                ):
                    status = "PASS"
                else:
                    status = "CHANGED"

            results.append({
                "file_name": record["file_name"],
                "status": status,
            })

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify sample files against a SHA-256 manifest."
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=DEFAULT_EVIDENCE_DIR,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
    )
    args = parser.parse_args()

    results = verify_manifest(
        args.evidence_dir,
        args.manifest,
    )

    for result in results:
        print(
            f"{result['status']}: {result['file_name']}"
        )

    failed = any(
        result["status"] != "PASS"
        for result in results
    )

    if not results:
        print("WARNING: The manifest contains no file records.")
        raise SystemExit(1)

    if failed:
        raise SystemExit(1)

    print("All recorded files passed verification.")


if __name__ == "__main__":
    main()
