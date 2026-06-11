---
title: "凯德洛夫文本收集与处理状态：Claude 交接文档"
created: "2026-06-11"
updated: "2026-06-11"
type: "handoff"
tags: ["kedrov", "handoff", "source-audit", "collection-status", "source-scans"]
language: "zh"
collection: "corpus-metadata"
llm_wiki_eligible: "true"
gbrain_source: "project-markdown"
---

# 凯德洛夫文本收集与处理状态：Claude 交接文档

> 本文只覆盖凯德洛夫子项目。整个仓库的语料、中文工程、版权、GBrain 和 Git 状态请先阅读 [`REPOSITORY_STATUS_FOR_CLAUDE.md`](REPOSITORY_STATUS_FOR_CLAUDE.md)。

## 1. 文档目的

本文是截至 **2026-06-11** 的凯德洛夫（Бонифатий Михайлович Кедров，1903-1985）资料收集交接快照，供 Claude 或其他后续代理直接了解：

- 项目采用什么来源与格式标准；
- 哪些作品已经检索到；
- 哪些文件曾经下载并检查；
- 哪些文件实际保存在当前工作区；
- 哪些文本已经转换为 Markdown；
- 哪些候选因未校验 OCR、受控借阅或重复版本而未进入正文；
- 当前仍需完成哪些工作。

本文只讨论凯德洛夫相关资料。仓库中的伊里因科夫、斯宾诺莎及其他文本不在本次清单范围内。

## 2. 必须遵守的项目处理标准

权威政策文件为 [`PHILOSOPHY_SOURCE_FORMAT_POLICY.md`](PHILOSOPHY_SOURCE_FORMAT_POLICY.md)。后续代理不得自行放宽以下规则。

### 2.1 格式优先级

| 优先级 | 来源类型 | 处理方式 |
|---:|---|---|
| 1 | 真实 HTML 正文 | 清理网页结构，转换为 Markdown |
| 2 | 原生、结构化 EPUB | 按目录和章节解析为 Markdown |
| 3 | 自由直接下载的 PDF | 保存到 `source_scans/`，不提取全文 |
| 4 | 自由直接下载的 DjVu | 保存原件，不使用 DjVuTXT/XML |
| 受控 | 加密、`inlibrary`、`printdisabled` | 只登记书目，不下载、不绕过 |

### 2.2 关键判断规则

1. 文件扩展名不能证明来源合格。EPUB 如果由 hOCR 或自动字符识别生成，仍属于 OCR 派生物；在校验流程建立并通过前不得转换为正文。
2. PDF 即使带有可复制文本层，也只作为 PDF 保存，不从文本层生成 Markdown。
3. 哲学内容优先寻找真实 HTML 或原生 EPUB；找不到时，有 PDF 就保存 PDF。
4. 只有 DjVu 而没有 PDF 时，可以保存自由直接下载的 DjVu 源件，但不从 DjVu 生成文本。
5. AI 总结、人物简介和研究笔记不是原始文献，必须与作者原文分开标记。
6. 可访问、可下载不等于允许公开再分发。来源未声明开放许可时，必须保留 `source_license: "not_stated"` 和 `redistribution_approved: "false"`。

## 3. 当前状态总览

| 项目 | 数量 | 状态 |
|---|---:|---|
| 已生成并保存在当前工作区的凯德洛夫 Markdown 原文 | 3 部、54 章 | 已完成 HTML 转换和可逆切章，尚未与纸质版逐字校勘 |
| 随正文保存在当前工作区的图片 | 28 张 PNG | 全部属于《论科学与技术中的创造》HTML 包 |
| 当前工作区中的凯德洛夫源扫描件 | 6 | 5 PDF、1 DjVu，均为 `source_scan_unprocessed` |
| 当前工作区中的 EPUB | 0 | 未发现合格的原生结构化 EPUB |
| 当前工作区中的源 HTML/ZIP | 0 | 转换时下载，但未长期保存；已记录 URL 和哈希 |
| 被确认是 OCR 派生物而未准入的 EPUB | 1 部 | 《列宁与科学革命》Internet Archive EPUB，不使用 |
| 已入库第二优先级源扫描件 | 6 个 | 总计 140,305,962 字节，完整 manifest 已写入 |
| 仅受控借阅、未下载的法译本 | 1 部 | 只记录书目 |
| 仅检索到书目或扫描下载入口、尚未逐项下载的作品 | 多部 | 见第 9 节 |
| GBrain 现有索引 | 652 页 | embedding 100%，stale 为 0 |
| 已进入 GBrain 的凯德洛夫正文 | 54 章 | 页面已入库，无 oversized 跳过 |

**结论：正文目录中有三部 RoyalLib HTML 转换作品，现存为 54 个可逆章节；另有 6 个源扫描件单独存放在 `source_scans/`，不进入正文或 GBrain。**

## 4. 项目整体目录结构

本仓库不是单一的凯德洛夫项目，而是以伊里因科夫为中心、同时保存相关哲学家原文、中文译本、研究资料和 LLM 索引配置的综合研究仓库。凯德洛夫资料必须留在独立子目录中，不应混入伊里因科夫原著目录。

### 4.1 顶层结构及职责

```text
Ilyenkov/
├── README.md                     # 项目总说明和主要入口
├── CONTRIBUTING.md               # 参与、来源记录和修改规则
├── RESOLVER.md                   # LLM/GBrain 按文本角色选择语料的路由规则
├── LLM_WIKI.md                   # GBrain 索引、同步和检索说明
├── gbrain.yml                    # GBrain 配置
├── TRANSLATION_PLAN.md           # 翻译优先级和候选文本
├── assets/                       # 项目展示图片等公共资源
├── caute_ru_markdown/            # 伊里因科夫原文和迈丹斯基研究资料
│   ├── ilyenkov_md/              # 伊里因科夫俄文来源文本
│   ├── maidansky_md/             # 迈丹斯基及相关二级研究文本
│   ├── metadata/                 # 来源和覆盖审计
│   └── scripts/                  # caute.ru 资料处理脚本
├── kedrov_markdown/              # 凯德洛夫独立资料库，本交接文档的核心对象
├── spinoza_markdown/             # 斯宾诺莎原文、历史见证、PDF 和来源审计
├── existing_translations/        # 已有中文译本和项目编译 PDF
├── translation_workspace/        # 新翻译的计划、草稿、复核和 LaTeX 模板
├── dialectical_logic/            # 《辩证逻辑》中文 LaTeX 工程
├── idols_ideals/                 # 《论偶像与理想》中文 LaTeX 工程
├── notes/                        # 研究笔记、术语、政策和交接文档
└── scripts/                      # 跨项目维护脚本
```

