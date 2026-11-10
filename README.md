# Subjective Evaluation of Perceived Effects in AI-Assisted Design Workflows

本仓库保存系统性文献综述 **Subjective Evaluation of Perceived Effects in AI-Assisted Design Workflows: A Systematic Literature Review** 的检索筛选记录、编码数据、规范性审查、关系分析、论文材料、图表与推荐器原型。

## 研究目标

本研究围绕 AI-assisted design workflows 中 perceived effects 的 subjective evaluation，考察评价操作化的三个递进层次——evaluation dimensions、subjective indicators 和 tools——以及它们与情境因素之间的关系。

- **RQ1 — Descriptive mapping:** 梳理评价维度、主观指标和工具，并分析其年代、设计领域及设计阶段分布。
- **RQ2 — Rigor appraisal:** 依据研究中操作化的七项 JCSEE 相关标准，审查公开论文所呈现的评价支持与报告情况。
- **RQ3 — Relational analysis:** 分析评价操作化与 G1–G7 情境因素之间的关系及其预测贡献。
- **RQ4 — Recommender development:** 将综述和关系分析结果转化为渐进式、可追溯的评价操作化推荐器。

## 当前数据口径

当前分析应使用补充材料增强版数据，而不是早期的 490 条记录版本：

| 层级 | 当前数量 |
|---|---:|
| 纳入论文 | 125 |
| 评价案例 | 159 |
| 候选评价证据记录 | 514 |
| 已映射评价维度的记录 | 460 |
| 已映射主观指标的记录 | 454 |
| 测量工具实例 | 624 |
| 七项标准级审查记录 | 3,598 |

当前机器可读主数据位于：

```text
outputs/rq_review_20261024/supplement_enhanced_v2/03_revised_results/
```

研究审计指出，125 篇论文中有 95 篇产生候选评价记录，71 篇产生至少一条已映射的评价维度记录。因此，不应把 125 篇论文、514 条候选记录和 460 条已映射记录视为相同分析总体。

## 评价操作化框架

研究将评价实践组织为两类信息：

1. **评价操作化组件**：evaluation question → evaluation dimension → subjective indicator → tool。
2. **情境因素 G1–G7**：evaluation purpose、design domain、design stage、evaluation object、evaluators、target users 和 AI function。

主要分类体系、JSON 结构、JCSEE 审查锚点及建模协议见：

```text
outputs/rq_review_20261024/protocol.md
```

## 目录说明

| 路径 | 内容 |
|---|---|
| `check/` | 各轮筛选表及最终纳入记录 |
| `1_consensus test/`、`2_consensus test/` | 筛选一致性检验材料 |
| `random/` | 检索、抽样或筛选相关数据 |
| `最终/` | 最终纳入清单及研究工作文件；全文 PDF 目录不进入 Git |
| `outputs/rq_review_20261024/` | 编码、RQ1–RQ4 分析脚本、结果和推荐器材料 |
| `outputs/rq_review_20261024/supplement_enhanced_v2/` | 当前增强版数据、分析和质量检查结果 |
| `outputs/manuscript_20261029/` | 当前论文文本、图表构建脚本、审计和交付文件 |
| `outputs/最终整合文档_20261027/` | 较早的 490 条记录整合版，仅供历史追踪 |
| `参考文献/` | 参考资料；出版商 PDF 不通过普通 Git 同步 |
| `GIT_SYNC_GUIDE.md` | 两台主机之间的 Git 同步说明 |

## 论文与审计入口

- 当前论文文本：`outputs/manuscript_20261029/manuscript_full_text.txt`
- 当前论文 DOCX/PDF：`outputs/manuscript_20261029/Subjective_Evaluation_Manuscript.*`
- 数据与方法审计：`outputs/manuscript_20261029/audit_data.md`
- 当前语料目录：`outputs/manuscript_20261029/reviewed_corpus_catalogue.csv`
- 增强版交付说明：`outputs/rq_review_20261024/supplement_enhanced_v2/README_交付说明.md`

## 重要解释边界

- 七项 JCSEE 代码是本研究根据已选标准形成的操作化审查规则，不是 JCSEE 官方量表、认证或总分。
- 规范性状态反映留存材料中的报告支持情况；信息未报告不等于研究质量已被证明为差。
- 关系模型提供预测性、描述性证据，不应解释为因果影响。
- 推荐器是具有证据追溯能力的研究原型，尚不能声称已经证明推荐最优或能够提高评价质量。
- `audit_data.md` 记录了筛选一致性、自动审查、特征泄漏、日期口径及推荐器验证方面仍需处理的限制；准备投稿时应优先依据该审计进行人工复核。

## 在另一台电脑上使用

首次获取：

```powershell
git clone https://github.com/wdyy427-ops/review.git
cd review
```

开始工作前：

```powershell
git pull --rebase origin main
```

完成修改后：

```powershell
git add <本次修改的文件>
git commit -m "简要说明修改内容"
git push origin main
```

完整同步原则见 `GIT_SYNC_GUIDE.md`。全文 PDF、本地模型、CUDA 文件、依赖目录、临时文件及可重新生成的构建产物已由 `.gitignore` 排除，需要通过受控云盘、NAS 或其他合规方式单独同步。

## 运行环境

仓库包含 Python 分析和绘图脚本以及推荐器相关的前端脚本，但目前没有统一锁定的 Python 或 Node 依赖清单。迁移到新主机时应创建独立环境，并根据实际要运行的脚本补齐依赖；不要把 `node_modules`、CUDA 运行时或本地模型提交到仓库。

