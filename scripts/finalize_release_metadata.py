from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def required(value: object, label: str) -> str:
    text = str(value or "").strip()
    if not text or "REPLACE_WITH_" in text:
        raise ValueError(f"Missing required metadata: {label}")
    return text


def doi_url(doi: str) -> str:
    return doi if doi.startswith("https://doi.org/") else f"https://doi.org/{doi}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", default="release_metadata.yml")
    args = parser.parse_args()
    path = Path(args.metadata)
    if not path.is_absolute():
        path = ROOT / path
    meta = yaml.safe_load(path.read_text(encoding="utf-8"))
    release = meta["release"]
    version = required(release["version"], "version")
    date = required(release["date"], "date")
    repo = required(release["github_repository_url"], "GitHub repository URL")
    gh_release = required(release["github_release_url"], "GitHub release URL")
    doi = required(release["zenodo_doi"], "reserved Zenodo DOI").removeprefix("https://doi.org/")
    record = required(release["zenodo_record_url"], "Zenodo record URL")
    medrxiv = str(release.get("medrxiv_url") or "").strip()
    if not medrxiv and release.get("medrxiv_doi"):
        medrxiv = doi_url(str(release["medrxiv_doi"]))
    if not medrxiv:
        medrxiv = "Not yet posted"

    corresponding_email = required(meta.get("manuscript", {}).get("corresponding_author_email"), "corresponding author email")

    authors = meta.get("authors") or []
    if not authors:
        raise ValueError("At least one author is required")
    clean = []
    for i, author in enumerate(authors, 1):
        given = required(author.get("given_names"), f"author {i} given names")
        family = required(author.get("family_names"), f"author {i} family name")
        affiliation = required(author.get("affiliation"), f"author {i} affiliation")
        orcid = str(author.get("orcid") or "").strip().removeprefix("https://orcid.org/")
        if orcid and not re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", orcid):
            raise ValueError(f"Invalid ORCID for author {i}: {orcid}")
        clean.append({"given": given, "family": family, "affiliation": affiliation, "orcid": orcid})

    cff_lines = [
        "cff-version: 1.2.0",
        'message: "If you use this software, please cite the versioned Zenodo record and the accompanying manuscript or preprint."',
        'title: "Ensitrelvir Post-Exposure Prophylaxis Cost-Effectiveness Model for Japan"',
        "type: software",
        f"version: {version}",
        f"date-released: {date}",
        "authors:",
    ]
    for author in clean:
        cff_lines.extend(
            [
                f'  - family-names: "{author["family"]}"',
                f'    given-names: "{author["given"]}"',
                f'    affiliation: "{author["affiliation"]}"',
            ]
        )
        if author["orcid"]:
            cff_lines.append(f'    orcid: "https://orcid.org/{author["orcid"]}"')
    cff_lines.extend(
        [
            f'repository-code: "{repo}"',
            f'url: "{doi_url(doi)}"',
            f'doi: "{doi}"',
            "license: MIT",
            "abstract: >-",
            "  A reproducible Python cost-utility model evaluating ensitrelvir as post-exposure",
            "  prophylaxis for COVID-19 among high-risk household contacts in Japan.",
            "keywords:",
            "  - cost-effectiveness",
            "  - cost-utility analysis",
            "  - ensitrelvir",
            "  - post-exposure prophylaxis",
            "  - COVID-19",
            "  - Japan",
        ]
    )
    (ROOT / "CITATION.cff").write_text("\n".join(cff_lines) + "\n", encoding="utf-8")

    creators = []
    for author in clean:
        entry = {
            "name": f'{author["family"]}, {author["given"]}',
            "affiliation": author["affiliation"],
        }
        if author["orcid"]:
            entry["orcid"] = author["orcid"]
        creators.append(entry)
    related = [
        {"identifier": repo, "relation": "isSupplementTo", "scheme": "url"},
        {"identifier": gh_release, "relation": "isVersionOf", "scheme": "url"},
    ]
    if medrxiv != "Not yet posted":
        related.append({"identifier": medrxiv, "relation": "isSupplementTo", "scheme": "url"})
    zenodo = {
        "title": "Ensitrelvir Post-Exposure Prophylaxis Cost-Effectiveness Model for Japan",
        "upload_type": "software",
        "description": (
            "Versioned Python model, inputs, analyses, tests, and reproducibility outputs "
            "for a cost-utility analysis of ensitrelvir post-exposure prophylaxis among "
            "high-risk household contacts in Japan."
        ),
        "creators": creators,
        "access_right": "open",
        "license": "mit",
        "version": version,
        "publication_date": date,
        "language": "eng",
        "keywords": [
            "cost-effectiveness",
            "cost-utility analysis",
            "ensitrelvir",
            "post-exposure prophylaxis",
            "COVID-19",
            "Japan",
            "reproducible research",
        ],
        "related_identifiers": related,
        "notes": (
            "Severe-outcome and post-acute benefits are model-based extrapolations because "
            "the pivotal prophylaxis trial observed no COVID-19-related hospitalization or death."
        ),
    }
    (ROOT / ".zenodo.json").write_text(json.dumps(zenodo, indent=2) + "\n", encoding="utf-8")

    display_names = ", ".join(f'{author["given"]} {author["family"]}' for author in clean)
    affiliations = "; ".join(dict.fromkeys(author["affiliation"] for author in clean))
    replacements = {
        "{{GITHUB_REPOSITORY_URL}}": repo,
        "{{GITHUB_RELEASE_URL}}": gh_release,
        "{{ZENODO_DOI_URL}}": doi_url(doi),
        "{{MEDRXIV_DOI_URL}}": medrxiv,
        "{{AUTHOR_NAMES}}": display_names,
        "{{AUTHOR_AFFILIATIONS}}": affiliations,
        "{{CORRESPONDING_AUTHOR_EMAIL}}": corresponding_email,
    }
    for rel in ["README.md", "SUBMISSION_AHEHP.md"]:
        target = ROOT / rel
        if target.exists():
            text = target.read_text(encoding="utf-8")
            for token, value in replacements.items():
                text = text.replace(token, value)
            target.write_text(text, encoding="utf-8")

    pyproject = ROOT / "pyproject.toml"
    pyproject_text = pyproject.read_text(encoding="utf-8")
    pyproject_text = pyproject_text.replace("REPLACE_WITH_STUDY_TEAM_OR_AUTHORS", display_names)
    pyproject.write_text(pyproject_text, encoding="utf-8")

    resolved = {
        "version": version,
        "release_date": date,
        "github_repository_url": repo,
        "github_release_url": gh_release,
        "zenodo_doi": doi,
        "zenodo_record_url": record,
        "medrxiv_url": medrxiv,
        "authors": clean,
        "corresponding_author_email": corresponding_email,
    }
    (ROOT / "release_metadata_resolved.json").write_text(
        json.dumps(resolved, indent=2) + "\n", encoding="utf-8"
    )
    print("Release metadata finalized.")


if __name__ == "__main__":
    main()
