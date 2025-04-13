import psycopg as psy
import datetime as dt
import threading as th
import barcode
from barcode.writer import ImageWriter
import random
from collections import defaultdict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib.units import inch, mm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import os
import tempfile
import shutil
import subprocess
from dotenv import load_dotenv
import os

load_dotenv()


def auto():
    db_configs={
        "db1":{"dbname": os.getenv("DB_NAME"),"user": os.getenv("DB_USER"),"password": os.getenv("DB_PASS"),"host": os.getenv("DB_HOST"),"port": int(os.getenv("DB_PORT"))},
        "db2":{"dbname": os.getenv("DB_NAME2"),"user": os.getenv("DB_USER"),"password": os.getenv("DB_PASS"),"host": os.getenv("DB_HOST"),"port": int(os.getenv("DB_PORT"))}
        }
    def get_conn(db_key):
        return psy.connect(**db_configs[db_key])#dictは**をつけて解法しないと引数として渡せない

    with get_conn("db2") as conn2:
        with conn2.cursor() as cur2:
            
            #作業計画に登録されたデータを抜き出す（2日分のデータ）
            
            cur2.execute("select * from project_date where issued_status='未' and record_date BETWEEN current_date and current_date + INTERVAL '2 days'")#今日から2日後以内の開始データを取得
            projectdate_list=cur2.fetchall()#project_dateテーブルから必要なデータが入っている
            project_list=[i[1] for i in projectdate_list]#製品名のリスト

            placeholders=",".join(["%s"]*len(project_list))#製品名の数ぶん%sを作る

            if len(project_list) == 0:
                return None

            query=f"""
                    select product.product_name, parts.parts_name,
                        parts.dimension_value, parts.magni, process.process_name,
                        part_process_map.procedure
                    from product
                    inner join parts on product.id = parts.product_id
                    inner join part_process_map on parts.id=part_process_map.parts_id
                    inner join process on part_process_map.process_id=process.id
                    where product.product_name in ({placeholders})
                    order by product.product_name,parts.parts_name,part_process_map.procedure"""
        
        
            cur2.execute(query,project_list)
            data_a=cur2.fetchall()#[製品名、作業名、寸法、作業倍率、工程名、作業順]
            
            grouped=defaultdict(list)#grouped[key]を設定したら自動的に[]空リストを生成
            for i in data_a:
                key=(i[0],i[1])
                grouped[key].append(i)#{i[0].i[1]:i}という辞書の形ができる、keyの中身が同じときはvalueに追加、keyの中身が変わった時に新しいkeyとvalueを作成していく
            
            result=[]
            image_list=list()
            for z in range(len(projectdate_list)):#projectdate_listのインデックス分繰り返し
                b=projectdate_list[z]#変数bには[id、製品名、開始日時、完了日時、ロットナンバー、ロット数、未処理]
                for i in grouped.values():#groupedのkey[製品名][作業名]、value[data_a]のvalueの方が[()]この形で入る
                    
                    random_code="".join([str(random.randint(0,9)) for _ in range(12)])
                    code128=barcode.get_barcode_class("code128")
                    barcode_obj=code128(random_code,writer=ImageWriter())
                    filename="random_barcode.png"
                    barcode_obj.save(filename)
                    with open(filename,"rb") as file:
                        binary_data=file.read()
                    file_list=(random_code,)#binary_data)
                    image_data=(random_code,binary_data)
                    image_list.append(image_data)
                    
                    for x in range(len(i)):#xには[(value)]の形のインデックスが入る
                        a=list(i[x])#grouped.values()を[value]の形に変えている
                        a.extend(list(file_list))
                        if i[x][0] in b:#[value]の中の製品名がbに含まれている場合のみ実行
                            for q in b[2:]:#qにはbのインデックス2以降のデータ(開始、終了、lot_no等）が順番に入ってaに追加されていく
                                a.append(q)#[製品名、作業名、寸法、倍率、工程、順番、バーコード、開始、終了、lot_no、lot数、未着手]
                                
                            a[11]="未着手"
                            a.pop(10)
                                
                            result.append(a)
                            
            product_val=defaultdict(int)
            ###作業数量設定のための処理
            for i in projectdate_list:
                product_val[i[1]]=i[5]
            for i in product_val:
                for x in range(len(result)):
                    if i == result[x][0] and result[x][5] == 1:
                        result[x][3]=int(product_val[i]*result[x][3])
                    elif i == result[x][0] and result[x][5] !=1:
                        result[x][3]=0
            
            projectdate_comp=[None]*len(projectdate_list)
            for i in range(len(projectdate_list)):#済に変換して新しいリストを作り、そのリストをproject_dateにupdateする
                projectdate_comp[i]=list(projectdate_list[i])
                projectdate_comp[i][6]="済"
                projectdate_comp[i].append(projectdate_comp[i].pop(0))
            pro_id=[("済",i[6]) for i in projectdate_comp]
            ###project_dateテーブルをアップデートしてstatusを済状態にする
        
            cur2.executemany("""update project_date set issued_status=%s where
                            id=%s""",pro_id)

            def process_manege(proje="",tas="",dim=""):#,filename="工程管理表.pdf"):
                
                
                with tempfile.NamedTemporaryFile(delete=False,suffix="pdf") as temp_file:
                    temp_filename=temp_file.name
                    
                pdf_canvas=set_infomation(temp_filename)
                print_data(pdf_canvas,proje,tas,dim)
                pdf_canvas.save()
                ###印刷処理、プリンター持っていないため実証できず。要実践が重要
                '''
                try:
                    os.system(f"start /min AcroRd32.exe /p /h '{temp_filename}'")
                    os.remove(temp_filename)
                except Exception as e:
                    return
                '''

            def set_infomation(filename):
                pdf_canvas=canvas.Canvas(filename,pagesize=landscape(A5),initialfontSize=10)
                pdf_canvas.setTitle("工程管理表")
                pdf_canvas.setAuthor("atu_hori")
                pdf_canvas.setSubject("工程管理表PDFのテンプレート")
                pdf_canvas.setKeywords("工程,管理,工程管理表,製造")
                return pdf_canvas

            def print_data(pdf_canvas,proje,tas,dim):
                pdfmetrics.registerFont(TTFont('MS Gothic','msgothic.ttc'))
                width,height=pdf_canvas._pagesize
                margin_x=5
                margin_y=height-5
                max_x=width-5
                max_y=5
                text="工程管理表（部品加工）"
                text_width=pdf_canvas.stringWidth(text,"MS Gothic",18)
                pdf_canvas.setFont("MS Gothic",18)
                pdf_canvas.drawString((width-text_width)/2,margin_y-20,'工程管理表（部品加工）')

                data=[
                    ["製品名", f"{proje}", "ID", "", "", "", "", "確認", "承認"],
                    ["作業名", f"{tas}", "寸法", f"{dim}", "", "", "", "", ""],
                    ["材料\nメーカー", "", "材質", "", "", "調達\n識別", "購入", "保管", "倉庫"],
                    ]
                table=Table(data,colWidths=(25*mm,50*mm,15*mm,5*mm,25*mm,20*mm,20*mm,20*mm,20*mm),rowHeights=(13*mm))
                table.setStyle(TableStyle([
                    ('FONT',(0,0),(8,2),'MS Gothic',12),
                    ('BOX',(0,0),(8,2),1,colors.black),
                    ('INNERGRID',(0,0),(8,2),1,colors.black),
                    ('SPAN',(3,0),(6,0)),
                    ('SPAN',(3,1),(6,1)),
                    ('SPAN',(3,2),(4,2)),
                    ('SPAN',(7,0),(7,1)),
                    ('SPAN',(8,0),(8,1)),
                    ('VALIGN',(0,0),(8,2),'MIDDLE')]))
                table.wrapOn(pdf_canvas,5*mm,135*mm)
                table.drawOn(pdf_canvas,5*mm,135*mm-table._height)
                image_path="random_barcode.png"
                pdf_canvas.drawImage(image_path,98*mm,122*mm,width=65*mm,height=12*mm)
                pdf_canvas.showPage()
            print(result)


            for i in result:#len(result)回、一時ファイル作成→印刷の作業を実行
                process_manege(i[0],i[1],i[2])
            
            conn2.commit()
               
        
    with get_conn("db1") as conn1:
        with conn1.cursor() as cur1:
            cur1.executemany("""insert into projectdata
                        (project_name,task_name,dimension_value,work_volume,work_name,
                        work_procedure,barcode_id,start_date,end_date,lot_no,status)
                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        returning *""",result)
            
            cur1.execute("select * from projectdata")
            pro_data=cur1.fetchall()
            
            cur1.executemany("""insert into barcodedata
                (projectid,project_name,task_name,work_name,barcode_id,status,work_volume,
                dimension_value,lot_no,start_date,end_date,work_procedure)
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",pro_data)
            cur1.executemany("""insert into barcode_file
                (barcode_id,barcode_image) values(%s,%s)""",image_list)
            
            conn1.commit()

        
auto()
