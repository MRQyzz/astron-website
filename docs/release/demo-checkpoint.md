# ASTRON — Demo Release Checkpoint

## Purpose

This document records the repository state intended as a stable Space Apps demo checkpoint. It is a checkpoint record, not a claim that a hosted production deployment or a GitHub Release has been created.

## Checkpoint source

- Repository: `MRQyzz/astron-website`
- Working branch: `fix/pre-demo-hardening`
- Checkpoint commit before this documentation update: `652b09a89e49ea220651f638addd16e27c7ec6fe`
- Frontend verification reported by the project owner: `npm install`, `npm run lint`, and `npm run build` completed successfully.
- Backend verification reported by the project owner: `pytest -v` — 53 passed.
- Manual integration verification reported by the project owner: core application workflows were tested and reported working.

## Known limitations

- IRSA SIA2 remote observation search previously returned HTTP 502 from the IRSA proxy, including when its query URL was tested directly. Treat remote IRSA availability as an external dependency and use the local FITS demo path if it is unavailable.
- The frontend production build reports a JavaScript bundle of approximately 2.9 MB after minification, above Vite's 500 kB advisory threshold. The build succeeds; code splitting is a post-demo optimization.
- No license file is currently included. Do not imply that the repository has an explicit open-source reuse license.

## Freeze policy

After this checkpoint:
1. Avoid feature additions immediately before the demo.
2. Accept only fixes that address a reproducible demo-blocking issue.
3. For every accepted change, rerun frontend lint/build, backend tests, and the affected manual integration workflow.
4. Keep FITS samples, local environment files, credentials, and generated artifacts out of version control.
5. Update this record if the checkpoint commit changes.

## Create a local annotated tag

After pulling the documentation commit and confirming the working tree is clean, create the tag locally:

```powershell
git tag -a astron-space-apps-demo-v1 -m "ASTRON Space Apps demo checkpoint"
git push origin astron-space-apps-demo-v1
```

If the tag already exists, inspect it before changing anything; do not force-update a published tag casually.
