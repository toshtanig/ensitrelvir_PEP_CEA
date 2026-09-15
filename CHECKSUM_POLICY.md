# Checksum policy

SHA-256 is an optional integrity check for an immutable release archive. It is not a substitute for a Git commit, release tag, or DOI.

Do not calculate or cite a checksum while files are still being edited. Any byte-level change, including a manual edit to a Word document or metadata file, will change the checksum. This is expected.

Recommended workflow:

1. Complete all code, data, documentation, and metadata edits.
2. Commit the final state and create a version tag.
3. Build the release archive with `python scripts/build_release_archive.py`.
4. Upload that exact archive to Zenodo and publish the record.
5. Use the Git tag and Zenodo DOI as the citable identifiers.
6. Only when an independent byte-for-byte verification is useful, run `python scripts/build_release_archive.py --checksum` and retain the generated `.sha256` file locally or attach it to the GitHub release. It does not need to be submitted to the journal or uploaded to Zenodo.

After any substantive edit, create a new commit and, if the public release has already been published, a new version. Do not overwrite the meaning of an existing DOI-linked version.

Submission packages do not include `.sha256` sidecar files. Generate one only after the final archive has been frozen and only when a recipient specifically needs byte-for-byte verification.
