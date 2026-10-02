"""Regression checks for template enforcement and fenced-example handling."""
from pathlib import Path
import tempfile
import unittest

from check_docs import LEGACY_STATUS, ROOT_FILES, validate

GUIDE = '''# Example

> **Applies to:** General concepts
> **Last reviewed:** 2026-10-02

Inspect a small example system.

## Safety

Inspect before changing state.

## Quick reference

### Example commands

```text
# An example title, not a document heading
## An example section, not a document section
show state
```

## Troubleshooting workflow

1. Confirm scope.
2. Inspect state and compare configuration.
3. Correct, verify, and record rollback state.

## Official references

- [Official documentation](https://example.com/docs)
'''


class DocumentationChecks(unittest.TestCase):
    def check(self, guide=GUIDE, readme='# Repository\n'):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ROOT_FILES:
                (root / name).write_text(readme if name == 'README.md' else '# Project documentation\n')
            docs = root / 'docs' / 'linux'
            docs.mkdir(parents=True)
            (docs / 'example.md').write_text(guide)
            return validate(root)[0]

    def test_valid_sheet_ignores_headings_in_fences(self):
        self.assertEqual(self.check(), [])

    def test_legacy_status_is_accepted_without_false_review_date(self):
        metadata = '> **Applies to:** General concepts\n> **Last reviewed:** 2026-10-02'
        self.assertEqual(self.check(GUIDE.replace(metadata, LEGACY_STATUS)), [])

    def test_missing_metadata_is_rejected(self):
        self.assertTrue(any('below the title' in e for e in self.check(GUIDE.replace('> **Applies to:** General concepts\n> **Last reviewed:** 2026-10-02', ''))))

    def test_invalid_date_is_rejected(self):
        self.assertTrue(any('invalid review date' in e for e in self.check(GUIDE.replace('2026-10-02', '2026-02-30'))))

    def test_section_order_is_enforced(self):
        self.assertTrue(any('required H2 sections' in e for e in self.check(GUIDE.replace('## Safety', '## Quick reference', 1))))

    def test_scope_is_required(self):
        self.assertTrue(any('scope paragraph' in e for e in self.check(GUIDE.replace('Inspect a small example system.', ''))))

    def test_empty_section_is_rejected(self):
        self.assertTrue(any('Safety cannot be empty' in e for e in self.check(GUIDE.replace('Inspect before changing state.', ''))))

    def test_official_reference_is_required(self):
        self.assertTrue(any('authoritative HTTPS link' in e for e in self.check(GUIDE.replace('- [Official documentation](https://example.com/docs)', 'Use official documentation.'))))

    def test_extra_h1_is_rejected(self):
        self.assertTrue(any('exactly one H1' in e for e in self.check(GUIDE + '\n# Another title\n')))

    def test_missing_language_is_rejected(self):
        self.assertTrue(any('language identifier' in e for e in self.check(GUIDE.replace('```text', '```'))))

    def test_unclosed_fence_is_rejected(self):
        self.assertTrue(any('unclosed code fence' in e for e in self.check(GUIDE + '\n```text\nunclosed\n')))

    def test_tilde_fence_and_longer_fence_preserve_embedded_examples(self):
        for marker in ('~~~~', '````'):
            with self.subTest(marker=marker):
                embedded = f'{marker}markdown\n```text\n# Embedded title\n```\n{marker}'
                self.assertEqual(self.check(GUIDE.replace('```text\n# An example title, not a document heading\n## An example section, not a document section\nshow state\n```', embedded)), [])

    def test_mermaid_declaration_is_checked(self):
        self.assertTrue(any('Mermaid declaration' in e for e in self.check(GUIDE.replace('```text', '```mermaid'))))

    def test_relative_links_and_fragments_are_validated(self):
        self.assertEqual(self.check(readme='# Repository\n\n[Example](docs/linux/example.md#example-commands)\n'), [])
        self.assertTrue(any('missing heading fragment' in e for e in self.check(readme='# Repository\n\n[Missing](docs/linux/example.md#missing)\n')))
        self.assertTrue(any('missing local link target' in e for e in self.check(readme='# Repository\n\n[Missing](docs/linux/missing.md)\n')))


if __name__ == '__main__':
    unittest.main()