### 4.2 目录之间的文本角色边界

| 目录 | 文本角色 | 凯德洛夫工作中的用途 |
|---|---|---|
| `kedrov_markdown/kedrov_md/` | 凯德洛夫作者原文 | 只放合格 HTML/原生 EPUB 转换的 Markdown |
| `kedrov_markdown/metadata/` | 来源与审计 | 记录 URL、格式、哈希、状态和许可 |
| `kedrov_markdown/scripts/` | 可复现工具 | 下载和转换脚本，不是正文 |
| `notes/` | 项目政策和研究笔记 | 保存来源调查、交接、AI 参考及格式政策 |
| `caute_ru_markdown/ilyenkov_md/` | 伊里因科夫原文 | 可研究伊里因科夫对凯德洛夫的引用和争论，但不是凯德洛夫作品库 |
| `existing_translations/` | 已有中文翻译和辅助 PDF | 不得把译文冒充俄文原文 |
| `translation_workspace/` | 新翻译工作过程 | 将来翻译凯德洛夫时应保留与俄文来源的对应关系 |

`RESOLVER.md` 规定凯德洛夫作品的首选路径是 `kedrov_markdown/kedrov_md/`。GBrain 直接索引现有 Markdown，不复制一套镜像语料；PDF 不进入 GBrain 正文语料。

### 4.3 当前缺少的仓库级许可文件

截至 2026-06-11，在仓库顶层及两层范围内没有发现 `LICENSE`、`LICENSE.md`、`COPYING` 等统一许可文件。不能因为项目托管在 GitHub、README 欢迎参与，或文件能被浏览下载，就推断仓库内容采用某种开源许可证。

如果以后增加仓库级许可证，必须明确区分：

- 项目自己编写的脚本、元数据和说明文档；
- 第三方原著全文、译文、扫描 PDF 和图片；
- 不同第三方材料各自可能存在的版权或合同限制。

仓库级代码或文档许可证不能自动覆盖第三方文本。

## 5. 当前工作区中实际存在的凯德洛夫文件

### 5.1 凯德洛夫子目录结构

```text
kedrov_markdown/
├── README.md
├── kedrov_md/
│   └── russian_web/
│       └── royallib/
│           ├── besedy-o-dialektike.md
│           ├── o-dialektike-prirody-engelsa.md
│           ├── o-tvorchestve-v-nauke-i-tekhnike.md
│           └── assets/
│               └── o_tvorchestve_v_nauke_i_tehnike/
│                   └── i_002.png ... i_029.png
├── metadata/
│   └── royallib_manifest.json
└── scripts/
    └── kedrov_royallib_convert.py
```

脚本运行产生的 `scripts/__pycache__/` 已被 `.gitignore` 忽略，不属于来源、正文或交付内容，因此未列入上面的有效文件树。

另有三份相关项目文档：

- [`KEDROV_SOURCE_SURVEY.md`](KEDROV_SOURCE_SURVEY.md)：来源调查、书目候选和优先级。
- [`PHILOSOPHY_SOURCE_FORMAT_POLICY.md`](PHILOSOPHY_SOURCE_FORMAT_POLICY.md)：格式、OCR 准入与发布政策。
- [`苏联哲学人物简介_AI参考.md`](苏联哲学人物简介_AI参考.md)：用户提供的 AI 人物总结，仅作未核验检索参考，不是原始文献。

### 5.2 各文件和目录的职责

| 路径 | 职责 | 是否属于正文 |
|---|---|---:|
| `kedrov_markdown/README.md` | 凯德洛夫子项目入口和重建说明 | 否 |
| `kedrov_markdown/kedrov_md/russian_web/royallib/*.md` | 三部俄文作者文本 | 是 |
| `kedrov_markdown/kedrov_md/russian_web/royallib/assets/` | HTML 源包内随正文出现的插图 | 正文附属资源 |
| `kedrov_markdown/source_scans/` | 6 个未处理 PDF/DjVu 源扫描件 | 否 |
| `kedrov_markdown/metadata/royallib_manifest.json` | URL、源文件哈希、输出哈希、图片哈希和处理状态 | 否 |
| `kedrov_markdown/metadata/source_scans_manifest.json` | 扫描件页数、字节数、SHA-256、格式和权利状态 | 否 |
| `kedrov_markdown/scripts/kedrov_royallib_convert.py` | 可复现的下载与 HTML 转 Markdown 脚本 | 否 |
| `notes/KEDROV_SOURCE_SURVEY.md` | 来源、书目、优先级和第二优先级核验结果 | 否 |
| `notes/PHILOSOPHY_SOURCE_FORMAT_POLICY.md` | 来源优先级、OCR 准入和发布规则 | 否 |
| `notes/KEDROV_COLLECTION_STATUS_FOR_CLAUDE.md` | 当前交接快照 | 否 |
| `notes/苏联哲学人物简介_AI参考.md` | 未核验 AI 人物资料，仅供检索 | 否 |

### 5.3 当前源扫描件位置

凯德洛夫 PDF/DjVu 统一保存在：

```text
kedrov_markdown/source_scans/
├── internet_archive/
├── phantastike/
└── public_library/
```

不得把这些文件放入 `kedrov_md/`。

扫描件元数据统一使用 `text_status: "source_scan_unprocessed"`，并明确 core、LLM 和 redistribution 均为 false。

### 5.4 转换脚本与清单

