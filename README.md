# Digital Forensics Lab

A hands-on learning project exploring SHA-256 hashing, file integrity
verification and evidence documentation using Python.

## Project Objectives

- Calculate SHA-256 hashes for synthetic sample files.
- Record file names, sizes and hash values in a CSV manifest.
- Verify recorded files against a previously generated manifest.
- Detect missing or modified files.
- Practise documenting a repeatable technical workflow.

## Technologies

- Python 3.9 or later
- SHA-256 via Python's `hashlib`
- CSV and file handling via the Python standard library
- `unittest` for automated tests

No third-party Python packages are required.

## Repository Structure

```text
digital-forensics-lab/
├── evidence/
├── scripts/
├── tests/
├── output/
└── README.md
```

## Getting Started

Clone the repository and open a terminal in its root directory.

### 1. Generate a hash manifest

```bash
python scripts/hash_files.py
```

The command hashes files in `evidence/` and creates:

`output/hash_manifest.csv`

### 2. Verify file integrity

```bash
python scripts/verify_hashes.py
```

Expected statuses:

- `PASS`: Current file size and SHA-256 hash match the manifest.
- `CHANGED`: File size or hash differs from the recorded values.
- `MISSING`: A recorded file is no longer available.

### 3. Run the tests

```bash
python -m unittest discover -s tests -v
```

The tests use temporary directories and do not modify the sample
evidence files in the repository.

## Methodology

The hashing script reads each regular sample file in binary chunks
and calculates its SHA-256 digest.

The manifest records the relative file path, file size, calculated
hash and UTC time when the record is generated.

The verification script recalculates the current hash and compares
it with the recorded values.

## Limitations

This project is an educational exercise, not a professional forensic
acquisition or examination.

- The sample files are synthetic.
- No physical disk imaging is performed by the Python scripts.
- The manifest is not digitally signed or independently secured.
- A successful hash comparison does not establish who created a file,
  when it was originally created or whether it was trustworthy before
  the initial hash was recorded.
- This project does not implement a formal chain-of-custody process.
- The scripts are not validated forensic software.

## Learning Outcomes

The project demonstrates practical experience with file hashing,
integrity checks, CSV reporting, Python automation and unit testing.

Further work may explore forensic disk images, filesystem artefacts
and examination workflows using dedicated digital forensics tools.
