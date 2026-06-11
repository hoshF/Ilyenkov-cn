---
title: "translation_workspace"
created: "2026-06-11"
type: "project"
tags: ["translation", "workspace"]
language: "zh"
collection: "translation-workspace"
llm_wiki_eligible: "true"
gbrain_source: "project-markdown"
---
# translation_workspace

这里是未来翻译新作品时使用的工作区。当前只建立框架，不放入新翻译。

## 子目录

- `planned/`：待翻译项目登记、优先级和来源说明。
- `drafts/`：初译草稿。每个作品以后单独建立 `<work_slug>/`。
- `reviewed/`：人工读过并初步校订的中文稿。
- `latex_templates/`：从中文稿生成 LaTeX/PDF 时使用的模板和说明。

## 推荐流程

1. 在 `planned/` 记录选题。
2. 从 `../caute_ru_markdown/ilyenkov_md/` 复制或引用俄文 Markdown。
3. 在 `drafts/<work_slug>/` 建立中文初稿。
4. 人工校订后放入 `reviewed/<work_slug>/`。
5. 需要出 PDF 时，再建立独立 LaTeX 工程。

