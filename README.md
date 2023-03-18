此文档基于 Udemy 上的一门[课程](https://thoughtworks.udemy.com/course/the-complete-hands-on-course-to-master-apache-airflow/)，讲师是 Marc Lamberti。记录了 Airflow 的主要概念、使用方法，以及一些良好的实践方式。

# 1. Airflow 介绍

## 1.1. Why Airflow?

Because during the data processing, we need to orchestrate the data flow - which phase runs first and which one after. If it's done manually, it'll be a nightmare because there will be a lot of unexpected things happening. That's why we want a tool to handle it automatically and efficiently.

## 1.2. What is Airflow?

Airflow is an open-source platform to author, schedule, and monitor workflows programmatically.

Airflow is an orchestrator allowing you to execute your tasks at the right time, in the right way, and in the right order. It can connect to so many platforms to trigger them to work as planned.

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

在 Airflow 中，一个 DAG 就代表了一条流水线。

#### 1.2.3. Operator

Operator 是 Airflow 中用于执行动作的具体的实体。有三种类型：

1. Action Operator：执行实际的动作，不同的 Operator 支持不同的执行方式，如 Bash、Python 等。
2. Transfer Operator：用于将数据从源迁移至目标系统。
3. Sensor Operator：类似一个触发器，感知其他事件，由事件触发。

#### 1.2.4. Task / Task Instance

一个 Operator 就代表了一个任务。当一个流水线触发时，在这具体的流水线上的每一步就成了一个任务实例。

#### 1.2.5. Workflow

当一个 DAG 具体地开始执行时，整个过程——包含每一任务实例——就被称为工作流。

#### 1.2.6. Airflow不是数据处理框架，只负责调度



## 1.3. Airflow是如何工作的？

### 1.3.1. 单点结构

以 Metastore 为中心，Webserver 通过 Metastore 来获取元数据，展示在网页上；Scheduler 读取 Metastore 和 Executor 来进行调度；Executor 在执行的过程中更新 Metastore，同时负责维护任务队列。

### 1.3.2. 分布式结构

节点1：Webserver、Scheduler、Executor

节点2：Metastore、Queue，这里注意 Queue 可以是各种第三方队列，如 RabbitQ、Redis。

多个Worker节点。

### 1.3.3. 各组件的工作流程

1. 用户将新的 DAG 文件放在 dags 目录下
2. Webserver 和 Scheduler 都不断地扫描该目录，发现新文件后，解析 DAG 文件
3. 当工作流准备好触发时就新实例化一个 DagRun 类。DagRun 就是 DAG 的实例
4. DagRun 的状态转为 running，将下一个 Task Instance 置入任务队列
5. 将任务队列中的任务放入 Executor，Executor 开始执行任务
6. 执行中由 Scheduler 监控，更新任务状态到 Metastore
7. DAG 执行完后，将再更新 Metastore 中的状态，并同步到UI（Webserver）



## 1.4. Airflow的安装

### 1.4.1. 安装

课程里所的讲解方式已经简化了 Airflow 的安装，因为讲师已经将所需的版本、以及依赖全部总结到了[这个gist](https://gist.github.com/marclamberti/742efaef5b2d94f44666b0aec020be7c)上。只需在这里找到 Airflow 的版本号（目前是2.1.0），以及点开 constraints 的原始文档，得到其URL即可。安装命令如下：

```shell
pip install apache-airflow==2.1.0 --constraint https://gist.githubusercontent.com/marclamberti/742efaef5b2d94f44666b0aec020be7c/raw/21c88601337250b6fd93f1adceb55282fb07b7ed/constraint.txt
```

也可按照官方文档的命令来执行，只不过 constraint 有所不同。

### 1.4.2. 依赖

1. flask：用于 webserver
2. gunicorn：用于 webserver
3. psycopg2-binary：用于连接 postgresql

### 1.4.3. 配置

#### 1.4.3.1. 数据库

以 Postgres 为例，需要在 airflow.cfg -> sql_alchemy_conn 的值设为 postgres 连接串：`postgres+psycopg2://<user>:<pwd>@<host>[:<port>]/<database>`



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

   <img src="https://zhenqi-imagebed.s3.ap-east-1.amazonaws.com/uploaded_date=2023-03/image-20220501095759650-python-interpreter-39fea8692ed775039676f5e84eec3fc6.png" alt="设置 python interpreter" style="zoom: 33%;" />

2. 设置 Run/Debug Configurations

   <img src="https://zhenqi-imagebed.s3.ap-east-1.amazonaws.com/uploaded_date=2023-03/image-20220501100000669-run-debug-conf-b2d81d5b7dd5c753ce3c8acbcb75a360.png" alt="设置 run/debug configuration" style="zoom:33%;" />



## 2.2. 编写DAG

### 2.2.1. Import 相关依赖包

```python
from airflow.models import DAG
from datetime import datetime
```



### 2.2.2. DAG 参数

1. dag_id：所有 DAG 中的唯一标识
2. default_args：对 DAG 中所有 operator 都生效的参数
3. schedule_interval, start_date, catchup



### 2.2.3. Operator 类型

**让一个 Operator 只完成一个 task，这样当 DAG 运行失败后可以从失败的那一个 task 重新开始运行。**

1. Action Operators：执行某种动作
2. Transfer Operators：数据迁移
3. Sensors：等待某种条件达成而触发事件



### 2.2.4. Providers

Airflow Providers 给airflow系统提供了一系列的额外的功能。Providers 包含了各类 operators，hooks 用于和其他系统进行连接、通信等，也可为 airflow 本身提供扩展功能。Providers 有 airflow 预设的，也可编写自定义的。



### 2.2.5. Connection

通过 Airflow 可以设置与其他系统的连接方式，例如各类数据库、github、aws、facebook 等。这些连接方式都需要通过 providers 提供支持。



### 2.2.6. Sensor

Sensor 是一种特殊的 Operator，它可以检测特定的条件，如果满足条件，则会继续运行。
有两个参数要注意：
1. *poke_interval*: 表示 sensor 每隔多长时间检查一次是否满足条件，默认值为60s.
2. *timeout*: 表示 sensor 需要在多长时间内满足条件，默认值是7天。但一般来说，要设置一个有实际意义的时间，例如小于 scheduler_interval，且符合业务需要。



### 2.2.7. XCOM

XCOM 是一种 tasks 间通信的方式，简单地说，一个 task 在运行的过程中，将数据存储至 Airflow 的 meta database，以 task_id 为主键，存储的内容为一个个键值对。另一个 task 就可以通过访问 task_id 来读取这个数据。
默认情况下，每个 task instance 运行时都会在数据库中存储一行 return_value 记录。

### 2.2.8 Hook
Hook 是一个介于 Operator 和外部工具之间的桥梁，简化了它们之间的连接，将各种通信细节隐藏了起来。不同的外部工具都会有不同的 hook，如 postgres hook，aws hook。

## 2.3 Time & Scheduling

作为一个任务流水线编排工具，其最基本的功能就是对于任务运行时间的管理。这里可分为3大部分：流水线的周期性触发，历史流水线的处理，多任务的调度。

### 2.3.1 流水线周期

我们通常在处理数据时，对于同一类数据都会采用相同的操作，只是在不同时间处理的数据会属于不同的时间段。那么我们就会希望流水线可以按照一定周期规则定期地自动运行。这样我们只需定义好一个周期内的操作即可。

Airflow 的 DAG 提供了4个与周期相关的参数：start_date，end_date，schedule_interval 以及 catchup。

### 2.3.2 历史流水线处理

当 DAG 的参数 catchup 设置为 *True* 时，当 start_date 与当前时间之间有未执行的 DAG run 时，会触发 “**back-fill**” 特性，即自动触发这些未执行的 DAG run。

## 3. 数据库与执行器

> **"Even it is called 'EXECUTOR', it doesn't execute your tasks."**
> <br/>-- by the instructor

执行器定义了在何种环境下，如何执行任务。例如本地执行器，远程执行器。它们可以线性执行任务，也可在集群上并行执行任务。

### 3.1 Sequential Executor

airflow的默认执行器，在本地运行，一次一个任务，依次执行。

需要在 airflow.cfg 中配置 `executor=SequentialExecutor`，同时使用 SQLite 作为 airflow 的后台数据库。

### 3.2 Local Executor

本地运行，可以并行执行任务。

需要在 airflow.cfg 中配置 `executor=LocalExecutor`，同时使用 PostgreSQL、MySQL 等等其他数据库作为 airflow 的后台数据库。

### 3.3 Celery Executor

Celery 是一个分布式的任务队列。

可以并行执行任务，任务运行在 Celery 集群上。 集群中除了 Airflow 固有的 Web Server、Scheduler 和数据库之外，还有多个 Worker 节点以及一个消息队列。

#### 3.3.1 Celery 组件

Celery 主要由一个 broker 和 一个 result backend 组成。Broker 用于接收任务，result backend 用于记录运行结果。

使用 Celery executor 的好处是 Airflow scheduler 可以将任务分发到多个 worker 上并行运行。分发机制如下：

1. Airflow scheduler 将任务发布至 Celery broker
2. Worker 从 broker 处获取到任务并执行
3. Worker 将结果返回到 result backend
4. Airflow scheduler 获取到任务执行的状态，在后台数据库和 web server 上显示

使用 Celery executor 需要配置：
1. core.executor='CeleryExecutor'
2. database.sql_alchemy_conn='{database_connection_string}'
3. celery.result_backend='{database_connection_string}'
4. celery.broker_url='{broker_url}'

#### 3.3.2 消息队列

消息队列，顾名思义，就是一个用来给消息排队的机制。在 Airflow 的语境中，队列中存放的是一个个的任务。默认地，按照先进先出的原则，队列中的任务被各 worker 节点提取并执行。

特别地，我们可以根据 worker 节点的特点，为不同的消息队列选择默认的 worker。例如可以将计算密集型的任务都分发到特定的队列，最终被 CPU 资源丰富的 worker 所消费。