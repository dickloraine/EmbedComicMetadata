"""Run with python -m unittest discover -s tests -v (no Calibre needed)."""

import importlib.util
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch


# The metadata model only imports this formatting helper from Calibre's
# plugin namespace. Stub that dependency, not the code being tested.
utils = ModuleType("calibre_plugins.EmbedComicMetadata.utils")
utils.listToString = lambda values: ", ".join(values)
spec = importlib.util.spec_from_file_location(
    "credit_model", Path(__file__).resolve().parents[1] / "metadata/ComicMetadata.py"
)
module = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {utils.__name__: utils}):
    spec.loader.exec_module(module)


class Metadata(module.ComicMetadata):
    def convert_from_native(self):
        pass

    def convert_to_native(self):
        pass

    def read_from_source(self):
        pass

    def write_to_source(self):
        pass

    def remove(self):
        pass


class CreditTests(unittest.TestCase):
    def test_unknown_role_for_existing_person(self):
        metadata = Metadata(None)
        metadata.addCredit("Mike Del Mundo", "Writer")
        metadata.overlayCredits([
            {"person": "Mike Del Mundo", "role": "painter"}
        ], overwrite=False)
        self.assertEqual([c["role"] for c in metadata.credits],
                         ["Writer", "painter"])

    def test_unknown_roles_preserved(self):
        for role in ("painter", "penciller (cover)", "colorist (cover)"):
            with self.subTest(role=role):
                metadata = Metadata(None)
                metadata.addCredit("Example Artist", role)
                self.assertEqual(metadata.credits,
                                 [{"person": "Example Artist", "role": role}])

    def test_unknown_duplicate_updates_primary(self):
        metadata = Metadata(None)
        metadata.addCredit("Example Artist", "painter")
        metadata.addCredit("EXAMPLE ARTIST", "PAINTER", primary=True)
        self.assertEqual(metadata.credits, [
            {"person": "Example Artist", "role": "painter", "primary": True}
        ])

    def test_known_synonyms_unchanged(self):
        metadata = Metadata(None)
        metadata.addCredit("Example Artist", "penciler")
        metadata.addCredit("Example Artist", "PENCILLER", primary=True)
        self.assertEqual(metadata.credits, [
            {"person": "Example Artist", "role": "Penciller", "primary": True}
        ])

    def test_overlay_replaces_only_matching_role(self):
        metadata = Metadata(None)
        metadata.addCredit("Old Artist", "painter")
        metadata.addCredit("Writer", "Writer")
        metadata.overlayCredits([
            {"person": "New Artist", "role": "painter"}
        ], overwrite=True)
        self.assertEqual(metadata.credits, [
            {"person": "Writer", "role": "Writer"},
            {"person": "New Artist", "role": "painter"}
        ])

    def test_missing_role_does_not_crash_add(self):
        metadata = Metadata(None)
        metadata.addCredit("Example Artist", "Writer")
        for role in (None, "", "   "):
            metadata.addCredit("Example Artist", role)
        self.assertEqual(metadata.credits,
                         [{"person": "Example Artist", "role": "Writer"}])


if __name__ == "__main__":
    unittest.main()
