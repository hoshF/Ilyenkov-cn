---
title: "GBrain 关系抽取诊断"
created: "2026-06-11"
updated: "2026-06-11"
type: "audit"
tags: ["gbrain", "extraction", "diagnosis"]
language: "zh"
collection: "project-documentation"
llm_wiki_eligible: "true"
---

# GBrain 关系抽取诊断

## 结论

当前 GBrain `0.42.37.0` 的默认 extraction 是确定性解析，不会从俄文、中文、荷兰文或拉丁文哲学正文中推断概念关系。它主要处理 Markdown 内链、front matter 引用和时间线格式。因此本仓此前得到 0 条链接、0 条时间线，主要原因是正文缺少可解析的内部链接，而不是语言识别失败。

本轮不新增或硬凑哲学关系 schema。后续只有两个合理选项：

1. 专门设计并验证适合哲学语料的关系 schema，再启用语义抽取。
2. 暂停关系抽取，把资源集中在 embedding、关键词检索、混合检索和人工来源校勘。

## 版本与源码证据

```text
$ gbrain --version
gbrain 0.42.37.0
```

安装源码：`/Users/hoshf/.bun/install/global/node_modules/gbrain/src/commands/extract.ts`

- 文件头明确说明 extraction 使用纯确定性正则，不产生 LLM 成本。
- `extractMarkdownLinks` 解析 Markdown 链接。
- `extractFrontmatterLinks` 解析 front matter 引用。
- `extractTimelineFromContent` 解析时间线格式。
- `extract --stale` 从数据库重做上述链接和时间线抽取。

这些证据只说明当前安装版本的默认行为，不代表 GBrain 永远不支持其他抽取模式。

## 隔离样本

测试目录只包含 `alpha.md`、`beta.md`，其中 Alpha 使用真实内部链接 `[Beta](beta.md)`。

```bash
gbrain extract links --source fs --dir "$tmp" --dry-run --json
```

原始输出：

```text
[extract.links_fs] start
[extract.links_fs] 2/2 (100%)
[extract.links_fs] 2/2 (100%) done
{
  "links_created": 1,
  "timeline_entries_created": 0,
  "pages_processed": 2
}
```

该结果证明解析器能确定性识别可解析的 Markdown 内链。

## 全仓结果

切章和 full sync 后运行：

```bash
gbrain extract --stale --catch-up --json
```

结果：

```json
{"action":"extract_stale_done","links_created":0,"timeline_created":0,"pages_processed":373,"stale_remaining":0,"budget_hit":false}
```

0 条结果与隔离样本不矛盾：当前 373 个有正文的导入页面没有形成可解析、可解析到目标页面的内部链接或时间线条目。

## dist 目录差异

本版本的 filesystem extraction walker 源码会检查嵌套 `.git` 指针，但 full-sync 与 lint 实测仍扫描 `dist/public`。本仓因此使用 `scripts/run_gbrain_without_dist.sh`：命令运行期间把已忽略的 `dist/` 临时改为点目录，并通过 `trap` 恢复。包装后的 full-sync dry-run 为 651 页，未包装时为 680 页，差值正好是公开导出中的 29 个 Markdown。

