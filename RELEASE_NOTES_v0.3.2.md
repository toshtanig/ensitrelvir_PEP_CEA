# Release notes v0.3.2

This is a documentation and public-release workflow patch. The model equations, parameter values, random seed, and numerical results are unchanged from v0.3.1.

Changes:

- clarified that SHA-256 checksums are optional integrity checks for immutable release archives, not identifiers for editable working files;
- removed checksum generation from the routine analysis workflow;
- made checksum sidecar generation optional in `build_release_archive.py`;
- updated AHEHP submission-format documentation; and
- retained Git tags and the Zenodo DOI as the primary persistent identifiers for the public computational record.
