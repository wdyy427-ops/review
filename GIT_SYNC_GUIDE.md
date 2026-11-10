# 双主机 Git 同步说明

## 1. 建议通过 Git 同步的内容

- 研究协议、检索记录、筛选结果与一致性检验数据，例如 `random/`。
- 人工编码表、代码本和最终纳入清单，例如根目录与 `最终/` 下的 `.xlsx` 文件。
- 分析、核验、绘图和论文构建脚本，例如 `outputs/rq_review_20261024/scripts/` 与 `outputs/manuscript_20261029/*.py`。
- 规范化后的 CSV、JSON、Markdown 数据和报告，尤其是 `supplement_enhanced_v2/`、RQ1-RQ3结果和稳健性分析。
- 论文源文件、参考文献库、最终图表和规模合理的 DOCX/PDF交付物。
- 推荐器构建脚本、QA脚本和其他源代码；生成的 `dist/` 不同步，可在任一主机重新生成。

## 2. 不建议通过普通 Git 同步的内容

- `local_llm/` 中的GGUF模型、CUDA DLL和下载压缩包，约6.6 GB。
- `_deps/`、`node_modules/`、`.vite-service/` 等可重新安装的依赖和运行时。
- `最终/全文-重新排序*` 中的全文PDF及其重复副本，约4.6 GB，且多文件超过GitHub单文件100 MB限制。
- `参考文献/` 中的出版商PDF。此类资料可能受许可限制，不宜上传至普通远程仓库。
- `tmp/`、QA分页截图、预览、日志、PID、检查转储和生成站点。
- ZIP/TGZ等重复打包文件；应同步其可编辑源文件。

全文文献建议使用两台主机都可访问的私有云盘、NAS、Syncthing或受控Git LFS仓库同步，并在两台主机保持相同的相对目录结构。

## 3. 首次建立仓库

在项目根目录执行：

```powershell
git init
git branch -M main
git remote add origin https://github.com/wdyy427-ops/review.git
git add .gitignore GIT_SYNC_GUIDE.md
git add .
git status
git commit -m "Initialize review research project"
git push -u origin main
```

在执行 `git commit` 前，应重点检查 `git status`，确认没有PDF全文、本地模型、依赖目录或敏感信息进入暂存区。

## 4. 第二台主机

```powershell
git clone https://github.com/wdyy427-ops/review.git
cd review
```

随后单独恢复全文文献目录和本地运行环境。不要把另一台主机的 `node_modules`、Python依赖或本地模型直接复制进Git历史。

## 5. 日常同步顺序

开始工作前：

```powershell
git pull --rebase
```

完成一组可描述的修改后：

```powershell
git status
git add <本次修改的文件或目录>
git commit -m "简要说明本次研究修改"
git push
```

不要在两台主机同时修改同一个Excel或Word文件。二进制文件无法像文本文件一样可靠合并，建议在切换主机前完成提交和推送。

## 6. 推荐的提交边界

- `screening:` 检索与筛选记录更新
- `coding:` 编码表或代码本更新
- `analysis:` 分析脚本和结果更新
- `figures:` 图表与源数据更新
- `manuscript:` 论文文字或参考文献更新
- `recommender:` 推荐器源代码更新

