#!/usr/bin/env python3
"""
md-to-storage.py — reference markdown → Confluence storage XHTML converter.

This is the canonical reference implementation that backs every RuneSmith
skill that publishes to Confluence (feature-doc, architecture-doc, project-
overview, decisions-log, known-issues, roadmap, session-log, bug-report).

The lib doc plugins/runesmith-confluence/lib/confluence-format.md describes
the conversion rules. This script implements them deterministically so skill
behavior doesn't drift over time.

Usage:
    python scripts/md-to-storage.py < input.md > output.xhtml
    python scripts/md-to-storage.py input.md output.xhtml
    cat input.md | python scripts/md-to-storage.py

Supports:
- Headings (h1-h6)
- Paragraphs
- Bold (**text** / __text__)
- Italic (*text* / _text_)
- Inline code (`code`)
- Code blocks (```lang ... ```) → ac:structured-macro code
- Unordered lists (-, *, +)
- Ordered lists (1. 2. 3.)
- Links ([label](url))
- Blockquotes (> ...)
- Horizontal rules (---)
- Tables (| col1 | col2 |)

Does NOT support (use raw storage XHTML for these):
- Confluence info/warning/note panels (handle in skill — wrap output)
- Status lozenges
- Task lists / decision lists
- Embedded media

Idempotent over already-converted XHTML inside ac:plain-text-body CDATA.
"""

import sys
import re
import html


def escape(text):
    """HTML-escape text for storage XHTML body content."""
    return html.escape(text, quote=False)


def convert_inline(text):
    """Apply inline transforms: code, bold, italic, links."""
    # Inline code first (so its content isn't re-processed)
    parts = re.split(r'(`[^`]+`)', text)
    out = []
    for part in parts:
        if part.startswith('`') and part.endswith('`'):
            out.append('<code>' + escape(part[1:-1]) + '</code>')
        else:
            # Links
            part = re.sub(
                r'\[([^\]]+)\]\(([^)]+)\)',
                lambda m: f'<a href="{escape(m.group(2))}">{escape(m.group(1))}</a>',
                part
            )
            # Bold
            part = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', part)
            part = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', part)
            # Italic
            part = re.sub(r'(?<![*\w])\*([^*\n]+)\*(?![*\w])', r'<em>\1</em>', part)
            part = re.sub(r'(?<![_\w])_([^_\n]+)_(?![_\w])', r'<em>\1</em>', part)
            out.append(part)
    return ''.join(out)


def convert(md):
    """Convert markdown string to Confluence storage XHTML."""
    lines = md.split('\n')
    out = []
    i = 0
    in_code = False
    code_lang = ''
    code_buf = []

    while i < len(lines):
        line = lines[i]

        # Code fence
        if line.startswith('```'):
            if not in_code:
                in_code = True
                code_lang = line[3:].strip() or 'text'
                code_buf = []
            else:
                in_code = False
                body = '\n'.join(code_buf)
                out.append(
                    f'<ac:structured-macro ac:name="code">'
                    f'<ac:parameter ac:name="language">{escape(code_lang)}</ac:parameter>'
                    f'<ac:plain-text-body><![CDATA[{body}]]></ac:plain-text-body>'
                    f'</ac:structured-macro>'
                )
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^-{3,}\s*$', line):
            out.append('<hr/>')
            i += 1
            continue

        # Heading
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            text = convert_inline(m.group(2).strip())
            out.append(f'<h{level}>{text}</h{level}>')
            i += 1
            continue

        # Blockquote
        if line.startswith('> '):
            quote_lines = []
            while i < len(lines) and lines[i].startswith('> '):
                quote_lines.append(convert_inline(lines[i][2:]))
                i += 1
            out.append('<blockquote><p>' + '<br/>'.join(quote_lines) + '</p></blockquote>')
            continue

        # Unordered list
        if re.match(r'^[-*+]\s+', line):
            items = []
            while i < len(lines) and re.match(r'^[-*+]\s+', lines[i]):
                items.append(convert_inline(re.sub(r'^[-*+]\s+', '', lines[i])))
                i += 1
            out.append('<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>')
            continue

        # Ordered list
        if re.match(r'^\d+\.\s+', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i]):
                items.append(convert_inline(re.sub(r'^\d+\.\s+', '', lines[i])))
                i += 1
            out.append('<ol>' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>')
            continue

        # Table
        if '|' in line and i + 1 < len(lines) and re.match(r'^\s*\|?[\s:-]+\|', lines[i + 1]):
            header_cells = [c.strip() for c in line.strip().strip('|').split('|')]
            i += 2  # skip header + separator
            rows = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            tbl = '<table><tbody>'
            tbl += '<tr>' + ''.join(f'<th>{convert_inline(c)}</th>' for c in header_cells) + '</tr>'
            for row in rows:
                tbl += '<tr>' + ''.join(f'<td>{convert_inline(c)}</td>' for c in row) + '</tr>'
            tbl += '</tbody></table>'
            out.append(tbl)
            continue

        # Blank line
        if not line.strip():
            i += 1
            continue

        # Paragraph (consume consecutive non-blank, non-special lines)
        para = []
        while i < len(lines):
            cur = lines[i]
            if (not cur.strip() or
                cur.startswith('#') or
                cur.startswith('```') or
                cur.startswith('> ') or
                cur.startswith('- ') or cur.startswith('* ') or cur.startswith('+ ') or
                re.match(r'^\d+\.\s+', cur) or
                re.match(r'^-{3,}\s*$', cur)):
                break
            para.append(convert_inline(cur))
            i += 1
        if para:
            out.append('<p>' + '<br/>'.join(para) + '</p>')

    return '\n'.join(out)


def main():
    if len(sys.argv) == 1:
        md = sys.stdin.read()
        print(convert(md))
    elif len(sys.argv) == 2:
        with open(sys.argv[1], encoding='utf-8') as f:
            md = f.read()
        print(convert(md))
    elif len(sys.argv) == 3:
        with open(sys.argv[1], encoding='utf-8') as f:
            md = f.read()
        with open(sys.argv[2], 'w', encoding='utf-8') as f:
            f.write(convert(md))
    else:
        print("Usage: md-to-storage.py [input.md] [output.xhtml]", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