- 转换脚本：[`kedrov_royallib_convert.py`](../kedrov_markdown/scripts/kedrov_royallib_convert.py)
- 来源和哈希清单：[`royallib_manifest.json`](../kedrov_markdown/metadata/royallib_manifest.json)
- 资料库说明：[`kedrov_markdown/README.md`](../kedrov_markdown/README.md)

脚本使用 Python 标准库下载 RoyalLib HTML ZIP，读取 Windows-1251 HTML，解析标题、段落、列表、链接和图片，输出 UTF-8 Markdown。脚本没有调用 OCR。

重新生成：

```bash
python3 kedrov_markdown/scripts/kedrov_royallib_convert.py
```

只检查远端来源是否仍能生成相同结果：

```bash
python3 kedrov_markdown/scripts/kedrov_royallib_convert.py --check
```

2026-06-11 已运行 `--check`，三部文本全部通过。仓库内三个 Markdown 的 SHA-256 也与 manifest 一致，28 张图片均存在并被正文引用。

### 5.5 Git 状态

截至本文生成时，以下内容存在于本地工作区，但仍显示为 `??` 未跟踪状态，**尚未暂存、尚未提交到 Git 历史**：

- `kedrov_markdown/`
- `notes/KEDROV_SOURCE_SURVEY.md`
- `notes/PHILOSOPHY_SOURCE_FORMAT_POLICY.md`
- `notes/KEDROV_COLLECTION_STATUS_FOR_CLAUDE.md`
- `notes/苏联哲学人物简介_AI参考.md`
- `LLM_WIKI.md`
- `RESOLVER.md`
- `gbrain.yml`
- `scripts/prepare_gbrain_markdown.py`

因此，本文中的“已入库”表示文件已经放入项目工作区及规划目录，不表示已经完成 Git commit。后续代理在提交前应先检查整个脏工作区，避免把无关的大量修改一并提交。

## 6. 已处理并进入仓库的文本

### 6.1 `Беседы о диалектике`（《辩证法谈话》）

| 字段 | 当前值 |
|---|---|
| 作品年份 | 初版 1983；RoyalLib 页面采用 2007 版信息 |
| 来源页 | <https://royallib.com/book/kedrov_bonifatiy/besedi_o_dialektike.html> |
| 下载地址 | <https://royallib.com/get/html/kedrov_bonifatiy/besedi_o_dialektike.zip> |
| 原始格式 | Windows-1251 编码的真实 HTML，封装在 ZIP 中 |
| OCR | 未使用 |
| 处理 | HTML 转 UTF-8 Markdown |
| 仓库输出 | [`besedy-o-dialektike.md`](../kedrov_markdown/kedrov_md/russian_web/royallib/besedy-o-dialektike.md) |
| 当前文件规模 | 1,755 行；757,755 字节 |
| 标题数量 | 输出中 27 个 Markdown 标题；manifest 记录 25 个来源正文标题 |
| 图片 | 0 |
| 源 ZIP SHA-256 | `55b35e1909356a368d0d0c8d3a3d038ecdc7f242445dbd8dd704d77aa3b6c47a` |
| 源 HTML SHA-256 | `c6798811f64c3c8f1178f542fb003137d269ea324a315d443f72f0932ea7fff4` |
| 输出 SHA-256 | `2221dd0aa85419519e90360d2ac59e54ba2f59ec07e2ee92f62909c3cb42d97f` |
| 校勘状态 | `html_conversion_unverified`，未与正式印刷本逐字核对 |
| 权利状态 | 未声明开放许可；`redistribution_approved: "false"` |

### 6.2 `О «Диалектике природы» Энгельса`（《论恩格斯〈自然辩证法〉》）

| 字段 | 当前值 |
|---|---|
| 作品年份 | 1973 |
| 来源页 | <https://royallib.com/book/kedrov_bonifatiy/o_dialektike_prirodi_engelsa.html> |
| 下载地址 | <https://royallib.com/get/html/kedrov_bonifatiy/o_dialektike_prirodi_engelsa.zip> |
| 原始格式 | Windows-1251 编码的真实 HTML，封装在 ZIP 中 |
| OCR | 未使用 |
| 处理 | HTML 转 UTF-8 Markdown |
| 仓库输出 | [`o-dialektike-prirody-engelsa.md`](../kedrov_markdown/kedrov_md/russian_web/royallib/o-dialektike-prirody-engelsa.md) |
| 当前文件规模 | 3,152 行；645,608 字节 |
| 标题数量 | 输出中 67 个 Markdown 标题；manifest 记录 55 个来源正文标题 |
| 图片 | 0 |
| 源 ZIP SHA-256 | `1e6ca6c7dd761e0f1598b4322b202298824a53b391f7d87b43bef3544ad23cf9` |
| 源 HTML SHA-256 | `e3594e941c4596f92dd3def8807f886e64aa7cdcbb19f4cc7f5a0a72d79bb42c` |
| 输出 SHA-256 | `1f480d1f1cfbee6c252672b4c363cf7a8d50473d6841b0ed7aee54adeae150b7` |
| 校勘状态 | `html_conversion_unverified`，未与正式印刷本逐字核对 |
| 权利状态 | 未声明开放许可；`redistribution_approved: "false"` |

Internet Archive 另有扫描 PDF，但因为本书已经有合格 HTML 正文，PDF 仅是可选的版本参考，当前没有保存。

### 6.3 `О творчестве в науке и технике`（《论科学与技术中的创造》）

