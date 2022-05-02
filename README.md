此文档基于Udemy上的一门[课程](https://thoughtworks.udemy.com/course/the-complete-hands-on-course-to-master-apache-airflow/)，讲师是Marc Lamberti。记录了Airflow的主要概念、使用方法，以及一些良好的实践方式。

# 1. Airflow 介绍

## 1.1. Why Airflow?

Because during the data processing, we need to orchestrate the data flow - which phase runs first and which one after. If it's done manually, it'll be a nightmare because there will be a lot of unexpected things happening. That's why we want a tool to handle it automatically and efficiently.

## 1.2. What is Airflow?

Airflow is an open-source platform to author, schedule, and monitor workflows programmatically.

Airflow is an orchestrater allowing you to execute your tasks at the right time, in the right way, and in the right order. It can connect to so many platforms to trigger them to work as planned.

### 1.2.1. Core components

* Webserver - provide the UI
* Scheduler - the heart of Airflow
* metastore - database storing metadata
* Executor -  a class defining how to execute the tasks
* Worker - a process/subprocess to execute the tasks, **actually do the job**.

### 核心概念

#### 1.2.2. DAG

> 在图论中，如果一个有向图从任意顶点出发无法经过若干条边回到该点，则这个图是一个有向无环图（DAG, Directed Acyclic Graph）。
>
> —— 摘自[维基百科](https://zh.wikipedia.org/wiki/%E6%9C%89%E5%90%91%E6%97%A0%E7%8E%AF%E5%9B%BE)

在Airflow中，一个DAG就代表了一条流水线。

#### 1.2.3. Operator

Operator是Airflow中用于执行动作的具体的实体。有三种类型：

1. Action Operator：执行实际的动作，不同的Operator支持不同的执行方式，如Bash、Python等。
2. Transfer Operator：用于将数据从源迁移至目标系统。
3. Sensor Operator：类似一个触发器，感知其他事件，由事件触发。

#### 1.2.4. Task / Task Instance

一个Operator就代表了一个任务。当一个流水线触发时，在这具体的流水线上的每一步就成了一个任务实例。

#### 1.2.5. Workflow

当一个DAG具体地开始执行时，整个过程——包含每一任务实例——就被称为工作流。

#### 1.2.6. Airflow不是数据处理框架，只负责调度



## 1.3. Airflow是如何工作的？

### 1.3.1. 单点结构

以Metastore为中心，Webserver通过Metastore来获取元数据，展示在网页上；Scheduler读取Metastore和Executor来进行调度；Executor在执行的过程中更新Metastore，同时负责维护任务队列。

### 1.3.2. 分布式结构

节点1：Webserver、Scheduler、Executor

节点2：Metastore、Queue，这里注意Queue可以是各种第三方队列，如RabbitQ、Redis。

多个Worker节点。

### 1.3.3. 各组件的工作流程

1. 用户将新的DAG文件放在dags目录下
2. Webserver和Scheduler都不断地扫描该目录，发现新文件后，解析DAG文件
3. 当工作流准备好触发时就新实例化一个DagRun类。DagRun就是DAG的实例
4. DagRun的状态转为running，将下一个Task Instance置入任务队列
5. 将任务队列中的任务放入Executor，Executor开始执行任务
6. 执行中由Scheduler监控，更新任务状态到Metastore
7. DAG执行完后，将再更新Metastore中的状态，并同步到UI（Webserver）



## 1.4. Airflow的安装

### 1.4.1. 安装

课程里所的讲解方式已经简化了Airflow的安装，因为讲师已经将所需的版本、以及依赖全部总结到了[这个gist](https://gist.github.com/marclamberti/742efaef5b2d94f44666b0aec020be7c)上。只需在这里找到Airflow的版本号（目前是2.1.0），以及点开containts的原始文档，得到其URL即可。安装命令如下：

```shell
pip install apache-airflow==2.1.0 --constraint https://gist.githubusercontent.com/marclamberti/742efaef5b2d94f44666b0aec020be7c/raw/21c88601337250b6fd93f1adceb55282fb07b7ed/constraint.txt
```

也可按照官方文档的命令来执行，只不过constraint有所不同。

### 1.4.2. 依赖

1. flask：用于webserver
2. gunicorn：用于webserver
3. psycopg2-binary：用于连接postgresql

### 1.4.3. 配置

#### 1.4.3.1. 数据库

以Postgres为例，需要在airflow.cfg -> sql_alchemy_conn的值设为postgres 连接串：`postgres+psycopg2://<user>:<pwd>@<host>[:<port>]/<database>`



## 1.5. Airflow CLI

```shell
airflow [command] --help
airflow db init
airflow webserver
airflow scheduler
airflow dags list
airflow tasks list <dag_name>
airflow dags trigger -e <EXEC_DATE> <dag_name>
airflow users create -u <username> -p <password> -f <first_name> -l <last_name> -e <email> -r <role>
```



# 2. 第一个Airflow Pipeline



## 2.1. PyCharm 设置

1. 设置 Python Interpreter，确认 Airflow 包存在，否则需要下载

   <img src="/Users/zhenqi/airflow/.image/image-20220501095759650.png" alt="设置 python interpreter" style="zoom: 33%;" />

2. 设置 Run/Debug Configurations

   <img src="/Users/zhenqi/airflow/.image/image-20220501100000669.png" alt="设置 run/debug configuration" style="zoom:33%;" />



## 2.2. 编写DAG

### 2.2.1. Import 相关依赖包

```python
from airflow.models import DAG
from datetime import datetime
```



### 2.2.2. DAG 参数

1. dag_id：所有DAG中的唯一标识
2. default_args：对DAG中所有operator都生效的参数
3. schedule_interval, start_date, catchup：



### 2.2.3. Operator 类型

**让一个 Operator 只完成一个 task，这样当 DAG 运行失败后可以从失败的那一个 task 重新开始运行。**

1. Action Operators：执行某种动作
2. Transfer Operators：数据迁移
3. Sensors：等待某种条件达成而触发事件



### 2.2.4. Providers

Airflow Providers 给airflow系统提供了一系列的额外的功能。Providers 包含了各类operators，hooks 用于和其他系统进行连接、通信等，也可为airflow本身提供扩展功能。Providers 有airflow预设的，也可编写自定义的。



### 2.2.5. Connection

通过Airflow可以设置与其他系统的连接方式，例如各类数据库、github、aws、facebook等。这些连接方式都需要通过providers提供支持。
