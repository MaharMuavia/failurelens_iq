# Git History Cleanup

Use this only before final submission and only if you are working solo.

## Safe Rule

If the branch has already been shared with teammates or reviewers, prefer one final clean commit instead of rewriting history.

Recommended final commit message if avoiding force-push:

```powershell
git commit -m "feat: finalize judge-ready FailureLens IQ demo"
```

## Inspect History

```powershell
git log --oneline
```

## Backup Before Rebase

```powershell
git checkout -b backup-before-rebase
git checkout main
```

## Solo Cleanup

```powershell
git rebase -i --root
git push --force-with-lease
```

## Example Semantic Commits

- `feat: implement multi-agent reasoning pipeline`
- `feat: add Microsoft IQ status endpoint`
- `feat: add animated agent trace dashboard`
- `fix: harden CORS and API key auth`
- `docs: add final demo and submission guide`
