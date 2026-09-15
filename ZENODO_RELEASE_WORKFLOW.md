# GitHub and Zenodo release workflow

Use one Zenodo archiving route for a given version. This package assumes a manual Zenodo deposit so that a DOI can be reserved and inserted before publication. Do not also enable automatic GitHub-to-Zenodo archiving for version 0.3.2.

## 1. Complete metadata

Edit `release_metadata.yml` with the complete author order, affiliations, ORCID iDs, GitHub repository URL, and funding and conflict statements.

## 2. Create the GitHub repository

Create an empty public repository, push these files, and verify that continuous integration passes. Do not create the final tag yet.

## 3. Reserve the Zenodo DOI

Create a Zenodo software draft and use the DOI reservation option. Keep the draft open. Enter the reserved DOI and draft record URL in `release_metadata.yml`.

## 4. Finalize and validate

```bash
python scripts/finalize_release_metadata.py --metadata release_metadata.yml
python scripts/check_release_readiness.py
python scripts/validate_inputs.py
python scripts/audit_derived_inputs.py
python -m pytest -q
```

Commit the finalized metadata. Create tag `v0.3.2` and a GitHub release.

## 5. Build and upload the immutable archive

```bash
python scripts/build_release_archive.py
```

Upload `dist/ensitrelvir-pep-cea-v0.3.2.zip` to the reserved Zenodo draft. Confirm resource type Software, open access, MIT license, version 0.3.2, English language, author order, ORCID iDs, and related GitHub identifiers. Zenodo records a checksum automatically after upload. Then publish the record.

## 6. Update manuscript files

Insert the final GitHub release URL and Zenodo DOI into the manuscript, title page, supplement, and medRxiv preprint PDF before submission. All citations must refer to the same versioned Git tag and Zenodo DOI. A separate checksum citation is unnecessary.
