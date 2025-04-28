# -*- coding: utf-8 -*-
"""
数据库相关的管理，主要是记录哪些文件已经被发送，哪些文件没有发送。
采用sqlite3作为数据库引擎，使用pandas作为数据处理库。
"""
import sqlite3
import pandas as pd
import os

def createDB(dbFile):
    '''
    创建数据库，数据库存在则不创建
    # 测试
    createDB(db_file) # 创建数据库
    '''
    # 创建数据库和数据表格形式
    # 如果数据库不存在就创建一个数据库，并创建相应的表格OLDFILES、SENTFILES
    if os.path.exists(dbFile):
        print("Database existed.")
    else:
        if not os.path.exists(os.path.dirname(dbFile)):
            os.makedirs(os.path.dirname(dbFile))
        conn = sqlite3.connect(dbFile)  # 如果数据库不存在，会自动创建一个
        conn.commit()
        conn.close()

class dbOperate:
    def __init__(self, dbFile):
        # 构造函数的逻辑，使用传入的 db_file 参数
        self.db_file = dbFile
        createDB(dbFile)
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.db_file)  # 如果数据库不存在，会自动创建一个
        self.conn.commit()
        self.cursor = self.conn.cursor()

    def close(self):
        '''关闭数据库连接'''
        self.conn.close()

    def create_table(self, table_name, columns):
        '''
        在指定的db数据库上创建表格，如果表格存在，则放弃

        # 测试
        db_file = 'database/mydatabase.db' # 数据库文件路径
        table_name = 'old' # 表格名称
        columns = ['id INTEGER PRIMARY KEY', 'name TEXT', 'age INTEGER'] # 列名列表
        createDB(db_file) # 创建数据库
        create_table(db_file, table_name, columns) # 创建表格

        '''
        # 检查表格是否已存在
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        result = self.cursor.fetchone()
        if result:
            print(f"表格 {table_name} 已存在，跳过创建步骤")
            # 可以在此处添加其他操作
        else:
            # 构建创建表格的SQL语句
            columns_str = ', '.join(columns)
            create_table_sql = f"CREATE TABLE {table_name} ({columns_str})"

            # 执行创建表格的SQL语句
            self.cursor.execute(create_table_sql)
            print(f"创建表格 {table_name} 成功")

            # 可以在此处添加其他操作

        # 提交事务
        self.conn.commit()

    def getDbData(self, table_name, PATHcol=True):
        '''
        提取表格信息PATH
        '''
        # 提取表格
        data = pd.read_sql(f"SELECT * FROM {table_name}", con=self.conn)
        if PATHcol:
            data = list(data['PATH'].unique())
        return data

    def insertData(self, table_name, data):
        '''
        插入数据
        '''
        # 构建插入数据的SQL语句
        placeholders = ', '.join(['?'] * len(data))
        insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

        # 执行插入数据的SQL语句
        self.cursor.execute(insert_sql, data)
        self.conn.commit()
        # print("数据插入成功")

    def check_file_exists(self, table_name, file_path):
        '''
        检查文件是否在表格中已经存在
        '''
        # 执行查询文件的SQL语句
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE path=?", (file_path,))
        result = self.cursor.fetchone()
        exists = result[0] > 0
        print('数据存在')
        return exists
# ==================================================================================================
# test
# ==================================================================================================
# # 数据库文件路径
# db_file = r'database/testdatabase.db'
#
# dbase = dbOperate(db_file)
#
# # 创建OLDFILES
# dbase.create_table(table_name='OLDFILES',
#              columns=['PATH TEXT', 'TIME DATETIME', 'NAME TEXT']) # 创建表格
# # 创建SENTFILES
# dbase.create_table(table_name='SENTFILES',
#              columns=['PATH TEXT', 'TIME DATETIME', 'NAME TEXT']) # 创建表格
#
# # 向OLDFILES表格插入数据
# table_name = 'OLDFILES'
# data = ('/path/to/oldfile.txt', '2021-01-01 10:30:00', 'oldfile.txt')
# dbase.insertData(table_name, data)
#
# # 向SENTFILES表格插入数据
# table_name = 'SENTFILES'
# data = ('/path/to/sentfile.txt', '2021-07-01 15:45:00', 'sentfile.txt')
# dbase.insertData(table_name, data)
#
# # 检查数据库里的数据是否存在
# dbase.check_file_exists(table_name='SENTFILES', file_path='/path/to/sentfile.txt')
