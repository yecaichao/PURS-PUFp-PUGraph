# 中文快速开始

## 1. 这个包是什么

`PURS-PUFp-PUGraph` 是一个统一的软件包，包含三条主线：

- `PURS`
  - 聚合物基元识别
- `PUFp`
  - 聚合物基元指纹与传统机器学习
- `PUGraph`
  - 聚合物基元图构建与图模型入口

这个仓库当前的目标不是严格复现论文原始划分，而是提供：

- 清晰的软件包结构
- 稳定、可运行的统一样例
- 适合发布和交接的文档入口

## 2. 从哪里开始

对外使用时，建议优先看：

1. `examples/README.md`
2. `examples/opecm_standard_demo/`

也就是说，优先从 `examples/` 进入，而不是先看 `tests/` 或内部 smoke 脚本。

标准样例主表是：

- `data/testing/opecm_paper54_tasks.csv`

这张表已经同时包含：

- `smiles`
- `ue`
- `uh`
- `max_mobility`
- 分类标签
- 图任务标签

所以它可以作为发布版统一样例数据源。

## 3. 安装

最简单的方式：

```bash
pip install -e .
```

如果要跑完整流程，建议：

```bash
pip install -e .[all]
```

如果你更习惯 `conda`，仓库里也提供了环境文件：

- `environments/environment-core.yml`
- `environments/environment-ml.yml`
- `environments/environment-graph.yml`
- `environments/environment-all.yml`

## 4. 推荐公开样例

### 4.1 OPECM 标准样例

路径：

- `examples/opecm_standard_demo/`

主命令：

```bash
python scripts/run_opecm_osc_unified_example.py --output-dir output/opecm_standard_demo
```

这个统一样例会基于主表：

- `data/testing/opecm_paper54_tasks.csv`

串起以下流程：

- 分类总结
- `PUFp` 回归 quick baseline
- `ue` / `uh` 图输入构建
- `PU-gn-exp` 与 `PU-MPNN` 的包装配置检查

如果还要执行图后端：

```bash
python scripts/run_opecm_osc_unified_example.py --output-dir output/opecm_standard_demo --execute-graphs
```

如果你只想先做最小直接检查，也可以运行：

```bash
purs recognize --input-csv data/testing/opecm_paper54_tasks.csv --name-column sample_id --smiles-column smiles --output-dir output/opecm_standard_demo/recognize
```

## 5. 当前推荐的理解方式

这个仓库里保留了论文映射和方法来源，但发布版更推荐这样理解：

- `examples/`
  - 面向用户的主入口
- `docs/`
  - 结构说明、schema、发布说明
- `tests/`
  - 内部维护用轻量回归测试
- `repro/`
  - 方法映射和论文相关材料

所以如果你是第一次使用，不需要先看 `repro/`。

## 6. 发布前内部验收

虽然发布包本身不强调测试入口，但发布前建议至少做一次主样例级验收：

1. 跑 `examples/opecm_standard_demo/`
2. 如有需要，再补跑聚焦样例

本仓库已经记录了一次实际跑通的发布前验收：

- `docs/package_release_validation.md`

## 7. 一句话建议

如果你只想快速上手：

1. 先装环境
2. 先看 `examples/README.md`
3. 直接跑 `examples/opecm_standard_demo/`
4. 如有需要，再看补充样例

这样最顺，也最符合这个统一软件包当前的发布方式。
