# 中文复现指南

## 1. 适用范围

这份文档面向以下场景：

- 在本机重新搭建 `PURS-PUFp-PUGraph`
- 复跑 `PURS / PUFp / ML / PUGraph`
- 让组内同学按照统一步骤验证环境与流程
- 为论文附录或软件说明准备一套清晰操作手册

## 2. 推荐环境

仓库已经提供了分层 conda 环境：

- `environments/environment-core.yml`
- `environments/environment-ml.yml`
- `environments/environment-graph.yml`
- `environments/environment-all.yml`

如果要完整复现图流程，推荐直接使用：

```powershell
conda env create -f environments/environment-graph.yml
conda activate purs-graph
pip install -e .
```

如果要一次性覆盖 `PURS + PUFp + ML + Graph`，推荐：

```powershell
conda env create -f environments/environment-all.yml
conda activate purs-all
pip install -e .
```

如果已经有可用环境，也可以直接：

```powershell
pip install -e .[all]
```

## 3. 快速自检

### 3.1 轻量测试

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p "test_*.py"
```

说明：

- 如果当前环境没有装全 `RDKit / scikit-learn / torch / torchgraphs`，只有轻量测试会运行
- 依赖重的工作流测试会被自动跳过

### 3.2 完整 smoke

```powershell
$env:PYTHONPATH='src'
python scripts/run_smoke_release.py
```

输出目录：

- `output/smoke_release/`

汇总文件：

- `output/smoke_release/smoke_summary.json`

当前 smoke 已覆盖：

- `purs fingerprint`
- `purs ml rf --quick`
- `purs graph build`
- `purs graph train` for `PU-gn-exp` in `command_only`
- `purs graph train` for `PU-gn-exp` in `execute`
- `purs graph train` for `PU-MPNN` in `command_only`
- `purs graph train` for `PU-MPNN` in `execute`
- `purs recognize --strict` 预期失败路径

## 4. PURS / PUFp / ML 基本流程

### 4.1 聚合基元识别

```powershell
$env:PYTHONPATH='src'
python -m purs.cli recognize `
  --input-csv examples/basic_recognition/input.csv `
  --output-dir output/basic
```

主要输出：

- `ring_total_list.csv`
- `one_hot.csv`
- `number.csv`
- `adjacent_matrix.csv`
- `node_matrix.csv`
- `index_data.csv`
- `skipped_records.csv`
- `run_summary.json`

### 4.2 PUFp 指纹

```powershell
$env:PYTHONPATH='src'
python -m purs.cli fingerprint `
  --input-csv examples/pufp_opv_demo/input.csv `
  --name-column sample_id `
  --smiles-column smiles `
  --output-dir output/pufp
```

### 4.3 传统机器学习

```powershell
$env:PYTHONPATH='src'
python -m purs.cli ml rf `
  --feature-csv output/pufp/number.csv `
  --target-csv examples/pufp_opv_demo/target.csv `
  --id-column sample_id `
  --target-column target `
  --quick
```

可替换 `rf` 为：

- `krr`
- `svm`

## 5. Graph 统一流程

### 5.1 graph build

```powershell
$env:PYTHONPATH='src'
python -m purs.cli graph build `
  --input-csv examples/pugraph_demo/input.csv `
  --output-dir output/graph
```

主要输出：

- `output/graph/graph_input.csv`
- `output/graph/graph_dataset_manifest.json`
- `output/graph/graph_build_manifest.json`
- `output/graph/pu_gn_exp_train.yaml`
- `output/graph/pu_mpnn_train.yaml`
- `output/graph/core/...`

说明：

- `graph_input.csv` 会自动过滤被共享 PURS 核心判定为无效的样本
- 这样后续图流程默认不会再吃到已经明确失败的记录

### 5.2 PU-gn-exp 训练

先执行：

```powershell
$env:PYTHONPATH='src'
python -m purs.cli graph train --config output/graph/pu_gn_exp_train.yaml
```

默认返回命令包装信息。

如果要真正执行训练，把 yaml 中的：

- `mode: command_only`

改成：