| 字段 | 当前值 |
|---|---|
| 作品年份 | 1987 |
| 来源页 | <https://royallib.com/book/kedrov_bonifatiy/o_tvorchestve_v_nauke_i_tehnike.html> |
| 下载地址 | <https://royallib.com/get/html/kedrov_bonifatiy/o_tvorchestve_v_nauke_i_tehnike.zip> |
| 备用网页 | <https://www.phantastike.com/superlearning/o_tvorch_v_nauke/html/> |
| 原始格式 | Windows-1251 编码的真实 HTML，封装在 ZIP 中 |
| OCR | 未使用 |
| 处理 | HTML 转 UTF-8 Markdown，并保存 HTML 包内插图 |
| 仓库输出 | [`o-tvorchestve-v-nauke-i-tekhnike.md`](../kedrov_markdown/kedrov_md/russian_web/royallib/o-tvorchestve-v-nauke-i-tekhnike.md) |
| 当前文件规模 | 1,853 行；678,287 字节 |
| 标题数量 | 输出中 25 个 Markdown 标题；manifest 记录 23 个来源正文标题 |
| 图片 | 28 张 PNG，正文中的 28 个引用均可解析 |
| 源 ZIP SHA-256 | `f7f68d95540143a61c343fcc2c9f102fe08fcc1549e1dc46e90d2c4e65bc35e7` |
| 源 HTML SHA-256 | `05f31ee965e6c785ebc30815c04364e4e2025e5f619e328b82034d089dba544b` |
| 输出 SHA-256 | `4b20ded880504bd935fa2ad54587f1a31e5ab78a4ec8a30af0e662e1c15019b7` |
| 校勘状态 | `html_conversion_unverified`，未与正式印刷本逐字核对 |
| 权利状态 | 未声明开放许可；`redistribution_approved: "false"` |

## 7. “已下载”的准确含义

为避免后续代理误解，本项目区分三种下载状态。

### 7.1 已下载、已处理、成果已入库

RoyalLib 的三个 HTML ZIP 已由脚本下载和处理。生成的三份 Markdown、28 张插图、哈希清单和转换脚本保存在仓库。

但是，**三个源 ZIP 和解压后的源 HTML 本身没有长期保存在仓库**。它们可由脚本从原 URL 重新下载，其 SHA-256 已写入 manifest。

### 7.2 已核验并按源扫描件入库

第二优先级调查期间，以下文件曾下载到临时目录进行格式、页数、题名页和哈希检查。它们没有复制到项目目录，因此不属于当前仓库收藏。

| 作品/文件 | 临时检查结果 | 当前状态 |
|---|---|---|
| `Ленин и научные революции` EPUB | OPF 和说明页明确表明由自动字符识别及 `hocr-to-epub` 生成 | 未准入；不使用、不转 Markdown |
| `Ленин и научные революции` PDF | 1980 年俄文版；477 个扫描页；64,934,140 字节；SHA-256 `3a519f5ef7808e4964356fd4e92422cc9e7234209f994496aea1f6e5ca1995e5` | 已保存为未处理源扫描件 |
| `Фридрих Энгельс. Развитие его взглядов на диалектику естествознания` PDF | 1970 年俄文版；160 个扫描页；5,455,395 字节；SHA-256 `6cf450f112e1768d6afb432ea32911f2ea0d8f69844e33229683598aeef832fa` | 已保存为未处理源扫描件 |
| `О «Диалектике природы» Энгельса` IA PDF | 186 个扫描页；约 8.3 MB；含 ABBYY 文本层；SHA-256 `5659b082b86c38ccc31e8b0c4704949e44fed9b72c9216e6d0c77a63c40c7f17` | 仅为重复版本参考；已有 HTML Markdown，目前不必入库 |

PDF 中存在 OCR/ABBYY 文本层不意味着必须删除 PDF，但任何文本层都不得用于生成 Markdown。

### 7.3 已检索到，但未下载

法译本 `Dialectique, logique, gnoseologie : leur unite` 的 Internet Archive 页面已找到：

<https://archive.org/details/dialectiquelogiq0000kedr>

普通 EPUB/PDF 不开放直接下载，只提供受控借阅的加密文件，因此当前只记录书目，没有下载，也没有入库。该法译本不能替代俄文原著。

## 8. 第二优先级逐项状态

| 作品 | 已检索 | 曾临时下载 | 已入库 | 已转 Markdown | 最终判断 |
|---|---:|---:|---:|---:|---|
| `Ленин и научные революции` | 是 | EPUB、PDF | PDF 已入库 | 否 | OCR EPUB 不使用；PDF 为未处理源扫描件 |
| `Фридрих Энгельс. Развитие его взглядов на диалектику естествознания` | 是 | PDF | 是 | 否 | 未处理源扫描件 |
| `Единство диалектики, логики и теории познания` | 是 | PDF | 是 | 否 | 2006 年第 2 版未处理源扫描件 |
| `О методе изложения диалектики. Три великих замысла` | 是 | PDF | 是 | 否 | 1983 年版未处理源扫描件 |
| `Диалектика и логика. Законы мышления` | 是 | DjVu | 是 | 否 | 1962 年版未处理源扫描件 |
| `Диалектика и логика. Формы мышления` | 是 | PDF | 是 | 否 | 1962 年版未处理源扫描件 |
| `О «Диалектике природы» Энгельса` IA 扫描版 | 是 | PDF | 否 | 不适用 | 已有 HTML Markdown；PDF 仅作可选版本参考 |
| `Dialectique, logique, gnoseologie : leur unite` 法译本 | 是 | 否 | 否 | 否 | 受控借阅，只记录书目 |

## 9. 已搜索到的目录、作品和入口

以下内容属于“已经发现检索线索”，不表示文件已经下载或正文已经核验。

### 9.1 综合目录入口

- Public Library 凯德洛夫作者页：<https://publ.lib.ru/ARCHIVES/K/KEDROV_Bonifatiy_Mihaylovich/_Kedrov_B.M..html>
- Koob 作者页：<https://www.koob.ru/kedrov_b/>
- Klex 作者页：<https://www.klex.ru/author/kedrov_b/>

Koob 和 Klex 覆盖约 30 项，适合建立书目和寻找 PDF。Public Library 主要提供 PDF/DjVu。DjVuTXT、XML 或 OCR 派生文本在项目校验流程建立并通过前不得进入正文语料。

### 9.2 已在目录中检索到的重要哲学著作

