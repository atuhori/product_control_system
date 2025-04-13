import psycopg as psy
from dotenv import load_dotenv
import os

load_dotenv()

conn=psy.connect(
            dbname=os.getenv("DB_NAME2"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
            )
cur=conn.cursor()



cur.execute("drop table project_date")
cur.execute("drop table product")
cur.execute("drop table parts")
cur.execute("drop table process")
cur.execute("drop table part_process_map")
cur.execute("drop table barcode_file")


cur.execute("""
    CREATE TABLE IF NOT EXISTS project_date (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        product TEXT NOT NULL,
        record_date DATE NOT NULL,
        end_date DATE NOT NULL,
        lot_no TEXT,
        lot_count INTEGER CHECK (lot_count >= 0), -- ロット数は負にならない想定
        issued_status TEXT CHECK (issued_status IN ('済', '未'))
    )
""")#valueにはロット数checkには済か未（発行済と未発行）
cur.execute("""create table if not exists product
            (id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            product_name TEXT)""")

cur.execute("""create table if not exists parts
            (id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            parts_name TEXT,product_id INTEGER,dimension_value TEXT,magni REAL)""")

cur.execute("""create table if not exists process
            (id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            process_name TEXT)""")

cur.execute("""create table if not exists part_process_map
            (id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            process_id SMALLINT,parts_id INTEGER,procedure SMALLINT)""")

cur.execute("""create table if not exists barcode_file
            (id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            barcode_data BIGINT,image BYTEA)""")
a=[("dl-05","2025-4-1","2025-4-20","5D20",50,"未"),("spl","2025-4-5","2025-4-20","5D20",20,"未"),
   ("kd1x1","2025-3-30","2025-4-20","5D20",50,"未"),("kd1x4","2025-4-5","2025-4-20","5D20",50,"未"),
   ("kl-h33","2025-3-25","2025-4-4","5D04",10,"未"),("kd1x1","2025-3-25","2025-4-2","5D02",50,"未"),
   ("ssw","2025-3-27","2025-4-19","5D01",33,"未"),("spl","2025-4-12","2025-4-22","5D22",20,"未"),
   ("spl","2025-3-31","2025-4-20","5D20",20,"未"),("kd1x1","2025-4-10","2025-4-15","250415",50,"未"),
   ("dl-05","2025-4-13","2025-4-20","200420",50,"未"),("ssw","2025-4-12","2025-4-18","5D18",23,"未"),
   ("spl","2025-4-12","2025-4-20","5D20",30,"未")]
b=[("dl-05",),("spl",),("kd1x1",),("kd1x4",),("kl-h33",),("ssw",)]
c=[("天板",1,"400x500x200",1),("底板",1,"400x500x200",1),("横仕切り",2,"400x500x200",2),
   ("扉",2,"400x500x200",4),("右背板",2,"400x500x200",1),("左背板",2,"400x500x200",1),
   ("右側板",3,"400x500x200",5),("左側板",3,"400x500x200",1),("棚板",1,"400x500x200",1),
   ("アジャスター版",2,"400x500x200",2),("縦仕切り",2,"400x500x200",1),("背板",4,"100x200x300",1),
   ("天板",5,"10x10x100",1),("本体",5,"無し",1),("扉",6,"3x3x3",10),("棚補強",6,"330x39x1",30)]
d=[("プレス",),("前処理",),("整備",),("塗装1号",),("塗装2号",),("マスキング",),
   ("ライン梱包",),("タレパン",),("オートマ",),("組み立て",),("溶接",),
   ("ベンダー",),("サルバ",),("スポット",),("梱包",),("シャーリング",)]
e=[(1,1,1),(1,2,3),(1,7,1),(1,8,1),(1,9,1),(1,12,6),(2,1,2),(2,2,1),
   (2,3,3),(2,4,1),(2,5,5),(2,6,6),(2,7,2),(2,8,2),(2,10,9),(2,11,10),(3,1,4),(3,2,2),(11,3,1),
   (3,4,3),(3,12,4),(3,7,3),(3,8,3),(4,1,3),(4,2,2),(4,3,3),(4,4,2),(4,12,5),(4,7,4),(4,8,4),
   (2,13,1),(3,14,1),(1,15,1),(8,15,2),(9,15,3),(2,15,4),(3,15,5),(8,16,1),(12,16,2),(14,16,3)]
cur.executemany("insert into project_date(product,record_date,end_date,lot_no,lot_count,issued_status) values(%s,%s,%s,%s,%s,%s)",a)
cur.executemany("insert into product(product_name) values(%s)",b)
cur.executemany("insert into parts(parts_name,product_id,dimension_value,magni) values(%s,%s,%s,%s)",c)
cur.executemany("insert into process(process_name) values(%s)",d)
cur.executemany("insert into part_process_map(process_id,parts_id,procedure) values(%s,%s,%s)",e)

conn.commit()
cur.close()
conn.close()
