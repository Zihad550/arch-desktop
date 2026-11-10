# Retired files move to the dotfiles-archive repository

Splitting dotfiles into dotfiles and arch-desktop left two repositories that
retire files, and the `archive/<topic>` branches from
[ADR 0021](0021-retired-setup-files-move-to-an-archive-branch.md) lived only in
dotfiles. They also had never been pushed, so the "named, pushed, listable"
property that decision relied on did not hold.

Decision: retired setup files and configurations move to the
[dotfiles-archive](https://github.com/Zihad550/dotfiles-archive) repository,
one top-level folder per topic, keeping each file's original path inside it.
They are deleted from dotfiles and arch-desktop. The `archive/<topic>`
branches were copied there and deleted.

This supersedes ADR 0021.

## Why

- **One place for both repositories.** A retirement from either repository
  lands in the same archive, and finding it does not depend on knowing which
  repository once owned the file.
- **Browsable without git.** A folder can be opened, searched and linked; a
  branch needs `git show`. ADR 0021 named that cost as the reason it hesitated.
- **The branches were already frozen snapshots of `main`.** Each tip is an
  ancestor of `main`, so deleting the branch names loses no history.

## Consequences

- Links that named a branch now name a folder in dotfiles-archive.
- Older ADRs (0003, 0011, 0015, 0021, 0029) still mention `archive/<topic>`
  branches; read those as folders in dotfiles-archive.
- Archived files stay frozen. Nothing in dotfiles or arch-desktop runs them.
- Each former `archive/<topic>` branch is now the `<topic>/` folder; the
  archive's README lists every topic.
