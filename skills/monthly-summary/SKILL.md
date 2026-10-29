---
name: monthly-summary
description: >-
  Turn the user's month of worklogs (Jira or similar) into a short,
  human-readable list of achievements to send to their manager, often over
  Telegram or another messenger. Use when the user asks for a monthly
  summary, a monthly report, "what I did this month", or invokes
  /monthly-summary, usually with a screenshot or export of their worklog
  table attached.
---

# Monthly work summary for the manager

Audience: the user's manager. They know the products, but they don't want ticket numbers or file-level detail.

## 1. Get the month's work

- **Preferred:** the user attaches a screenshot or export of their worklog table (ticket link, ticket title, worklog text). Read all of it, including rows that are cut off.
- **No attachment:** if a Jira connector is available, search with
  `worklogAuthor = currentUser() AND worklogDate >= startOfMonth() ORDER BY updated ASC`
  (use `startOfMonth(-1)` and `worklogDate < startOfMonth()` if they want last month), then read each issue's title and worklog comments. If that fails or comes back thin, ask for the screenshot instead of guessing.
- Use any notes or memory you have about the user's projects only to explain what a piece of work is about, never to add work that isn't in the worklogs.

## 2. Write the list

- **5-10 items, flat list, no nesting.**
- **No ticket IDs, no ticket links, no file or component names, no numbers of hours.**
- Group by outcome, not by ticket: merge several tickets or days on one feature into a single item, and split one big epic into a few items when it covers clearly separate results (for example, planning, foundation, main screens).
- Each item starts with its **main point in bold** (a short past-tense phrase such as "**Built the account Settings section:**"), followed by one or two plain sentences of detail.
- Plain, everyday English: "Built", "Finished", "Added", "Planned". Spell out product names on first mention; abbreviations the whole team uses are fine.
- Mention open questions raised with backend teams or other teams only when they matter to the manager.
- Order: finished or shipped work first, then work in progress, roughly in the order it happened.

## 3. Deliver

Save two files (in a temporary or scratch folder) and give their full paths:

- `monthly-summary.md` — `- ` bullets, `**bold**` lead-ins.
- `monthly-summary-telegram.txt` — the same text with `• ` instead of `- ` (Telegram doesn't render Markdown lists; it does turn `**bold**` into bold when the message is sent).

Then show the Telegram version in a fenced code block so it's easy to copy. Remind the user in one line to check it in Saved Messages first, and if they still see asterisks there, to make those parts bold with Ctrl+B.

## Example item

```
• **Finished the price calculator for the trading app.** It works out price, interest and yield in both directions, and the result can be carried straight into a new order. I also finished translations and fixes, and raised open questions with the backend team.
```