- `mode: execute`

然后再次运行：

```powershell
$env:PYTHONPATH='src'
python -m purs.cli graph train --config output/graph/pu_gn_exp_train.yaml
```

当前 `PU-gn-exp` 在统一 wrapper 下按连续值回归处理 `PCE_max`。

训练后推荐关注的输出：

- `output/graph/runs/pu_gn_exp/metrics_summary.json`
- `output/graph/runs/pu_gn_exp/val_predictions.csv`
- `output/graph/runs/pu_gn_exp/model.latest.pt`
- `output/graph/runs/pu_gn_exp/experiment.latest.yaml`
- `output/graph/runs/pu_gn_exp/checkpoints/`

其中：

- `metrics_summary.json`：验证集回归指标汇总
- `val_predictions.csv`：验证集逐条预测值、真实值、误差
- `model.latest.pt`：最近一次模型参数
- `experiment.latest.yaml`：可复现的实验配置

### 5.3 PU-gn-exp 预测

训练完之后，可以使用保存下来的实验配置直接预测。

示例：

```powershell
$env:PYTHONPATH='src'
python -m polymer_unit.predict `
  --model output/graph/runs/pu_gn_exp/experiment.latest.yaml `
  --data output/graph/graph_input.csv `
  --options batch_size=2 `
  --output output/graph/runs/pu_gn_exp/predict
```

当前预测输出包括：

- `output_000000.pt` 这类逐图结果文件
- `predictions.csv`

`predictions.csv` 适合后续直接做表格、误差分析和论文整理。

### 5.4 PU-MPNN 预处理

`PU-MPNN` 当前在统一仓库中主要打通的是预处理链路。

如果直接走 wrapper：

```powershell
$env:PYTHONPATH='src'
python -m purs.cli graph train --config output/graph/pu_mpnn_train.yaml
```

同样先是 `command_only`。

把 yaml 中：

- `mode: command_only`

改成：

- `mode: execute`

后再次运行，即可实际执行统一预处理。

主要输出：

- `output/graph/pu_mpnn/genwl3.pkl`
- `output/graph/pu_mpnn/release_check.csv`
- 中间 SDF 文件

说明：

- 为兼容 Windows 中文路径下的 RDKit 写文件问题，预处理内部会在必要时自动使用 ASCII 临时路径生成中间 SDF
- 但最终主输出仍保留在仓库目录下

## 6. OPECM 相关测试数据

仓库当前同时保留了：

- 正式 OPECM 数据位置：
  - `data/external/opecm/`
  - `data/processed/opecm/`
- 基于 OPECM 公共样例整理的统一小型测试夹具：
  - `tests/fixtures/opecm_common_tiny.csv`

这个小型夹具的用途是：

- 覆盖 `PURS`
- 覆盖 `PUFp`
- 覆盖 `PUGraph`
- 覆盖无效样本过滤逻辑

不建议把大型 `data/testing/common_polymer_cases.csv` 直接塞进日常单测，因为运行时间会明显变长。

## 7. 当前推荐的复现顺序

如果从零开始，建议按这个顺序：

1. 先创建 conda 环境并 `pip install -e .`
2. 跑 `python -m unittest discover ...`
3. 跑 `python scripts/run_smoke_release.py`
4. 跑 `purs fingerprint`
5. 跑 `purs ml rf --quick`
6. 跑 `purs graph build`
7. 先验证 `PU-gn-exp` execute
8. 再验证 `PU-MPNN` execute

## 8. 当前仍需要注意的地方

虽然现在整套链路已经可运行，但仍有几点要记住：

- `PU-gn-exp` 的大框架仍然保留 legacy 结构，只是 wrapper 层已经改成回归语义
- `PU-MPNN` 当前重点是统一预处理，后续真正训练主干仍可继续整理
- 部分 `pandas / numpy` 上游版本组合仍会打印少量弃用 warning，不影响当前通过

## 9. 一句话结论

当前仓库已经可以作为：

- 课题组内部统一主仓库
- 论文配套复现实验仓库
- 后续对外整理发布的基础版本

来使用。
