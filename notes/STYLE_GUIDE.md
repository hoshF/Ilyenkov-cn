---
title: "翻译风格指南"
created: "2026-06-11"
type: "note"
tags: ["research-note"]
language: "zh"
collection: "research-notes"
llm_wiki_eligible: "true"
gbrain_source: "project-markdown"
---
# 翻译风格指南

本项目当前不追求批量产出，而追求可读、可校、可追溯。

## 基本原则

- 保留原文结构，尽量不重写作者的论证顺序。
- 中文表达要通顺，但不把哲学概念改写成过度现代化的解释性语言。
- 重要概念第一次出现时可保留俄文。
- 原文页码、脚注、出处和版本说明尽量保留。
- 不确定的译法先标记，不在正文中悄悄定稿。

## 文件头建议

以后新翻译 Markdown 可使用如下头部：

```yaml
---
title_ru:
title_zh:
author: Э.В. Ильенков
year:
source_url:
source_file:
source_type:
translation_status: draft
keywords:
---
```

## 翻译状态

- `planned`：已列入计划，尚未翻译。
- `draft`：初译稿，可能由 AI 辅助生成。
- `reviewed`：人工读过并修过明显问题。
- `term_checked`：关键术语已对照术语表统一。
- `latex`：已进入 LaTeX 排版工程。
- `final`：可作为阶段性成品保存。

## LaTeX/PDF 原则

- 只有经过人工校订的文本才进入 LaTeX。
- 每个成书项目保持独立目录，不与俄文原文资料库混放。
- `main.tex` 负责结构，章节文本独立为 `chXX.tex`。
- 编译生成的 `.aux/.log/.toc/.out/.fls/.fdb_latexmk/.synctex.gz` 不作为长期资料保存。
