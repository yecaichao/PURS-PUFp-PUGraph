# 程序包架构

## 总体结构

这个程序包的核心结构是：

`polymer SMILES -> PURS core -> PUFp / PUGraph -> downstream tasks`

也就是说，它不是三套彼此独立的代码，而是：

- 一个共享核心
- 两条下游分支
- 一个统一命令入口
- 一套单主样例发布入口

## 分层说明

### 1. `purs.cli`

统一命令入口，负责分发到各模块：

- `purs recognize`
- `purs classify`
- `purs fingerprint`
- `purs ml rf|krr|svm`
- `purs graph build`
- `purs graph train`

### 2. `purs.core`

共享核心层，负责：

- 输入列识别
- `SMILES` 清洗
- polymer-unit 识别
- 标准输出文件生成

### 3. `purs.fingerprint`

`PUFp` 主线，负责从共享核心结果生成指纹与相关表格。

### 4. `purs.ml`

轻量机器学习层，负责：

- 回归
- 分类
- `PUFp` 与主表标量特征融合

### 5. `purs.graph`

图工作流层，负责：

- graph 输入构建
- graph 配置生成
- `PU-gn-exp` 与 `PU-MPNN` 的统一包装入口

### 6. `purs.data`

数据任务层，负责统一标准样例表的任务标签逻辑。

## 入口

当前有一个公开样例：

- `examples/opecm_standard_demo/`

它使用一张标准样例表：

- `data/testing/opecm_paper54_tasks.csv`

这张表同时支撑：

- `PURS`
- `PUFp`
- 分类演示
- 图输入准备

```