| 著作 | 当前覆盖情况 | 后续处理 |
|---|---|---|
| `Беседы о диалектике` | 已有 RoyalLib HTML 转 Markdown | 保持现状，后续可校勘 |
| `О «Диалектике природы» Энгельса` | 已有 RoyalLib HTML 转 Markdown | 保持现状；PDF 可选 |
| `О творчестве в науке и технике` | 已有 RoyalLib HTML 转 Markdown | 保持现状，后续可校勘 |
| `Единство диалектики, логики и теории познания` | 2006 年第 2 版 PDF 已保存 | 保持未处理状态，等待合法文本源或未来校验流程 |
| `О методе изложения диалектики. Три великих замысла` | 1983 年版 PDF 已保存 | 同上 |
| `Диалектика и логика. Законы мышления` | 1962 年版 DjVu 已保存 | 同上 |
| `Диалектика и логика. Формы мышления` | 1962 年版 PDF 已保存 | 同上 |
| `Анализ развивающегося понятия` | 已找到目录线索，尚未下载 | 核对合著信息；按格式政策处理 |
| `О повторяемости в процессе развития` | 已找到 Public Library 入口，尚未下载 | 有 PDF 则保存 PDF |
| `Классификация наук` 第 1-3 册 | 已找到 Public Library 入口，尚未下载 | 偏科学分类史，逐册核对；有 PDF 则保存 PDF |
| `Как изучать книгу В. И. Ленина «Материализм и эмпириокритицизм»` | 已找到 Public Library 入口，尚未下载 | 有 PDF 则保存 PDF |
| `Проблемы логики и методологии науки` | 已找到目录线索，尚未下载 | 优先寻找 HTML/EPUB；否则保存 PDF |
| `О великих переворотах в науке` | 已找到目录线索，尚未下载 | 按哲学/科学史资料处理 |
| `Периодический закон Д. И. Менделеева и его философское значение` | 已找到目录线索，尚未下载 | 有 PDF 则保存 PDF |
| `Развитие понятия элемента от Менделеева до наших дней` | 已找到目录线索，尚未下载 | 有 PDF 则保存 PDF |
| `Три аспекта атомистики` 第 1-3 卷 | 已找到目录线索，尚未下载 | 有 PDF 则保存 PDF |
| `Мировая наука и Менделеев` | 已找到目录线索，尚未下载 | 有 PDF 则保存 PDF |

### 9.3 已检索到的短篇和论文线索

- `Ленин и гегелевская диалектика`：找到一个 21 页 PDF 节选，不是完整 64 页版本。入口：<https://hegel.rhga.ru/upload/iblock/7eb/%D0%9A%D0%B5%D0%B4%D1%80%D0%BE%D0%B2.pdf>。尚未入库；如保存，应标记 `partial_excerpt`。
- `О диалектике научных открытий`（1966）：只记录论文题目，未找到权利状态清楚的完整 HTML。
- `О природе научного понятия`（1969）：只记录论文题目。
- `История науки и принципы ее исследования`（1971）：只记录论文题目。
- `О методе изложения диалектики от абстрактного к конкретному`（1978）：只记录论文题目。
- `О современной классификации наук`（1980）：只记录论文题目。

这些论文应继续查《Вопросы философии》档案和图书馆数据库。不得用搜索摘要拼接正文。

## 10. 人物与书目核对来源

以下网页用于确认人物身份和扩展书目，不是凯德洛夫原著正文来源：

- 俄罗斯科学院哲学研究所人物页：<https://iphras.ru/page22950653.htm>
- 莫斯科大学人物资料：<https://letopis.msu.ru/peoples/7673>
- 人物简介和较完整著作目录：<https://shchedrovitskiy.com/bonifatiy-mikhajlovich-kedrov/>

用户提供的 [`苏联哲学人物简介_AI参考.md`](苏联哲学人物简介_AI参考.md) 已放入项目，但带有以下限制：

- `text_role: "ai_reference"`
- `verification_status: "unverified"`
- `llm_wiki_eligible: "false"`

其中关于人物生卒年、职务、思想流派、作品和历史评价的说法，使用前都必须回查俄文原始资料或权威档案。

## 11. GBrain 处理流程与当前状态

### 11.1 GBrain 在项目中的定位

本项目使用 GBrain 作为本地 LLM wiki 的索引、分块、向量检索和关系抽取工具。Markdown 与 Git 文件是可审计的事实来源，GBrain 数据库、分块、嵌入和抽取结果都是可重建的派生数据，不能替代原始文件或来源元数据。

相关配置和说明：

- [`LLM_WIKI.md`](../LLM_WIKI.md)：GBrain 使用说明和常用命令。
- [`RESOLVER.md`](../RESOLVER.md)：按作者、文本角色和来源类型选择语料的规则。
- [`gbrain.yml`](../gbrain.yml)：当前 schema pack 和数据库跟踪目录配置。
- [`prepare_gbrain_markdown.py`](../scripts/prepare_gbrain_markdown.py)：检查和补充 Markdown front matter 的维护脚本。

GBrain 不负责判断原始文本是否合法、是否使用 OCR、是否校勘或是否可以公开再分发。来源准入必须先通过本项目的格式政策和版权审查，然后才能进入索引。

### 11.2 凯德洛夫文本进入 GBrain 的准入规则

| 内容类型 | 是否进入 GBrain 正文语料 | 原因 |
|---|---:|---|
| 合格 HTML 转换的三部凯德洛夫 Markdown | 是，当前标记为 eligible | 作者语言正文，未使用 OCR |
| 将来发现的原生结构化 EPUB 转换 Markdown | 可以 | 需先确认 EPUB 不是 OCR/hOCR 派生物 |
| 扫描 PDF | 否 | 只作版本资料和阅读参考，不建立 Markdown 正文 |
| PDF 内置文本层、ABBYY、hOCR、DjVuTXT/XML | 否 | 项目明确禁止用作正文来源 |
| `苏联哲学人物简介_AI参考.md` | 否 | AI 生成且未核验，`llm_wiki_eligible: "false"` |
| 来源调查、格式政策和本交接文档 | 可作为项目说明索引 | 属于元数据、政策或研究说明，不得与作者原文混同 |

三部凯德洛夫 Markdown 当前 front matter 一致包含：

```yaml
type: "source"
language: "ru"
collection: "kedrov-russian"
text_status: "html_conversion_unverified"
text_role: "source"
llm_wiki_eligible: "true"
redistribution_approved: "false"
gbrain_source: "project-markdown"
```

