# My AI skills

Personal skills in the open Agent Skills format: one folder per skill, each with a `SKILL.md`. They work in Claude Code and in other tools that read `SKILL.md` skills.

| Skill | What it does |
|---|---|
| `monthly-summary` | Turns a month of worklogs into a short list for my manager, ready to paste into Telegram |
| `disk-cleanup` | Finds and frees disk space on a Windows + WSL2 laptop |

## Install on a new machine

```bash
git clone <this repo> ~/ai-skills
mkdir -p ~/.claude/skills ~/.agents/skills
for s in ~/ai-skills/skills/*/; do
  name=$(basename "$s")
  ln -s "$s" ~/.claude/skills/"$name"   # Claude Code
  ln -s "$s" ~/.agents/skills/"$name"   # shared folder other agents read
done
```

Other tools may use their own folder (for example `~/.codex/skills`, `~/.copilot/skills`, `~/.gemini/skills`). Check the tool's documentation and add a link the same way.

If a tool doesn't follow symlinks, copy the folders instead.

### Windows tools

Tools installed on Windows (not in WSL) read `%USERPROFILE%\.claude\skills` and `%USERPROFILE%\.agents\skills`. Link each skill there with a junction (no admin rights needed), from `cmd`:

```bat
for /d %s in (%USERPROFILE%\projects\ai-skills\skills\*) do (
  mklink /J "%USERPROFILE%\.claude\skills\%~nxs" "%s"
  mklink /J "%USERPROFILE%\.agents\skills\%~nxs" "%s"
)
```

Create the two `skills` folders first if they don't exist.

## Rules for this repo

- No employer details: no company or product names, internal URLs, ticket IDs, credentials or colleagues' names.
- Edit skills here, then commit and push, so the backup stays current.
