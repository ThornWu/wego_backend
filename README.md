### 使用步骤
1. 创建数据库

    目前项目中包含的 “wego.db” 文件为包含所有表的空数据库。一般情况下可以直接跳过此步骤。如果数据库文件出现问题，请使用 SQLite 命令创建数据库，“tables.sql”文件中包含数据库所有表的 SQL 创建语句。
2. 导入数据

    相关外部依赖：csv、sqlite3、numpy、pickle
    ```
    python3 insert_data.py
    ```
3. 运行程序

    相关外部依赖：bottle、sqlite3、numpy、pickle、csv
    ```
    python3 backend.py
    ```
