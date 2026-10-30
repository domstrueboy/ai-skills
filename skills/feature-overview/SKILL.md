---
name: feature-overview
description: >-
  Build a reading guide (.md with embedded mockup images) for a new product
  section before implementing it: what to build, screen by screen, from the
  tickets, the written spec (Confluence or similar) and the Figma mockups,
  plus every conflict and open point between them. Optionally a translated
  copy. Use when the user asks for an overview, a summary or "the whole
  picture" of an upcoming section/epic/feature, wants the mockups and the spec
  in one document, or invokes /feature-overview.
---

# Feature overview: the whole picture before coding

The reader is the developer who will build the section (usually the user). They want to read one document and know: what the section is for, every screen, the rules behind each screen, and what is still unclear. It is a reading guide, not a work plan: no estimates, no code design. If a work plan exists, link to it.

## 0. Inputs

You need three kinds of source. Ask only for what you can't find yourself:
- **Tickets:** the root/epic ticket and its sub-tasks (title, scope, linked designs and spec pages).
- **Spec:** the main spec page, its child pages and the pages it links to (statuses, roles, permissions, audit, import rules…). Note each page's last-updated date: when pages disagree, the newest usually wins on logic.
- **Mockups:** the Figma file and the canvas/section for this feature.

Read the comments on the spec pages too (inline and footer): open comments are often open points.

## 1. Folder layout

Put everything next to the user's plans (ask once if there is no obvious place), outside any code repo:

```
<name>-overview/
  <Name>-overview.md        # built, don't edit by hand
  <Name>-overview.<lang>.md # optional translation, built
  images/NN-short-name.png
  parts/0-intro.md          # written by you
  parts/A-<area>.md …       # one per area, in reading order
  parts/Z-open-points.md    # written last
  parts/_spec-<page>.md     # extracted spec text (skipped by the build)
  parts/<lang>/…            # translated parts, same file names
```

## 2. Collect

1. **Tickets → a table**: ticket, what it covers, dependencies. Note work that the designs or spec contain but no ticket covers.
2. **Spec → `parts/_spec-*.md`**: save the text of each relevant page so later steps (and helper agents) read the file instead of fetching again.
3. **Figma → frame list**: fetch the canvas with a shallow depth first (full node trees are huge). List the frames per area with their node IDs. **Check the node IDs in the tickets**: designs get rebuilt and old links point to deleted nodes; use the current IDs and say which ticket links are stale.
4. **Download the frames as PNG** (scale 1 is enough to read) into `images/`, named `NN-short-name.png`. Number by area in blocks of ten (01–09 shell/dashboard, 10–19 detail, 20–29 dialogs, …) so new frames can slot in. Include every state: menus, dialogs, empty/error states, success screens. If a frame is very tall, export its sub-frames instead.

## 3. Write the parts

**`0-intro.md`**:
- Title and one italic line on what the document is, the date the sources were checked, and a link to the work plan if there is one.
- **Sources**: links to the Figma canvas and every spec page used (mark the newest).
- **The whole thing on one page**: who uses it, what it's for (numbered list of jobs), where it lives in the code, a text **screen map** (an ASCII tree of pages, tabs, menus and dialogs), the ticket table, and work with no ticket.
- **Key ideas**: the concepts every screen depends on: status model and transitions (a table of rules if the spec has one), roles and permissions, categories/types, a glossary of domain words, common UI patterns seen in the mockups, and the backend's current state (what exists, what will be mocked).

**One part per area**, each section `## <TICKET> · <screen or flow>` (or `## No ticket yet · …`), always in this order:
- **What it is:** one or two sentences.
- **Screens:** each image embedded as `![caption](images/NN-name.png)`, followed by bullets describing what is on it: layout, every field, column, button, menu item and state, with the exact labels. Note typos and placeholder data ("spelled like this in Figma"), and write "(unreadable)" rather than guessing.
- **Rules from the spec:** validations, permissions, transitions, error and alternative flows, with section references.
- **Figma vs spec:** every difference and every gap (no design for a state the spec has, or the other way round).

**`Z-open-points.md`**: every open point collected above, numbered, grouped by who can answer it (analyst, designer, backend, the user), each a short bullet with both sides of a conflict. Start with the default you will follow until an answer comes (for example: Figma for layout and visuals, the newest spec page for logic and statuses). End with a "Mockup typos (ignore in the UI)" line.

**Large features:** when there are more than about four areas, give each area to a helper agent in parallel. Give each one: the paths of the spec extracts, the image files for its area with their node IDs, the section template above, and the plain-English style rules below. Write the intro and open points yourself, then read every part: check that the images exist, the labels match the screenshots, and the style is consistent.

## 4. Build and check

```bash
python3 scripts/build_overview.py <overview-dir> <Name>
```

It joins the parts in file-name order (skipping `_*.md`), adds a contents list after the intro, and checks that every image link resolves. Fix any MISSING image. Unused images are listed: embed them or delete them.

## 5. Translation (only when asked)

- Translate each part into `parts/<lang>/` with the same file names, keeping every image link, heading, table and code block in place. Screen maps and labels quoted from the UI stay in the original language.
- **Russian (and other languages the user reads alongside English):** put the English original in parentheses **only for special terms**: finance and regulatory terms and the system's own vocabulary (status, tab, role, category names), at the first mention per section. Don't add it to common, UI or IT words, and don't repeat quoted UI messages in English.
- Build with `--lang <lang> --contents-title "<Contents in that language>"`. The script compares headings, table rows and image links with the base file; fix any MISMATCH.

## 6. Deliver

Give the full paths of the built files, the number of screens and open points, and say how to view it (any Markdown preview, e.g. VS Code's, shows the images). Then sum up in a few lines the biggest open points, and offer to turn them into questions for the people named in `Z-open-points.md`.

## Style

Plain, short sentences in simple English: one idea per sentence, active voice, everyday words. Bullets for lists of things on a screen; tables for rules and comparisons. Describe what is there, don't evaluate the design. No implementation detail beyond "where it lives" and "backend today".
