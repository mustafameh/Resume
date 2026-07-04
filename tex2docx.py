#!/usr/bin/env python3
"""Preprocess the RenderCV-style main.tex so pandoc produces a clean,
parser-friendly resume.docx. Layout-only macros (paracol two-column
entries, adjustwidth margins, the fontawesome external-link arrow) are
neutralized so their arguments stop leaking into the Word text and all
hyperlinks convert to real links. main.tex itself is never modified;
this writes a throwaway _pp.tex that pandoc consumes.
"""
import subprocess
import sys

SRC = "main.tex"
TMP = "_pp.tex"
OUT = "resume.docx"

# Neutralize the \href redefinition that appends the faExternalLink arrow.
# Restoring pandoc-native \href makes every link (header + body) convert.
HREF_LINE = r"\renewcommand{\href}[2]{\hrefWithoutArrow{#1}{\ifthenelse"

# Overrides injected right before \begin{document}: collapse the custom
# layout environments to no-ops so paracol's column count and adjustwidth's
# margin values (e.g. "0.2 cm + 0.00001 cm") stop appearing as body text.
OVERRIDES = r"""% ---- pandoc/docx overrides (injected by tex2docx.py) ----
\renewenvironment{onecolentry}{}{}
\renewenvironment{twocolentry}[2][]{#2\par}{}
\renewenvironment{header}{}{}
\renewcommand{\hrefWithoutArrow}[2]{\href{#1}{#2}}
\renewcommand{\color}[1]{}% keep link/header text visible (drop color switch)
\renewcommand{\placelastupdatedtext}{}
% ---------------------------------------------------------
\begin{document}"""


def main() -> int:
    with open(SRC, encoding="utf-8") as fh:
        lines = fh.readlines()

    out = []
    for line in lines:
        if line.lstrip().startswith(HREF_LINE):
            out.append("% href redefinition removed for pandoc/docx\n")
        else:
            out.append(line)
    text = "".join(out).replace(r"\begin{document}", OVERRIDES, 1)

    with open(TMP, "w", encoding="utf-8") as fh:
        fh.write(text)

    pandoc = sys.argv[1] if len(sys.argv) > 1 else "pandoc"
    return subprocess.call([pandoc, TMP, "-f", "latex", "-t", "docx", "-o", OUT])


if __name__ == "__main__":
    raise SystemExit(main())