`llm_wiki_eligible: "true"` 只表示文件在内容角色上允许进入本地索引，不表示已经实际同步，也不表示获准公开再分发。`redistribution_approved` 是独立的版权字段。

### 11.3 标准处理流程

后续新增或修改凯德洛夫文本时，建议严格按以下顺序处理。

1. **来源准入**：确认来源是真实 HTML 或原生结构化 EPUB；排除 OCR、hOCR、ABBYY、DjVuTXT 和 PDF 文本提取。
2. **生成 Markdown**：保留标题结构、来源 URL、版次、语言、转换日期和校勘状态。
3. **补全 front matter**：至少记录 `type`、`language`、`collection`、`text_role`、`text_status`、`llm_wiki_eligible`、`source_license` 和 `redistribution_approved`。
4. **元数据检查**：运行 `python3 scripts/prepare_gbrain_markdown.py --check`。
5. **结构检查**：运行 `python3 scripts/split_longform_markdown.py --check` 和包装后的 GBrain lint。
6. **确认 Git 和配置范围**：文件必须进入 GBrain 实际读取的仓库状态；检查 `gbrain.yml` 是否覆盖新子目录。
7. **同步预演**：运行 `scripts/run_gbrain_without_dist.sh gbrain sync --full --dry-run --no-pull`。
8. **正式同步**：确认预演范围正确后通过同一包装脚本运行 full sync。
9. **补做嵌入和抽取**：必要时运行 `gbrain embed --stale` 与 `gbrain extract --stale`。
10. **检索验证**：使用俄文原题、作者名和关键概念进行 `gbrain search`，确认返回的页面 slug 指向 `kedrov_markdown/kedrov_md/`。

嵌入服务不可用时，可以先导入页面和分块：

```bash
gbrain sync \
  --repo /Users/hoshf/Project/Ilyenkov \
  --no-embed \
  --no-extract \
  --no-pull \
  --yes
```

服务恢复后再运行：

```bash
gbrain embed --stale
gbrain extract --stale
```

### 11.4 当前 GBrain 实例状态

2026-06-11 完成同步后的结果：

| 项目 | 当前值 |
|---|---|
| CLI 路径 | `/Users/hoshf/.bun/bin/gbrain` |
| GBrain 版本 | `0.42.37.0` |
| schema pack | `gbrain-base-v2` |
| 运行模式 | local |
| 本轮最终同步日期 | `2026-06-11` |
| 现有索引页数 | 652 页 |
| 现有页嵌入状态 | 100% |
| 凯德洛夫章节页 | 54 页 |
| 关系/时间线抽取 | 373 个正文页已处理；生成 0 条链接、0 条时间线，stale=0 |
| full cycle | 从未运行 |
| targeted cycle | 从未运行 |
| 活动锁和队列 | 无活动锁；队列无 active/waiting/failed/dead 项 |
| autopilot | 未运行，也未安装为自动任务 |

`embed=100%` 是数据库汇总状态。本轮三部作品已切为 54 个章节页面，没有 `embed_skip: oversized`，可参与向量检索。

### 11.5 凯德洛夫文本的实际索引状态

三部凯德洛夫著作均已进入 GBrain，但 slug 现在指向稳定章节，例如 `.../besedy-o-dialektike-ch000`。数据库验收确认 54 个凯德洛夫章节可检索，源扫描件、快照和旧单体页面均未进入 GBrain。

### 11.6 当前配置缺口

当前 [`gbrain.yml`](../gbrain.yml) 已包含 `kedrov_markdown/`：

```yaml
storage:
  db_tracked:
    - caute_ru_markdown/
    - spinoza_markdown/
    - kedrov_markdown/
    - notes/
    - translation_workspace/
    - dialectical_logic/
    - idols_ideals/
    - existing_translations/
```

普通增量 dry-run 只看 Git 书签；处理结构迁移时使用 `--full --dry-run`。GBrain 0.42.37.0 的 full-sync 实测仍会扫描 `dist/public`，因此全仓命令必须通过 `scripts/run_gbrain_without_dist.sh` 执行；该脚本用 `trap` 临时隐藏并恢复 `dist/`。

### 11.7 元数据与 lint 检查结果

运行：

```bash
python3 scripts/prepare_gbrain_markdown.py --check
```

结果为：

```text
changed=0 markdown_total=652 errors=0
```

这表示 652 个 Markdown 通过基础检查；正文与章节还通过统一来源、角色、版权和章节字段 schema，不表示正文已经完成纸本校勘。

运行 `gbrain lint .` 后：

```text
652 pages scanned. 209 issue(s) in 197 page(s).
```

三部凯德洛夫作品已按真实标题边界切章：

| 作品 | 章节数 | 最大章节状态 |
|---|---:|---|
| `besedy-o-dialektike` | 20 | 小于 500,000 字节 |
| `o-dialektike-prirody-engelsa` | 14 | 小于 500,000 字节 |
| `o-tvorchestve-v-nauke-i-tekhnike` | 20 | 小于 500,000 字节 |

15 部全仓长文本均使用共享脚本、原始快照、稳定 ID、字节偏移和 SHA-256 manifest 可逆切章。lint 仍会对 50 KB 以上页面给出软警告，但不存在 500 KB 以上完整章节，也没有 oversized embedding 跳过。

### 11.8 推荐的首次凯德洛夫同步步骤

当前已经完成切章、full sync、embedding 和 stale extraction。后续修改时按以下顺序重复验收：

1. 运行 Schema、source manifest 和 longform manifest 检查。
2. 通过 dist 包装脚本运行 lint 和 full dry-run。
3. 执行 full sync；如需分阶段审计，先使用 `--no-embed --no-extract`。
4. 运行 `gbrain embed --stale` 与 `gbrain extract --stale --catch-up`。
5. 用以下查询验证：

```bash
gbrain search "Беседы о диалектике"
gbrain search "О Диалектике природы Энгельса"
gbrain search "О творчестве в науке и технике"
gbrain search "Б. М. Кедров"
```

成功标准是结果明确出现 `kedrov_markdown/kedrov_md/russian_web/royallib/...`，而不是只返回提及凯德洛夫的伊里因科夫文本。

