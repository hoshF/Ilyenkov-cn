---
title: "B. M. Kedrov Philosophy Text Archive"
created: "2026-06-11"
type: "project"
tags: ["kedrov", "philosophy", "russian", "source-archive"]
language: "zh"
collection: "project-documentation"
llm_wiki_eligible: "true"
gbrain_source: "project-markdown"
---

# 凯德洛夫哲学文本资料库

本目录保存博尼法季·米哈伊洛维奇·凯德洛夫（Б. М. Кедров）的哲学文本和来源元数据。

## 当前内容

- `kedrov_md/russian_web/royallib/`：从 RoyalLib 真实 HTML 转换的俄文 Markdown。
- `kedrov_md/russian_web/royallib/assets/`：HTML 压缩包中的正文插图。
- `source_scans/`：自由直接下载的未处理 PDF/DjVu 源扫描件，不进入正文或 GBrain。
- `metadata/royallib_manifest.json`：来源 URL、源文件哈希、输出文件和转换状态。
- `metadata/source_scans_manifest.json`：源扫描件的版本、URL、哈希与权利状态。
- `scripts/kedrov_royallib_convert.py`：可复现的 HTML 下载和转换脚本。

当前第一批文本：

- `Беседы о диалектике`
- `О «Диалектике природы» Энгельса`
- `О творчестве в науке и технике`

## 来源政策

本目录遵循仓库的[哲学文本来源与格式政策](../notes/PHILOSOPHY_SOURCE_FORMAT_POLICY.md)：

- 优先从真实 HTML 或原生结构化 EPUB 生成 Markdown。
- 项目当前不执行新的 OCR，也不使用 DjVuTXT、ABBYY、hOCR 或 PDF 文本层生成正文。
- 自由可下载的 PDF/DjVu 保存到 `source_scans/` 并标记为未处理；受控借阅只登记书目。

RoyalLib 页面没有提供明确的开放许可证。生成文件保留 `source_license: "not_stated"` 和 `redistribution_approved: "false"`，当前用于研究、检索和来源评估，不视为校勘定本。

## 重新生成

```bash
python3 kedrov_markdown/scripts/kedrov_royallib_convert.py
```

检查远端 HTML 是否仍能生成相同正文：

```bash
python3 kedrov_markdown/scripts/kedrov_royallib_convert.py --check
```
