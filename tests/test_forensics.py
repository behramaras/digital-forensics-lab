"""Unit tests for the digital forensics learning utilities."""

import tempfile
import unittest
from pathlib import Path

from scripts.hash_files import (
    calculate_sha256,
    create_manifest,
)
from scripts.verify_hashes import verify_manifest


class DigitalForensicsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        self.evidence_dir = self.root / "evidence"
        self.output_dir = self.root / "output"
        self.manifest_path = (
            self.output_dir / "hash_manifest.csv"
        )

        self.evidence_dir.mkdir()
        self.output_dir.mkdir()

        self.sample_file = (
            self.evidence_dir / "sample.txt"
        )
        self.sample_file.write_text(
            "Original training evidence\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sha256_is_deterministic(self):
        first_hash = calculate_sha256(self.sample_file)
        second_hash = calculate_sha256(self.sample_file)

        self.assertEqual(first_hash, second_hash)
        self.assertEqual(len(first_hash), 64)

    def test_manifest_creation_and_verification(self):
        count = create_manifest(
            self.evidence_dir,
            self.manifest_path,
        )

        self.assertEqual(count, 1)
        self.assertTrue(self.manifest_path.is_file())

        results = verify_manifest(
            self.evidence_dir,
            self.manifest_path,
        )

        self.assertEqual(
            results,
            [{"file_name": "sample.txt", "status": "PASS"}],
        )

    def test_modified_file_is_detected(self):
        create_manifest(
            self.evidence_dir,
            self.manifest_path,
        )

        self.sample_file.write_text(
            "Modified training evidence\n",
            encoding="utf-8",
        )

        results = verify_manifest(
            self.evidence_dir,
            self.manifest_path,
        )

        self.assertEqual(results[0]["status"], "CHANGED")

    def test_missing_file_is_detected(self):
        create_manifest(
            self.evidence_dir,
            self.manifest_path,
        )

        self.sample_file.unlink()

        results = verify_manifest(
            self.evidence_dir,
            self.manifest_path,
        )

        self.assertEqual(results[0]["status"], "MISSING")


if __name__ == "__main__":
    unittest.main()
