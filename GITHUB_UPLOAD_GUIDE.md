# GitHub publication guide

This repository is prepared as a versioned public research-software release. Complete the metadata before making the final release.

## 1. Create the repository

Create an empty GitHub repository named `ensitrelvir-pep-cea` or another stable name. Do not initialize it with a separate README or license because those files are already included here.

## 2. Finalize metadata

Edit `release_metadata.yml` with the actual author order, affiliations, ORCID iDs, repository URL, future release URL, reserved Zenodo DOI, and Zenodo draft record URL.

Run:

```bash
python scripts/finalize_release_metadata.py --metadata release_metadata.yml
python scripts/check_release_readiness.py
```

The readiness check must pass before the public tag is created.

## 3. Verify the model

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/validate_inputs.py
python scripts/audit_derived_inputs.py
python -m pytest -q
python scripts/run_all.py
```

## 4. Push and release

```bash
git init
git add .
git commit -m "Public release v0.3.2"
git branch -M main
git remote add origin REPLACE_WITH_GITHUB_REPOSITORY_URL
git push -u origin main
git tag -a v0.3.2 -m "Ensitrelvir PEP CEA v0.3.2"
git push origin v0.3.2
```

Create a GitHub release from tag `v0.3.2`. A separate checksum attachment is optional and is not needed for journal submission or Zenodo deposition.

## 5. Preserve the exact analysis

Do not alter inputs or results after tagging. Any numerical change requires a new version, rerun, and archive. Documentation-only corrections should also use a new patch version once the release is public.
