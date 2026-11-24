# AGENTS.md

Instructions for coding agents working in this repository. `CLAUDE.md` only imports this file.

Developer-specific settings (the local path of the clone) are in the untracked file @AGENTS.local.md.

## Project

**pycohortflow** draws cohort flow diagrams (CONSORT / PRISMA style) with Matplotlib and ships a
browser-based Interactive Generator with its documentation. Distributed on PyPI, archived on Zenodo,
licensed EUPL-1.2.

- `src/pycohortflow/` – the package: `cfd.py` (`plot_cfd`), `cfd_util.py` (colour, text and config
  helpers), `export.py` (`export` → `.cohort.json` + `.style.toml`), `__init__.py` (public API,
  `plot_and_export`, `__version__`), `styles/` (built-in TOML styles `white`, `colorful`, `minimal`).
- `tests/` – pytest suite; uses the Matplotlib `Agg` backend, runs headless.
- `examples/example_cfd.ipynb` – example notebook.
- `docs/` – Sphinx documentation (pydata theme); the Interactive Generator is plain JavaScript in
  `docs/_static/js/`.
- `scripts/sync_roadmap.py` – copies the roadmap from `docs/roadmap.rst` into `README.md`.
- `paper/` – Quarto sources of the OSF preprint.

### Commands

- Install with all extras: `pip install -e ".[dev,docs]"`
- Install pre-commit (once, standalone, not in the extras): `uv tool install pre-commit && pre-commit install`
- Unit tests (as in CI): `pytest -v`
- Execute the example notebook: `pytest --nbmake examples/`
- Lint and the other hooks (as in CI): `pre-commit run --all-files`
- Ruff fixes and formatting: `pre-commit run --hook-stage manual ruff-fix --all-files` ("Failed" means
  files were changed – review the diff)
- Docs: `sphinx-build -b html docs docs/_build/html`
- Roadmap in sync: `python3 scripts/sync_roadmap.py --check`

### Conventions

- Supported Python: 3.10–3.14 (`requires-python = ">=3.10"`). Keep the CI test matrix, the classifiers
  in `pyproject.toml`, the Ruff `target-version`, "Requirements" in `README.md` and
  `docs/development.rst` in step.
- Ruff: line length 100, rules `E F W I N D` (docstrings are linted). Lint scope is `src/` and `tests/`
  only; `examples/`, `scripts/` and `docs/` have known lint debt – do not widen the scope.
- Ruff is pinned once: `rev:` in `.pre-commit-config.yaml` (commit hooks, CI and the manual `ruff-fix`).
  Do not add Ruff to the `dev` extras or run an unpinned `ruff`. Dependabot (`.github/dependabot.yml`)
  opens monthly pull requests for the hook revisions and the GitHub Actions.
- Docs, docstrings and comments use British spelling (colour, customise).
- The built-in styles exist twice: `src/pycohortflow/styles/*.toml` (package) and
  `docs/_static/styles/*.toml` (Interactive Generator). Both are identical – change them together.
- The roadmap is maintained in `docs/roadmap.rst`; `README.md` is generated from it by
  `scripts/sync_roadmap.py` (pre-commit hook). Never edit the roadmap in `README.md` by hand.
- Notebooks are committed without outputs (`nbstripout` hook).
- `CHANGELOG.md` follows Keep a Changelog: new entries go under `## [Unreleased]`.
- The package version lives only in `pyproject.toml` (`__version__` is read via `importlib.metadata`).
  A release also updates `CITATION.cff`, `.zenodo.json` and `paper/paper.md`; release steps are in
  `docs/development.rst` ("Publishing to PyPI", "Git Tags").

## Git – non-negotiable

- **Never** run a git command that changes the repository on your own – under no circumstances: no `commit`,
  `push`, `tag`, pull request or `merge`, no new branch, and nothing that deletes, discards or rewrites: `reset`,
  `rebase`, `restore`, `checkout -- <file>`, `clean`, `stash drop`, `git rm`, deletion of branches or tags, force
  push. Deleting a file, branch or tag is the developer's step: output the command.
- Read-only commands are allowed, e.g. `status`, `log`, `diff`, `show`, `grep`, `branch --show-current`, and
  `fetch` (it updates only the remote-tracking branches, never a local branch or the working tree).
- Dry runs are allowed in a throw-away copy outside the clone (e.g. a scratch folder): an extract made with
  `git archive`, or a clone whose remote is removed (`git remote remove origin`) before any other command.
  Git commands there change only that copy; nothing is pushed from it, and changes reach the work branch
  only as uncommitted file changes.
- Small changes go directly on `main`; a big shift (e.g. a larger feature or a refactor across several
  modules) gets a work branch (see "Session start") – if unsure, ask. Leave changes uncommitted.
- Every bash block for the developer starts with `cd <path of the clone> &&`.
- Only when the developer asks (exception: the branch command of the session start): output the bash
  commands to commit and push – on a work branch also to open the pull request and merge. The developer
  runs them.
- If `main` accepts only signed commits, the commit in these commands is followed by the signature check
  `git log --format='%h %G? %s' origin/main..HEAD`: every line must show `G`. If a line shows another letter
  (`N` = no signature), the branch is not pushed as it is: output the fix that puts its changes into one new
  signed commit – `git reset --soft "$(git merge-base origin/main HEAD)" && git diff --cached --stat`, then,
  after the developer has checked that list, `git commit -S -m "<message>"`; a branch that was pushed before
  is then pushed with `--force-with-lease`. With SSH signatures, `G` needs an allowed-signers file
  (`gpg.ssh.allowedSignersFile`) with the key: `U` means the key is missing from the file, `N` with an error
  about `gpg.ssh.allowedSignersFile` means no file is configured – then the file is set up, not the commit redone.
- Commit messages: **Conventional Commits** – `type(scope): subject (#issue)`.
  Types: feat, fix, docs, test, refactor, chore, ci, build, perf.
- Commit messages and pull-request descriptions carry no attribution: no `Co-Authored-By` line, no
  "Generated with …" line, no other note on AI involvement.
- Versioning: **Semantic Versioning**, starting at `0.1.0`. Propose the bump (major = incompatible change;
  minor = compatible new function; patch = bug fix; during 0.x an incompatible change increments minor) –
  do not create the tag.

### Session start

1. Check the branch: `git status`, `git branch --show-current`.
2. On `main`: small changes are made directly on `main`. For a big shift, make no change yet: output the
   command for a new work branch, with the topic for the developer to fill in, and wait until the developer
   has run it:
   `cd <path of the clone> && git pull --ff-only && git switch -c <type>/<issue>-<topic>` – `<type>` as in the
   commit messages; without `<issue>-` while there is no issue.
3. On a work branch: continue there. A new branch is needed per topic, not per session; a continued session
   (e.g. after a compaction) stays on its branch.
4. Report uncommitted changes you did not make; never overwrite them.
5. The local path of the clone for each developer is in `AGENTS.local.md` (untracked, listed in `.gitignore`,
   never committed). If that file is missing or names no path for the developer you work for, ask for it and
   add it there.
