# -*- coding: utf-8 -*-

"""Align the GO with the Bioregistry."""

import json
from typing import Any, Dict, Mapping

from bioregistry.align.utils import Aligner
from bioregistry.constants import DATA_DIRECTORY
from bioregistry.external import get_go

__all__ = [
    "GoAligner",
]

PROCESSING_GO_PATH = DATA_DIRECTORY / "processing_go.json"


class GoAligner(Aligner):
    """An aligner for the Gene Ontology (GO) registry."""

    key = "go"
    getter = get_go
    curation_header = "name", "description"

    def get_skip(self) -> Mapping[str, str]:
        """Get the skipped GO identifiers."""
        with PROCESSING_GO_PATH.open() as file:
            j = json.load(file)
        return j["skip"]

    def prepare_external(
        self, external_id: str, external_entry: Mapping[str, Any]
    ) -> Dict[str, Any]:
        """Prepare GO data to be added to the bioregistry for each GO registry entry."""
        rv = {
            "name": external_entry["name"],
        }

        description = external_entry.get("description")
        if description:
            rv["description"] = description

        homepages = [
            homepage
            for homepage in external_entry.get("generic_urls", [])
            if not any(
                homepage.startswith(homepage_prefix)
                for homepage_prefix in [
                    "http://purl.obolibrary.org",
                ]
            )
        ]
        if len(homepages) > 1:
            print(external_id, "multiple homepages", homepages)
        if homepages:
            rv["homepage"] = homepages[0]

        entity_types = external_entry.get("entity_types", [])
        if len(entity_types) > 1:
            print(external_id, "multiple entity types")
            # TODO handle
        elif len(entity_types) == 1:
            entity_type = entity_types[0]
            formatter = entity_type.get("url_syntax")
            if formatter and not any(
                formatter.startswith(formatter_prefix)
                for formatter_prefix in [
                    "http://purl.obolibrary.org",
                    "https://purl.obolibrary.org",
                ]
            ):
                formatter = formatter.replace("[example_id]", "$1")
                rv["formatter"] = formatter

        if "synonyms" in external_entry:
            rv["synonyms"] = external_entry["synonyms"]

        return rv

    def get_curation_row(self, external_id, external_entry):
        """Prepare curation rows for unaligned GO registry entries."""
        return [external_entry["name"], external_entry.get("description")]


if __name__ == "__main__":
    GoAligner.align()
