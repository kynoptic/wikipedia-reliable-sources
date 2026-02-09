---
trigger: glob
description: "MECE-first documentation classification and structure with secondary Diátaxis alignment."
globs: ["docs/**", "guides/**", "reference/**", "handbook/**"]
---
# Mece-first documentation classification and structure

## Objectives

- Eliminate overlap and gaps using a strict **MECE** pass first.
- Align each document secondarily to **Diátaxis** for reader intent and navigation.
- Enforce single-purpose documents.

## Core rules

- **Single mece area per document (required).**
  A doc must belong to exactly one MECE area from your information architecture (IA). Example IA (adapt/extend to your product):
  - *Getting started*
  - *Tasks and operations*
  - *Configuration*
  - *APIs and schema*
  - *Concepts and architecture*
  - *Troubleshooting and known issues*
  - *Release notes and changes*

- **Optional diataxis tag (secondary).**
  After MECE assignment, docs should address one of the four areas: `tutorial`, `how-to`, `reference`, or `explanation`.

- **Strict single-purpose rule.**
  If a file spans multiple MECE areas or multiple Diátaxis types, split it. Cross-link, don't mix.

- **Alert usage guidelines.**
  Use GitHub Markdown Alerts (NOTE, TIP, IMPORTANT, WARNING, CAUTION) following hierarchy: WARNING > IMPORTANT > CAUTION > NOTE > TIP. Syntax: `> [!TYPE]` with exact capitalization. Limit to 1-2 alerts per document section for maximum impact.

- **Formatting standards enforcement.**
  Apply consistent formatting: sentence case headings, backtick wrapping for code/paths/commands, proper markdown structure, strategic alert placement, and optional illustrative emojis for navigation signposts (🚀 Getting started, 📋 Prerequisites, etc.).
