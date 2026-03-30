# 中文快速开始

## 1. 这个包是什么

`PURS-PUFp-PUGraph` 是一个统一的软件包，包含三条主线：

- `PURS`：聚合物基元识别
- `PUFp`：聚合物基元指纹与轻量机器学习流程
- `PUGraph`：聚合物基元图构建与图学习包装流程

## 2. 从哪里开始

发布版只保留一个公开样例：

- `examples/opecm_standard_demo/`

它对应的一张标准样例表是：

- `data/testing/opecm_paper54_tasks.csv`

## 3. 安装

最简单的安装方式：

```bash
pip install -e .
```

如果要跑完整图流程：

```bash
pip install -e .[all]
```

## 4. 推荐命令

统一样例命令：

```bash
python scripts/run_opecm_osc_unified_example.py --output-dir output/opecm_standard_demo
```

如果还要执行图后端：

```bash
python scripts/run_opecm_osc_unified_example.py --output-dir output/opecm_standard_demo --execute-graphs
```

如果只想先做最小识别检查：

```bash
purs recognize --input-csv data/testing/opecm_paper54_tasks.csv --name-column sample_id --smiles-column smiles --output-dir output/opecm_standard_demo/recognize
```

## 5. 当前发布版的理解方式

这个仓库当前强调的是：

- 一个清晰的软件包结构
- 一张统一标准样例表
- 一个公开样例入口

而不是保留大量并行样例或论文复现目录。
