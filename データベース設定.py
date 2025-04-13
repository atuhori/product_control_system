import psycopg as psy
from dotenv import load_dotenv
import os

load_dotenv()

conn=psy.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
            )
cur=conn.cursor()
cur.execute("drop table projectdata")
cur.execute("drop table barcodedata")
cur.execute("drop table update_history")
cur.execute("drop table barcode_file")
table_list=["""create table if not exists projectdata(
            projectid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            project_name TEXT NOT NULL,
            task_name TEXT NOT NULL,
            work_name TEXT NOT NULL,
            barcode_id TEXT NOT NULL,
            status VARCHAR(5) NOT NULL,
            work_volume SMALLINT,
            dimension_value TEXT,
            lot_no TEXT,
            start_date DATE,
            end_date DATE,
            work_procedure SMALLINT)"""         
            ,
            """create table if not exists barcodedata(
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            projectid INTEGER,
            project_name TEXT NOT NULL,
            task_name TEXT NOT NULL,
            work_name TEXT NOT NULL,
            barcode_id TEXT NOT NULL,
            status VARCHAR(5) NOT NULL,
            work_volume SMALLINT,
            dimension_value TEXT,
            material_number TEXT,
            machine_number TEXT,
            goodproduct_volume SMALLINT,
            defectiveitems_number SMALLINT,
            worker TEXT,
            special_notes TEXT,
            lot_no TEXT,
            start_date DATE,
            end_date DATE,
            progress_data INTEGER,
            work_procedure INTEGER,
            end_time_date TIMESTAMP
            )"""          
            ,
            """create table if not exists update_history(
            updateid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            projectid INTEGER,
            project_name TEXT NOT NULL,
            task_name TEXT NOT NULL,
            work_name TEXT NOT NULL,
            barcode_id BIGINT NOT NULL,
            status VARCHAR(5) NOT NULL,
            work_volume SMALLINT,
            dimension_value TEXT,
            material_number TEXT,
            machine_number TEXT,
            goodproduct_volume SMALLINT,
            defectiveitems_number SMALLINT,
            worker TEXT,
            special_notes TEXT,
            lot_no TEXT,
            start_date DATE,
            end_date DATE,
            progress_data INTEGER,
            work_procedure INTEGER,
            end_time_date TIMESTAMP,
            update_at TIMESTAMP)"""
            ,
            """create table if not exists barcode_file(
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            barcode_id BIGINT NOT NULL,
            barcode_image BYTEA)"""
            ]
for i in table_list:
    cur.execute(i)
cur.execute("select * from barcodedata")
bb=cur.fetchall()
print(len(bb))
cur.execute("select * from update_history")
aa=cur.fetchall()
print(len(aa))
conn.commit()
cur.close()
conn.close()
