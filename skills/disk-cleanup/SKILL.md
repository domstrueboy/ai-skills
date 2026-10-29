---
name: disk-cleanup
description: >-
  Check and reclaim disk space on this dev laptop (Windows host + WSL2 Ubuntu,
  accessed via /mnt/c). Covers Docker/WSL vhdx bloat, npm/build caches,
  Windows Temp, and a generic top-folder size scan that catches whatever app
  (Docker, an IDE, a browser, anything) is currently the biggest offender.
  Use when the user asks about freeing disk space, low storage warnings, or
  "where did my space go".
---

# Disk cleanup (Windows + WSL2 dev laptop)

Machine context: Windows host, primary drive `C:`, user profile
`C:\Users\<you>`. Working environment is WSL2 Ubuntu, reached from here
via `/mnt/c/Users/<you>/...`. Windows-side commands run via
`powershell.exe -NoProfile -Command "..."` from Bash (interop works).

`<you>` below is the Windows user name. Find it first with
`powershell.exe -NoProfile -Command '$env:USERNAME'` and substitute it into
every path before running a command (diskpart needs a literal path anyway).

This skill is meant to be run periodically (whenever space is tight), not
just once. It has two parts: (1) recurring checks for things that reliably
regrow over time, and (2) a generic scan that catches *whatever's* currently
bloated without needing per-app knowledge baked in.

Always start and end with a free-space check so progress is visible:
```powershell
Get-PSDrive C | Select-Object @{N='FreeGB';E={[math]::Round($_.Free/1GB,2)}}
```

## 1. Docker / WSL vhdx bloat (recurring — check this every time)

WSL2 disks (`ext4.vhdx`) and Docker's data disk (`docker_data.vhdx`) grow
but never auto-shrink, even after deleting images/containers/volumes. This
is the one thing on this machine that reliably refills over normal dev use
(pulling/building images, WSL package installs), so it's worth checking
every pass.

Check real Docker usage vs. disk file size:
```bash
docker system df -v
```
Then compare against the actual vhdx file sizes:
```powershell
Get-ChildItem 'C:\Users\<you>\AppData\Local' -Recurse -Filter '*.vhdx' -ErrorAction SilentlyContinue |
  Select-Object FullName, @{N='SizeGB';E={[math]::Round($_.Length/1GB,2)}}
```
Known paths on this machine:
- `C:\Users\<you>\AppData\Local\Docker\wsl\disk\docker_data.vhdx` — Docker's actual image/layer/volume storage (this is the one that bloats).
- `C:\Users\<you>\AppData\Local\Docker\wsl\main\ext4.vhdx` — Docker's engine distro, stays small.
- `C:\Users\<you>\AppData\Local\wsl\{...}\ext4.vhdx` — the Ubuntu dev distro.

If a vhdx is much bigger than what `docker system df` / actual WSL disk usage
justifies, it needs manual compaction. **This cannot be run from inside this
session** — `wsl --shutdown` kills the WSL instance this tool is running in.
Give the user these exact steps to run themselves in a plain Windows
PowerShell window (not WSL) when they're ready to close things out:

```powershell
wsl --shutdown
diskpart
```
then inside diskpart:
```
select vdisk file="C:\Users\<you>\AppData\Local\Docker\wsl\disk\docker_data.vhdx"
attach vdisk readonly
compact vdisk
detach vdisk
exit
```
Repeat with the Ubuntu distro's `ext4.vhdx` path if it's also bloated.

Before suggesting `docker system prune -a --volumes`: check `docker ps -a`
first — containers "Up" and in active use should not be pruned. Only remove
dangling images / stopped containers / volumes with no links, and **ask the
user before removing any volume** (it may hold real database data from
another project — don't assume it's disposable).

Note: this machine's WSL version has sparse VHD (auto-shrink) support, but
it's disabled by Microsoft by default due to a known corruption risk. Do
**not** suggest `--set-sparse --allow-unsafe` — periodic manual compaction is
the safe path here. Don't re-suggest sparse mode unless the user asks again.

## 2. Safe, low-risk caches (recurring, fine to clear proactively)

These regrow from normal work and cost nothing to clear:
```bash
npm cache clean --force          # ~/.npm — safe, just re-downloads on install
```
```powershell
Remove-Item -Path 'C:\Users\<you>\AppData\Local\Temp\*' -Recurse -Force -ErrorAction SilentlyContinue
```
(Temp will report some files still in use / locked — that's normal, skip them.)

## 3. Generic "what's big right now" scan (run every time — catches anything)

Don't hardcode per-app checks for things like Android Studio, Visual Studio,
Claude Desktop, browsers, etc. — those come and go, get reinstalled, or
change size unpredictably. Instead, always run this scan to find whatever is
currently the biggest thing, and investigate whatever surfaces on the spot:

```powershell
Get-ChildItem 'C:\Users\<you>\AppData\Local' -Directory -Force -ErrorAction SilentlyContinue |
  ForEach-Object {
    $size = (Get-ChildItem $_.FullName -Recurse -Force -ErrorAction SilentlyContinue |
      Measure-Object -Property Length -Sum).Sum
    [PSCustomObject]@{Name=$_.Name; SizeGB=[math]::Round($size/1GB,2)}
  } | Sort-Object SizeGB -Descending | Select-Object -First 15 | Format-Table -AutoSize
```
Repeat with `Roaming` instead of `Local`, and with `C:\Users\<you>`
itself (top level: Downloads, Documents, Desktop, `.cargo`, `.rustup`, etc.)
to widen the scan.

If a folder looks surprisingly big, drill into it to find the actual large
file(s) before deciding what to do:
```powershell
Get-ChildItem '<folder>' -Recurse -Force -ErrorAction SilentlyContinue |
  Sort-Object Length -Descending | Select-Object -First 20 FullName,
  @{N='SizeGB';E={[math]::Round($_.Length/1GB,2)}}
```
Then reason about it case by case: is it a cache/vhdx/log (safe to clear or
compact), a real data store (ask before touching), or an app the user no
longer uses (ask before uninstalling)? Don't assume — the whole point of
this generic pass is that the offender changes over time.

## Ground rules

- Never delete anything that holds user data (Docker volumes, Downloads
  contents, project files) without asking first — caches and vhdx slack are
  fair game to clean proactively, data is not.
- Don't run `wsl --shutdown` or anything that would kill this session's own
  WSL instance — hand those steps to the user to run themselves.
- Report a before/after free-space number so the win is concrete.