### 11.9 GBrain 数据的维护边界

- 不直接编辑 GBrain 数据库来修正文献；应修改 Markdown 后重新同步。
- 不把数据库、分块或向量嵌入当作唯一副本。
- 不让 GBrain 自动抽取结果覆盖作品元数据和人工来源判断。
- 不把语义检索的相似结果当作精确书目匹配。
- 删除或禁止公开某份全文时，应同步更新索引，但保留不含正文的来源审计记录。
- GBrain 本地索引资格与公开再分发资格相互独立；本地可索引不等于可以推送完整正文到 GitHub。

## 12. 已遇到的版权与再分发问题

> 本节是项目风险记录，不构成针对任何国家或具体发布行为的法律意见。当前没有完成系统的版权期限、权利归属或司法辖区分析。

### 12.1 当前能确认的事实

1. 凯德洛夫于 1985 年去世，但仅凭作者去世年份不能在本项目中直接宣布其作品属于公共领域。
2. 当前作品和版本集中出版于 1970-1987 年；出版社版本、编辑工作、序言、注释、插图、数字化成果和翻译可能分别涉及不同权利。
3. 当前找到的 RoyalLib 和 Internet Archive 条目没有为这些具体文件标示 Creative Commons、公共领域声明或允许下游再分发的许可。
4. 当前仓库自身也没有统一 `LICENSE` 文件，因此不存在可以覆盖这些第三方全文的仓库级授权依据。
5. 下载权限、在线阅读权限和公开再分发权限是不同问题。技术上能够下载文件，不等于能够把全文提交到公开 Git 仓库。

### 12.2 各来源遇到的具体情况

| 来源 | 实际观察 | 不能据此推断的事项 | 当前处理 |
|---|---|---|---|
| RoyalLib | 提供免费在线阅读和 HTML 等格式下载；设有“作者与权利人”投诉联系页，并说明收到正式请求后可能屏蔽或删除材料 | 该投诉机制不是作品的开放许可证，也没有授权本项目重新发布全文或图片 | 三部输出保留 `source_license: "not_stated"`、`redistribution_approved: "false"` |
| Internet Archive：`Ленин и научные революции` | PDF/EPUB 可访问；元数据中的 `rights`、`licenseurl` 和版权状态字段为空 | IA 托管、免费下载或派生格式存在不等于公共领域或获得再分发许可 | PDF 已入库且禁止公开导出；OCR EPUB 不使用 |
| Internet Archive：恩格斯研究著作 | PDF 可访问；元数据同样没有权利或许可声明 | 不能把可下载状态当作授权 | PDF 已入库且禁止公开导出 |
| Internet Archive：法译本 | 条目属于 `inlibrary`、`printdisabled` 等受控借阅集合，普通文件不开放直接下载 | 借阅权限不等于复制、解密或再分发权限；法文翻译本还可能有独立译者和版本权利 | 不下载、不绕过限制，只记录书目和网址 |
| Public Library、Koob、Klex | 提供书目或扫描下载入口，本次未发现针对凯德洛夫文件的明确开放许可 | 目录收录和下载按钮不能证明下游发布权 | 已保存的文件均为 `redistribution_approved: "false"` |
| Phantastike | 作为《论科学与技术中的创造》的 HTML 备用入口 | 备用网页存在不等于内容可自由再分发 | 只记录来源，不作为额外授权依据 |

RoyalLib 权利人页面：<https://royallib.com/copyright.html>。

本次版权状态核验使用的可复核入口如下，检查日期均为 2026-06-11：

- RoyalLib 权利人说明：<https://royallib.com/copyright.html>
- 《列宁与科学革命》IA 条目：<https://archive.org/details/B-001-038-009-ALL>
- 《列宁与科学革命》IA 元数据：<https://archive.org/metadata/B-001-038-009-ALL>
- 恩格斯研究著作 IA 条目：<https://archive.org/details/ao-114-friedrich-engels-developing-his-views-on-the-dialectic-of-natural-science-kedrov-1970>
- 恩格斯研究著作 IA 元数据：<https://archive.org/metadata/ao-114-friedrich-engels-developing-his-views-on-the-dialectic-of-natural-science-kedrov-1970>
- 法译本 IA 条目：<https://archive.org/details/dialectiquelogiq0000kedr>
- 法译本 IA 元数据：<https://archive.org/metadata/dialectiquelogiq0000kedr>

### 12.3 当前工作区内风险最高的内容

| 内容 | 风险原因 | 当前标记 |
|---|---|---|
| 三部完整俄文 Markdown | 属于完整作品的格式转换；来源没有给出下游开放许可 | `source_license: "not_stated"`；`redistribution_approved: "false"` |
| 28 张随书插图 | 图片可能具有与正文不同的作者、出版社或版式权利；当前没有逐图权利说明 | 哈希已记录，但没有独立开放许可 |
| 将来可能保存的扫描 PDF | 扫描本可能包含正文、封面、版式、序言和图片等多层权利；IA 元数据未给出授权 | 应标记 `pdf_reference_only`，不能默认公开发布 |
| 法译本 | 除原作外，还涉及法文翻译和具体版本；且当前是受控借阅 | 只记录书目 |
| AI 人物总结 | 不是原始资料，来源链不完整，可能混入受版权保护表述或事实错误 | `ai_reference`、`unverified`、不进入 LLM 正文语料 |

Markdown 转换改变了文件格式和排版，但不会自动消除原作品的版权。转换脚本可以独立授权，脚本生成的完整正文仍需按第三方内容处理。

### 12.4 公开 GitHub 仓库前的处置原则

在权利状态没有进一步确认之前，较稳妥的公开提交范围是：

- 来源调查、URL、书目和哈希；
- 转换脚本和处理政策；
- 不包含大段原文的技术说明与审计结果。

三部完整 Markdown 和 28 张插图目前不应被描述为“已获授权公开发布”。在提交到公开远端前，应至少选择一种明确方案：

