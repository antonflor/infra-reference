#!/usr/bin/env python3
"""Check documentation structure, template metadata, and local links (offline)."""
from datetime import date
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT_FILES = ('README.md', 'CONTRIBUTING.md', 'STYLE_GUIDE.md')
DOMAINS = {
    'networking', 'network-platforms', 'cisco-contact-center', 'cloud',
    'containers', 'kubernetes-platforms', 'automation', 'linux',
    'high-availability', 'development',
}
SECTIONS = ('Safety', 'Quick reference', 'Troubleshooting workflow', 'Official references')
LEGACY_STATUS = '> **Status:** Legacy reference — technical validation pending'
MERMAID = re.compile(
    r'^(flowchart|graph|sequenceDiagram|stateDiagram-v2|classDiagram|erDiagram|'
    r'journey|gitGraph|mindmap|timeline)\b'
)
FENCE = re.compile(r'^\s{0,3}(`{3,}|~{3,})(.*)$')
HEADING = re.compile(r'^(#{1,6}) (.+?)(?: +#+)?$')
LINK = re.compile(r'\[[^\]]*\]\(([^\s)]*)(?:\s+"[^"]*")?\)')


def parse(path, text, errors):
    """Exclude fenced examples from heading, metadata, and link checks."""
    prose = []
    headings = []
    fence = None
    language = ''
    block = []
    opening_line = 0
    for number, line in enumerate(text.splitlines(), 1):
        match = FENCE.match(line)
        if fence is not None:
            if (match and match[1][0] == fence[0]
                    and len(match[1]) >= len(fence) and not match[2].strip()):
                if language == 'mermaid':
                    declaration = next((s.strip() for s in block if s.strip()), '')
                    if not MERMAID.match(declaration):
                        errors.append(f'{path}:{opening_line}: unsupported Mermaid declaration')
                fence = None
            else:
                block.append(line)
            continue
        if match:
            fence = match[1]
            language = match[2].strip()
            block = []
            opening_line = number
            if not language:
                errors.append(f'{path}:{number}: code fence needs a language identifier')
            continue
        prose.append((number, line))
        heading = HEADING.match(line)
        if heading:
            headings.append((number, len(heading[1]), heading[2]))
    if fence is not None:
        errors.append(f'{path}:{opening_line}: unclosed code fence')
    return prose, headings


def anchors(headings):
    """GitHub-style heading fragments, including duplicate-heading suffixes."""
    result = set()
    counts = {}
    for _, _, title in headings:
        title = re.sub(r'<[^>]*>', '', title)
        slug = re.sub(r'[^\w\- ]', '', title.lower()).replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(slug if count == 0 else f'{slug}-{count}')
    return result


def validate(root):
    errors = []
    docs = sorted((root / 'docs').rglob('*.md'))
    files = [root / name for name in ROOT_FILES] + docs
    if not docs:
        errors.append('docs/: no Markdown references found')
    unexpected = sorted(p.name for p in root.glob('*.md') if p.name not in ROOT_FILES)
    if unexpected:
        errors.append('Unexpected root Markdown files: ' + ', '.join(unexpected))
    for path in docs:
        relative = path.relative_to(root / 'docs')
        if relative.parts == ('visual-guides.md',):
            continue
        if len(relative.parts) != 2:
            errors.append(f'{path}: references must use docs/<domain>/<file>.md')
        elif relative.parts[0] not in DOMAINS:
            errors.append(f'{path}: unknown documentation domain')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*\.md', relative.name):
            errors.append(f'{path}: filename must use lowercase kebab-case')
    parsed = {}
    for path in files:
        if not path.is_file():
            errors.append(f'{path}: file is missing')
            continue
        text = path.read_text(encoding='utf-8')
        if not text.strip():
            errors.append(f'{path}: file is empty')
            continue
        if '\x00' in text:
            errors.append(f'{path}: NUL byte found')
        prose, headings = parse(path, text, errors)
        parsed[path] = (prose, headings)
        first = next((line for _, line in prose if line.strip()), '')
        if not first.startswith('# '):
            errors.append(f'{path}: first content line must be an H1')
        if sum(level == 1 for _, level, _ in headings) != 1:
            errors.append(f'{path}: exactly one H1 is required outside code examples')
        previous_level = 0
        for number, level, _ in headings:
            if level > previous_level + 1:
                errors.append(f'{path}:{number}: heading level skips a level')
            previous_level = level
        for number, line in prose:
            if re.search(r'\[[^\]]*\]\(\s*\)', line):
                errors.append(f'{path}:{number}: empty Markdown link')
        if path not in docs:
            continue
        lines = text.splitlines()
        metadata = []
        index = 1
        while index < len(lines) and not lines[index].strip():
            index += 1
        while index < len(lines) and lines[index].startswith('> **'):
            metadata.append(lines[index])
            index += 1
        if metadata != [LEGACY_STATUS]:
            if (len(metadata) != 2 or not metadata[0].startswith('> **Applies to:** ')
                    or not metadata[0].removeprefix('> **Applies to:** ').strip()
                    or not re.fullmatch(r'> \*\*Last reviewed:\*\* \d{4}-\d{2}-\d{2}', metadata[1])):
                errors.append(f'{path}: use Applies to + Last reviewed, or the legacy status, below the title')
            else:
                try:
                    date.fromisoformat(metadata[1].split(':** ', 1)[1])
                except ValueError:
                    errors.append(f'{path}: invalid review date')
        h2 = [(number, title) for number, level, title in headings if level == 2]
        if tuple(title for _, title in h2) != SECTIONS:
            errors.append(f'{path}: required H2 sections in order: {", ".join(SECTIONS)}')
            continue
        scope = [line for number, line in prose if index < number < h2[0][0] and line.strip()]
        if not scope or not any(not line.startswith(('>', '#')) for line in scope):
            errors.append(f'{path}: add a scope paragraph after metadata')
        for i, (start, title) in enumerate(h2):
            end = h2[i + 1][0] if i + 1 < len(h2) else len(lines) + 1
            body = lines[start:end - 1]
            if not any(line.strip() and not line.startswith('#') for line in body):
                errors.append(f'{path}:{start}: {title} cannot be empty')
        reference_start = h2[-1][0]
        if not any(re.search(r'\[[^\]]+\]\(https://[^)]+\)', line)
                   for number, line in prose if number > reference_start):
            errors.append(f'{path}: Official references needs an authoritative HTTPS link')
    # Validate relative paths and heading fragments without making network requests.
    for path, (prose, _) in parsed.items():
        for number, line in prose:
            for match in LINK.finditer(line):
                target = urlsplit(match[1])
                if target.scheme or target.netloc:
                    continue
                destination = (path.parent / unquote(target.path)).resolve() if target.path else path.resolve()
                if not destination.exists():
                    errors.append(f'{path}:{number}: missing local link target {match[1]!r}')
                    continue
                if target.fragment and destination.suffix == '.md':
                    if destination in parsed:
                        destination_headings = parsed[destination][1]
                    else:
                        _, destination_headings = parse(destination, destination.read_text(), [])
                    fragment = unquote(target.fragment)
                    if fragment not in anchors(destination_headings):
                        errors.append(f'{path}:{number}: missing heading fragment {match[1]!r}')
    return errors, len(files), len(docs)


def main():
    errors, file_count, doc_count = validate(Path.cwd().resolve())
    if errors:
        print('\n'.join(errors))
        return 1
    print(f'Validated {file_count} Markdown files across {doc_count} references, including templates and local links.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
