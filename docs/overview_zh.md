# PURS-PUFp-PUGraph 总梳理

## 1. 项目定位

这个统一仓库的目标，是把原来的三个相关项目整合为一套分层清晰的软件平台：

- `PURS`：聚合基元识别核心
- `PUFp`：聚合基元指纹表达与传统机器学习
- `PUGraph`：聚合基元图表达与图学习

统一后的主线是：

`polymer SMILES -> PURS core -> PUFp / PUGraph -> 下游预测与解释`


## 2. 三个原始项目现在在统一仓库中的对应关系

### 2.1 PURS 核心

来源：

- `Python-based-polymer-unit-recognition-script-PURS-for-PUFp`
- `PUFp-for-OPV-materials`
- `PURS-for-PU-graph` 中重复出现的公共识别逻辑

现在的位置：

- `src/purs/core/recognize.py`
- `src/purs/core/classify.py`
- `src/purs/core/structure_identity.py`

### 2.2 PUFp 与传统机器学习

来源：

- `PUFp-for-OPV-materials`

现在的位置：

- `src/purs/fingerprint/build.py`
- `src/purs/ml/common.py`
- `src/purs/ml/rf.py`
- `src/purs/ml/krr.py`
- `src/purs/ml/svm.py`

### 2.3 PUGraph

来源：

- `PURS-for-PU-graph`

现在的位置：

- 包装层：
  - `src/purs/graph/dataset.py`
  - `src/purs/graph/builders.py`
- legacy 资产：
  - `src/purs/graph/pu_gn_exp/polymer_unit/`
  - `src/purs/graph/pu_mpnn/legacy/`


## 3. 仓库结构

统一仓库当前已经形成以下主结构：

- `src/purs/`
  - 核心 Python 包
- `data/`
  - 外部数据库与处理后数据
- `examples/`
  - 可运行样例
- `tests/`
  - 自动化测试与夹具
- `repro/`
  - 面向论文复现的目录
- `docs/`
  - 架构、迁移、稳定性、数据规范、发布清单等文档
- `environments/`
  - 分层环境文件


## 4. 数据层现在的组织方式

### 4.1 正式数据库层

当前已经接入 `OPECM-Dataset`：

- `data/external/opecm/1_raw_data.csv`
- `data/external/opecm/OPECM_dataset.xlsx`
- `data/processed/opecm/2_PU_data.csv`
- `data/processed/opecm/3_Descriptors.csv`

### 4.2 示例数据层

当前示例包括：

- `repro/supplementary_examples/basic_recognition/`
- `repro/supplementary_examples/opecm_demo/`
- `repro/supplementary_examples/pufp_opv_demo/`
- `repro/supplementary_examples/pugraph_demo/`

### 4.3 测试夹具层

当前测试夹具包括：

- `tests/fixtures/tiny_polymers.csv`
- `tests/fixtures/duplicate_names.csv`
- `tests/fixtures/invalid_smiles.csv`
- `tests/fixtures/opv_tiny.csv`

### 4.4 论文复现层

当前保留了论文方向的复现入口目录：

- `repro/acsami_2023_pufp/`
- `repro/jctc_2024_pugraph/`
- `repro/npj_2025_opv/`


## 5. 当前已经打通的命令面

### 5.1 PURS core

已可运行：

- `purs recognize`
- `purs classify`

### 5.2 PUFp

已可运行：

- `purs fingerprint`

它会串起：

- `recognize`
- `classify`

并在一个输出目录内生成完整 PUFp 核心结果。

### 5.3 传统机器学习

已可运行：

- `purs ml rf`
- `purs ml krr`
- `purs ml svm`

### 5.4 图学习

已可运行：

- `purs graph build`
- `purs graph train`

说明：

- `graph build` 已经能生成标准化图输入和 manifest
- `graph train` 当前已经能包装 `PU-gn-exp` / `PU-MPNN` 的调用
- 但图模型内部仍保留较多 legacy 代码，后续还需要继续精炼


## 6. 稳定性策略

统一仓库已经开始显式处理稳定性问题，尤其是 RDKit 解析失败这类情况。

目前 `purs recognize` 已经具备：

- 对无效 SMILES 的结构化跳过
- `skipped_records.csv`
- `run_summary.json`
- CLI 中显示：
  - 输入行数
  - 成功处理条数
  - 跳过条数

另外已经支持：

- `--strict`

含义：

- 只要有跳过记录，就直接失败退出
- 同时保留跳过报告文件，便于排查


## 7. 当前已完成的实际验证

### 7.1 PURS / PUFp

已使用 `repro/supplementary_examples/opecm_demo/input.csv` 进行真实 smoke test。

已成功生成：

- `ring_total_list.csv`
- `one_hot.csv`
- `number.csv`
- `adjacent_matrix.csv`
- `node_matrix.csv`
- `index_data.csv`
- `ring_df.csv`
- `type_frame.csv`
- `skipped_records.csv`
- `run_summary.json`

### 7.2 ML

已成功做过 `purs ml rf --quick` smoke test，并生成图文件。

### 7.3 Graph

已成功做过：

- `purs graph build`
- `purs graph train --config ...`

其中：

- `graph build` 会生成标准化 `graph_input.csv`
- `graph train` 当前可输出图模型训练命令包装信息


## 8. 自动化测试现状

当前已经补了轻量自动测试：

- `tests/test_cli.py`
- `tests/test_workflows.py`

测试覆盖的方向包括：

- CLI parser 构建
- invalid SMILES 跳过与报告
- fingerprint 全输出包生成
- graph build manifest 生成

当前测试已通过。

推荐运行方式：

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p "test_*.py"
```


## 9. 当前文档体系

当前已经有以下辅助文档：

- `docs/architecture.md`
- `docs/migration.md`
- `docs/dataset_registry.md`
- `docs/stability.md`
- `docs/graph_workflow.md`
- `docs/schema.md`
- `docs/release_checklist.md`
- `docs/changelog.md`

这些文档分别负责：

- 架构
- 旧仓库迁移
- 数据角色分配
- 稳定性规则
- 图分支接通状态
- 列名与字段规范
- 发布前检查
- 变更记录


## 10. 当前还没完全做完的部分

虽然统一仓库已经可运行，但还存在几个“后续精炼”方向：

### 10.1 图分支仍有 legacy 重复逻辑

尤其是 `PU-gn-exp` 内部仍带有旧版 `PURS` 逻辑，后面应逐步改为直接调用统一 `purs.core`。

### 10.2 图模型执行还偏包装层

目前 `graph train` 已经接通，但主要是统一入口和命令封装；
后续还应进一步：

- 统一 preprocessing
- 统一 config 校验
- 减少 notebook 依赖

### 10.3 README 还可以再对外发布化

后续如果面向正式开源发布，建议进一步补：

- citation 整理
- install 细化
- command examples 精炼
- 论文与软件关系说明


## 11. 当前项目状态的简短判断

现在这个统一仓库已经不再只是“整理计划”或“目录骨架”，而是：

- 主结构已成型
- 主命令已接通
- 数据层已统一
- 稳定性开始显式管理
- 图分支已有统一入口
- 自动测试已建立

也就是说，它已经进入：

**“可以持续迭代和发布的统一软件仓库”**

而不是停留在前期概念设计阶段。


## 12. 下一步最推荐的工作顺序

如果继续推进，建议按下面顺序：

1. 清理图分支中的重复 PURS 逻辑
2. 继续把 graph preprocessing 完整脚本化
3. 精炼 README 为正式开源版本
4. 补更多 regression tests
5. 准备首个对外 release
