"""
Search for patterns in a jsonlines corpus.

Input:
* Patterns file (file with CATEGORY==REGULAR_EXPRESSION)
* Corpus jsonl (expects text to be stored in an element called 'text')

Usage:
* `python search.py /path/to/patterns.txt /path/to/corpus.jsonl`
    * Outputs: /path/to/corpus.pattern.jsonl
"""
import json
import re
from pathlib import Path


def main(pattern_file: Path, corpus_file: Path, context_length=180, max_window=500):
    """

    Args:
        pattern_file: file with CATEGORY==REGEX (e.g., `JEALOUS==\b(?:jealous|env[yi])\w*\b`)
        corpus_file: file with jsonlines corpus with 'text' as key storing text
        context_length: how much around each match to collect for immediate context

    """
    patterns = []
    with open(pattern_file, encoding='utf8') as fh:
        for line in fh:
            if line := line.strip():
                category, regex = line.split('==', maxsplit=1)
                patterns.append((category, re.compile(regex, re.I | re.MULTILINE)))

    with open(corpus_file.with_suffix('.pattern.jsonl'), 'w', encoding='utf8') as out:
        with open(corpus_file, encoding='utf8') as fh:
            for line in fh:
                data = json.loads(line)
                text = data['text']
                del data['text']
                for category, pattern in patterns:
                    for m in pattern.finditer(text):
                        out.write(json.dumps(data | {
                            'category': category,
                            'precontext': text[max(m.start() - context_length, 0): m.start()],
                            'match': m.group(),
                            'postcontext': text[m.end(): m.end() + context_length],
                            'pretext': text[max(m.start() - max_window, 0): m.start()],  # TODO: configure how much to show
                            'posttext': text[m.end(): m.end() + max_window],  # TODO: configure how much to show
                            'start_index': m.start(),
                            'end_index': m.end(),
                        }) + '\n')


if __name__ == '__main__':
    import sys

    main(Path(sys.argv[1]), Path(sys.argv[2]))
