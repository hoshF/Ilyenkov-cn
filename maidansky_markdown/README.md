---
title: "Andrey Maidansky Academia.edu Source Archive / 迈丹斯基 Academia.edu 源文件资料库"
created: "2026-06-17"
updated: "2026-06-22"
type: "project"
tags: ["maidansky", "philosophy", "source-archive", "academia"]
language: "en-zh"
collection: "project-documentation"
llm_wiki_eligible: "true"
gbrain_source: "project-markdown"
---
# Andrey Maidansky Academia.edu Source Archive

This collection preserves metadata and unprocessed files publicly listed on the Academia.edu
profile of Andrey Dmitrievich Maidansky (Андрей Дмитриевич Майданский).

Source profile: <https://белгу.academia.edu/AndreyMaidansky>

## Layout

```text
maidansky_markdown/
├── README.md
├── metadata/
│   ├── academia_manifest.json
│   ├── academia_manual_queue.json
│   └── source_scans_manifest.json
├── scripts/
│   └── academia_download.py
└── source_scans/academia/
```

## Collection Rules

- Preserve the original PDF or attachment supplied by Academia.edu.
- Do not run OCR, read PDF text layers, or generate Markdown body text.
- Source files default to `source_license: "not_stated"`,
  `rights_review_status: "unreviewed"`, and `redistribution_approved: "false"`.
- Files remain outside the core corpus and GBrain:
  `core_corpus_eligible: "false"` and `llm_wiki_eligible: "false"`.

## Current Status

The June 17, 2026 collection run recorded 57 Academia uploads and registered 56 downloaded entries.
Two work URLs resolve to the same local file,
`spinoza-in-cultural-historical-psychology.pdf`, so the directory contains 55 distinct files.

`metadata/academia_manual_queue.json` retains one unresolved item:
`Культурно историческая психология Истоки и новая реальность`. No usable public source had been
found when the gap was confirmed on June 17, 2026.

## Reproduction

```bash
ACADEMIA_COOKIE_FILE=/Users/hoshf/Project/Ilyenkov/academia_cookie.txt \
python3 maidansky_markdown/scripts/academia_download.py --dry-run

ACADEMIA_COOKIE_FILE=/Users/hoshf/Project/Ilyenkov/academia_cookie.txt \
python3 maidansky_markdown/scripts/academia_download.py
```

`academia_cookie.txt` is a temporary local credential. It is excluded from the repository and
should be deleted after use.

## 中文摘要

本目录保存迈丹斯基 Academia.edu 页面所列作品的元数据和未处理附件。现有记录为 57 项，
已登记 56 项下载结果，对应 55 个实际文件，并保留 1 项未解决缺口。附件不进行 OCR、不进入
核心语料或 GBrain，公开再分发仍需逐文件权利审核。
