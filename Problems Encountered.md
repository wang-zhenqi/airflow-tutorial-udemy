# 遇到过的问题汇总

## 从文件加载数据至MySQL

MySQL 版本：8.0.21

从文件加载数据至MySQL表中，SQL语句：

```mysql
LOAD DATA LOCAL INFILE '/tmp/processed_user.csv'
    INTO TABLE user
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\r';
```

但是由于8.0版本的默认安全设置，直接执行一般会报错：“LOAD DATA LOCAL INFILE file request rejected due to restrictions on
access.”

这是由于MySQL默认将“从文件加载数据”功能关闭了。需要在服务器端和客户端都做调整：

1. 服务器端：`SET GLOBAL local_infile = 1;`
2. 客户端：
    1. DataGrip：在连接设置->高级中，将‘AllowLoadLocalInfile’设为‘true’;
    2. Airflow Connection: 在extra中添加`{"local_infile": true}`

## Scheduler 在运行中出现`SIGABRT`报错

该问题会在 MacOS High Sierra 及以上版本出现，这是由于 MacOS 添加了对于多进程、多线程的安全限制。
解决方案：

```shell
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

## 从 Docker container 连接至宿主机的 localhost

如果 Airflow 是运行在 docker container 里的，那么在设置 Airflow connection 的时候，如果需要连接运行在宿主机上的服务，需要将通常的
localhost
替换为 `host.docker.internal`。
