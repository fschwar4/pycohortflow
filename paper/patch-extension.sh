#!/usr/bin/env bash
set -euo pipefail
F=_extensions/mikemahoney218/arxiv/partials/before-body.tex
grep -q '\\emph{Keywords}' "$F" || \
  sed -i.bak 's/\\emph Keywords/\\emph{Keywords}/' "$F"

F2=_extensions/mikemahoney218/arxiv/arxiv.sty
grep -q 'vskip 0\.4in \\@minus 0\.1in \\center{\\today}' "$F2" && \
  sed -i.bak 's/vskip 0\.4in \\@minus 0\.1in \\center{\\today}/vskip 0.15in \\@minus 0.05in \\center{\\today}/' "$F2"