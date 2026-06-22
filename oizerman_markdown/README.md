---
title: "Teodor Oizerman Philosophy Text Archive / 奥伊泽尔曼哲学文本资料库"
created: "2026-06-16"
updated: "2026-06-22"
type: "project"
tags: ["oizerman", "philosophy", "russian", "source-archive"]
language: "en-zh"
collection: "project-documentation"
llm_wiki_eligible: "true"
gbrain_source: "project-markdown"
---
# Teodor Oizerman Philosophy Text Archive

This collection preserves bibliography, provenance metadata, and unprocessed source scans for
Teodor Ilyich Oizerman (Теодор Ильич Ойзерман, 1914-2017).

See the repository [Source Policy](../notes/PHILOSOPHY_SOURCE_FORMAT_POLICY.md) and
[Oizerman Source Survey](../notes/OIZERMAN_SOURCE_SURVEY.md).

## Layout

```text
oizerman_markdown/
├── README.md
├── bibliography/
│   ├── iphras_official_bibliography.pdf
│   └── iphras_official_bibliography.txt
├── metadata/
│   ├── works_master.json
│   └── source_scans_manifest.json
├── source_scans/
└── oizerman_md/                 # created only when eligible source text exists
```

## Current Status

- 35 unprocessed source scans are registered: 20 DjVu and 15 PDF files, totaling 265,146,055 bytes.
- The four-volume `Теория познания`, edited by Vladislav Lektorsky and Teodor Oizerman, is preserved
  as source PDF: volumes 1 and 2 from 1991, volume 3 from 1993, and volume 4 from 1995.
- The 2014 `Избранные труды: в 5 томах` (Moscow: Наука) is a five-volume selected-works edition. It
  must not be treated as digitally identical to the earlier individual books.
- The collection currently contains bibliography and scans, not searchable Oizerman body text.

## Rights And Handling

Oizerman died in 2017 and his works remain protected. Source files default to
`source_license: "not_stated"`, `rights_review_status: "unreviewed"`, and
`redistribution_approved: "false"`.

- The official bibliography is a factual research tool, not Oizerman's full text.
- PDF/DjVu files remain `source_scan_unprocessed`: no text-layer extraction, OCR, GBrain ingestion,
  or public export.
- Controlled loans, encrypted files, and `printdisabled` materials are bibliography only.
- Translations in English, German, Chinese, or other languages remain separate from the Russian
  works registry.
- Co-authored and edited works record Oizerman's actual responsibility rather than treating every
  title as a sole-authored monograph.

## 中文摘要

本目录保存奥伊泽尔曼的书目、来源元数据和 35 份未处理扫描件，其中包括列克托尔斯基与
奥伊泽尔曼共同主编的四卷本《Теория познания》（1991、1991、1993、1995）。这些扫描件
不等于已数字化正文，不进行 OCR、不进入 GBrain 或公开导出。2014 年五卷本选集与早期单行本
必须保持版本区分。