1. 获得权利人或合法授权方的许可；
2. 完成适用法域、保护期限、版本和权利人的公共领域分析，并保存依据；
3. 将完整正文和图片保留在本地或私有存储，只公开脚本、元数据和来源链接；
4. 若项目管理者决定基于其他法律依据公开，单独记录该依据、适用范围和风险判断，不能仅写“研究用途”。

“用于学习、研究”是项目目的说明，不自动构成全文公开再分发许可，也不能替代具体法律依据。

### 12.5 后续版权核验清单

对每部拟公开作品至少核查：

- 作者及其他贡献者的死亡年份；
- 原作首次出版年份和当前数字版对应的具体版次；
- 出版社、编辑、序言、注释、图片和封面权利；
- 翻译本的译者、翻译年份和版本权利；
- 来源页是否提供明确许可证、权利声明或公共领域标记；
- 项目发布所在地、托管平台和目标读者涉及的适用法域；
- 获得许可时，是否允许格式转换、全文托管、再分发和商业或非商业使用。

元数据至少保留：`source_license`、`redistribution_approved`、`rights_review_status`、`rights_evidence_url` 和 `rights_notes`。没有证据时应写 `not_stated` 或 `unreviewed`，不得猜测。

### 12.6 权利人请求与移除记录

如果权利人、出版社、译者或整理者对公开材料提出异议，应暂停相关全文的公开分发，保留来源与哈希审计记录，并在处理日志中记录：请求日期、涉及文件、请求方身份核验、临时措施、最终决定和恢复条件。不要因为删除公开副本而删除项目对来源和处理历史的事实记录。

## 13. 当前文本质量与已知限制

1. 三部 Markdown 都来自真实 HTML，不是从扫描页 OCR 得到。
2. 转换是自动完成的，已保留标题、段落、列表、链接和图片，但没有逐页对照印刷版。
3. 三部文本当前统一标记为 `html_conversion_unverified`，不能称为“校勘本”或“权威版”。
4. RoyalLib 源 HTML 是 Windows-1251 编码，输出已转换为 UTF-8。
5. 原始 ZIP/HTML 未入库，长期可复现性依赖 RoyalLib URL 继续可访问；manifest 中的哈希可用于检测来源变化。
6. 当前来源均没有明确 Creative Commons、公共领域或其他开放再分发许可。
7. 完整正文当前用于研究、检索和来源评估；公开发布前仍需单独处理版权问题。

## 14. 后续代理的推荐工作顺序

### 14.1 已完成的源扫描件批次

6 个文件已保存到 `kedrov_markdown/source_scans/`，并在 `metadata/source_scans_manifest.json` 记录题名、作者、出版年、版次、URL、日期、页数、字节数、SHA-256、格式和权利状态。全部为 `source_scan_unprocessed`，不进入 GBrain。

### 14.2 下一批应继续查找格式的核心著作

1. `Единство диалектики, логики и теории познания`
2. `О методе изложения диалектики. Три великих замысла`
3. `Диалектика и логика. Законы мышления`
4. `Диалектика и логика. Формы мышления`
5. `Проблемы логики и методологии науки`

其中前四项已有扫描件；`Проблемы логики и методологии науки` 仍无合格自由完整源。检索顺序保持 HTML -> 原生 EPUB -> PDF -> DjVu，不能因为 OCR 文本更容易处理就改变顺序。

### 14.3 已有 Markdown 的后续质量工作

- 抽样对照正式出版物，检查标题层级、脚注、公式、表格和断段。
- 确认 RoyalLib 的版次信息与作品初版年份，必要时增加 `edition_year`。
- 对《论科学与技术中的创造》的 28 张图片逐项检查图注和顺序。
- 在版权状态未确认前，继续保持 `redistribution_approved: "false"`。

## 15. 禁止事项

后续代理不得执行以下操作：

- 在项目所有者明确启动校验流程前，不得把 `Ленин и научные революции` 的 IA OCR EPUB 转成 Markdown。
- 当前不得从 PDF 文本层、ABBYY、OCR Search Text、DjVuTXT/XML 或 hOCR 生成正文。
- 不得把 AI 人物总结当作学术事实或原始文献引用。
- 不得把“已搜索到”“曾临时下载”“已入库”“已转换”四种状态混为一谈。
- 不得在没有许可依据时把来源标记为可公开再分发。
- 不得把 RoyalLib 的投诉处理页面、Internet Archive 的下载按钮或“研究用途”说明当作开放许可证。
- 不得绕过法译本的受控借阅、加密或访问限制。
- 不得用仓库未来可能采用的代码许可证覆盖第三方原著、译本、PDF 或图片。

## 16. 给 Claude 的最短状态摘要

截至 2026-06-11，凯德洛夫子项目已经完成第一优先级：从 RoyalLib 的真实 HTML 转换了三部俄文著作为 Markdown，并保存第三部书的 28 张插图、转换脚本和完整哈希清单。转换没有使用 OCR，但文本尚未与印刷版校勘。

第二优先级已保存 6 个未处理源扫描件，并建立完整 manifest。《列宁与科学革命》的 OCR EPUB 不使用；法译本 `Dialectique, logique, gnoseologie : leur unite` 仍是受控借阅，只保留网址和书目。《逻辑与科学方法论问题》仍无合格完整源。

所有后续工作必须遵守：真实 HTML/原生 EPUB 优先；自由 PDF/DjVu 保存到 `source_scans/`；当前不启动新 OCR；未经人工校勘确认的 OCR 不进入核心层。已逐篇对图校勘的历史报纸特例必须保留 provenance 和 manifest。

版权方面，当前所有凯德洛夫全文均未发现明确开放再分发许可，仓库也没有统一许可证。RoyalLib 的权利人投诉机制和 IA 的可下载状态都不是下游授权；三部完整 Markdown 与 28 张图片在公开提交前需要单独完成权利判断，或只保留在本地或私有环境。

GBrain 方面，三部凯德洛夫著作已切为 54 个章节并进入当前 652 页数据库，`gbrain.yml` 已列出 `kedrov_markdown/`。章节没有 oversized 跳过，embedding stale 为 0。关系抽取已运行但仍为 0 条，因为默认 extraction 解析 Markdown 链接、front matter 引用和时间线，不从哲学正文推断语义关系。
