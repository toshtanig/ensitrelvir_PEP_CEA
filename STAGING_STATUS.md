# Staging status

This archive is ready for repository publication after author and public-identifier metadata are completed.

Expected unresolved fields before finalization:

- Author names, affiliations, and ORCID iDs
- GitHub repository and release URLs
- Reserved Zenodo DOI and draft record URL
- Funding and competing-interest statements
- medRxiv DOI or URL, which can be added after the preprint is posted

Run `python scripts/finalize_release_metadata.py --metadata release_metadata.yml` and then `python scripts/check_release_readiness.py`. The readiness check is expected to fail before these fields are completed and must pass before tag `v0.3.2` is created.
