import tkinter as tk
from tkinter import ttk
import psycopg as psy
import datetime as dt
from PIL import Image, ImageTk
import barcode
from barcode.writer import ImageWriter
import io
import os
from tkinter import messagebox
from dotenv import load_dotenv
import os

load_dotenv()


root=tk.Tk()
root.title("作業バーコード")
root.geometry("200x200")
root.resizable(width=False,height=False)
        

def push_e(event):
    conn=psy.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
            )
    cur=conn.cursor()
    
    work=work_combo.get()
    try:
        bar_id=str(barcode_entry.get())
    except ValueError:
        tk.messagebox.showerror("バーコードデータが一致しません")
        return None
    barcode_entry.delete(0,tk.END)

    """-------------------------------

    barcodedataテーブルに登録されているデータを取り出し工程管理表に反映させる

    -------------------------------"""
    cur.execute("select * from barcodedata where barcode_id=%s",(bar_id,))
    barcodedata_list=cur.fetchall()#入力されたバーコードに対応する製品データをリストとして取得
    barcodedata_list=sorted(barcodedata_list,key=lambda x: x[19])#データの並び替え、作業の順番に合わせて降順
    works_list=[i[4] for i in barcodedata_list]#projectに対するすべてのworkを抜き出す
    works_list=list(dict.fromkeys(works_list))
    try:
        real_procedure=works_list.index(work)
    except ValueError as e:
        tk.messagebox.showerror("エラー","正しい工程が選択されている、\nまたは正しいバーコードが入力されているか確かめてください")
        cur.close()
        conn.close()
        return
    last_status=""
    if real_procedure > 0:#indexが０（最初の工程）の場合は発生せず、last_status=""のまま０以上の時前工程のstatusを取り込む
        last_status=barcodedata_list[real_procedure-1][6]
    if last_status == "未着手":#前工程が未着手の場合発生
        tk.messagebox.showerror("エラー","前工程の作業が始まっていません")
        cur.close()
        conn.close()
        return None
        

    """-------------------------------

    工程管理表作成に必要なデータをprojectdataテーブルから取り出す

    -------------------------------"""
    cur.execute("select * from projectdata where barcode_id=%s",(bar_id,))#バーコードIDに関連したデータをすべてリスト化
    projectdata_list=cur.fetchall()#バーコードを元に抜き出した情報が入っている 
    projectwork_list=[i for i in projectdata_list if work in i]#選択された工程名が含まれたデータを抜き出す
    try:
        projectwork_list=list(projectwork_list[0])#タプルからリスト化
    except IndexError:
        cur.close()
        conn.close()
        return None

    ###バーコードの設定
    code = str(bar_id)  # バーコードの内容（JANコードなど）
    ean = barcode.get("ean13", code, writer=ImageWriter())
    
    filename = ean.save("barcode.png")
    img = Image.open(filename)
    img = img.resize((200, 40))  # サイズ調整
    img = ImageTk.PhotoImage(img)
    
    ##
    """-------------------------------

    登録ボタンの関数設定

    -------------------------------"""
    def record():#登録ボタンのコマンド設定
        work_index=works_list.index(work)
        if work_index > 0:
            prior_status=barcodedata_list[work_index-1][6]
            if prior_status == "未着手":
                tk.messagebox.showerror("エラー","前工程の作業データが登録されていません")
                return None
            
        
        record_list=list(zip(macnum_box,workvol_box,goodpro_box,defeitems_box,worker_box,text_box))#リスト化されているエントリーをzip関数でまとめて取得。リスト化されているエントリーは縦軸のまとまりになるがzip関数を使うことで横軸（work名)のまとまりに変えることができる
        
        
        record_data=record_list[work_index]#zip関数でまとめ方を変えたリストの中から、書き込み可能になっているwork名のインデックスを取得
        record_data=[record_data[i].get() for i in range(len(record_data))]#取得したインデックスに入力されている値のみを新しくリスト化
        if "" in record_data[1:5]:
            tk.messagebox.showerror("エラー","正しいデータ入力が確認できていません")
            return None
        materia=materialid_entry.get()
        timestamp=dt.datetime.now()
        sta=""
        if int(record_data[1]) == int(record_data[2])+int(record_data[3]):
            sta="完了"
        elif int(record_data[1]) > int(record_data[2])+int(record_data[3]):
            sta="作業中"
        elif int(record_data[1]) < int(record_data[2])+int(record_data[3]):
            tk.messagebox.showerror("エラー","作業数量をオーバーしています")
            #print("作業数オーバー",record_data[1],record_data[2],record_data[3])
            return None
        addition_list=[materia,timestamp,sta]
        record_data.extend(addition_list)
        updatebarcode_list=record_data.copy()
        real_id=barcodedata_list[work_index][0]
        record_data.append(real_id)
        cur.execute("""update barcodedata set machine_number=%s,work_volume=%s,
                    goodproduct_volume=%s,defectiveitems_number=%s,
                    worker=%s,special_notes=%s,material_number=%s,
                    end_time_date=%s,status=%s where id=%s""",record_data)
        dataindex_list=[10,7,11,12,13,14,9,20,6]#record_dataに入っている各データのデータベースに対応するインデックスを設定
        updatebarcode_dict={x:updatebarcode_list[i] for i , x in enumerate(dataindex_list)}
        
        update_list=[None]*len(barcodedata_list[work_index])
        for i , x in enumerate(barcodedata_list[work_index]):
            if i in dataindex_list:
                update_list[i]=updatebarcode_dict[i]
            else:
                update_list[i]=x
        update_list.append(timestamp)
        update_list.pop(0)
        cur.execute("""insert into update_history
                    (projectid,project_name,task_name,work_name,barcode_id,status,work_volume,
                    dimension_value,material_number,machine_number,goodproduct_volume,
                    defectiveitems_number,worker,special_notes,lot_no,start_date,end_date,
                    progress_data,work_procedure,end_time_date,update_at)
                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",update_list)
        conn.commit()

    """-------------------------------

    各種ウィジェット設定

    -------------------------------"""
    font12=("","12","bold")
    font10=("","10","bold")
    project=projectdata_list[0][1]#必要なプロジェクト名
    task=projectdata_list[0][2]#必要なタスク名
    dimension=projectdata_list[0][7]#必要な寸法
    workvolume=projectdata_list[0][6]#スタート工程に入力される作業数
    workprocess_top=tk.Toplevel()#工程管理表画面の作成
    workprocess_top.title("工程管理表")
    workprocess_top.geometry("660x400")
    workprocess_top.resizable(width=False,height=False)
    workprocess_top.config(bg="white")
    project_frame=tk.Frame(workprocess_top)
    project_frame.pack()
    info_frame=tk.Frame(workprocess_top)
    info_frame.pack()
    work_frame=tk.Frame(workprocess_top)
    work_frame.pack()
    seihin_label=tk.Label(project_frame,width=8,text="製品名",relief=tk.SOLID,bd=2,font=("","12","bold"))
    seihin_label.grid(row=0,column=0,padx=2)
    project_label=tk.Label(project_frame,width=15,text=project,bg="white",relief=tk.SOLID,bd=2,font=("","20","bold"))
    project_label.grid(row=0,column=1,padx=2)
    label = tk.Label(project_frame,relief=tk.SUNKEN,bd=2)  # バーコード表示用ラベル
    label.grid(row=0,column=2,padx=2)
    label.config(image=img)
    label.image = img
    task_label=tk.Label(info_frame,width=30,text=task,font=font12,relief=tk.SOLID,bd=2)
    task_label.grid(row=0,column=0,padx=2)
    dimension_label=tk.Label(info_frame,width=30,text=dimension,relief=tk.SOLID,bd=2,font=font12)
    dimension_label.grid(row=0,column=1,padx=2)
    materialid_label=tk.Label(work_frame,width=10,text="材料ロット",relief=tk.SUNKEN,bd=2,font=font10)
    materialid_label.grid(row=0,column=0,padx=2)
    materialid_entry=tk.Entry(work_frame,width=60,state="readonly",relief=tk.SOLID,bd=2,font=font12)
    materialid_entry.grid(row=0,column=1,columnspan=8)
    work_box,macnum_box,workvol_box,goodpro_box,defeitems_box,worker_box,text_box=[[None] * len(works_list) for _ in range(7)]#work_box=[None]*7,macnum_box=[None]*7等を一括作成
    workname_label=tk.Label(work_frame,width=10,text="工程名",relief=tk.SUNKEN,bd=2,font=font10)
    workname_label.grid(row=1,column=0,padx=2,pady=2)
    macnum_label=tk.Label(work_frame,width=5,text="号機",relief=tk.SUNKEN,bd=2,font=font10)
    macnum_label.grid(row=1,column=1,padx=2)
    workvol_label=tk.Label(work_frame,width=5,text="作業数",relief=tk.SUNKEN,bd=2,font=font10)
    workvol_label.grid(row=1,column=2,padx=2)
    goodpro_label=tk.Label(work_frame,width=5,text="良品数",relief=tk.SUNKEN,bd=2,font=font10)
    goodpro_label.grid(row=1,column=3,padx=2)
    defeitems_label=tk.Label(work_frame,width=5,text="不良数",relief=tk.SUNKEN,bd=2,font=font10)
    defeitems_label.grid(row=1,column=4,padx=2)
    worker_label=tk.Label(work_frame,width=20,text="作業者名",relief=tk.SUNKEN,bd=2,font=font10)
    worker_label.grid(row=1,column=5,padx=2)
    text_label=tk.Label(work_frame,width=25,text="コメント",relief=tk.SUNKEN,bd=2,font=font10)
    text_label.grid(row=1,column=6,padx=2)
    row_count=4
    goodpro=None
    
    for i in range(len(works_list)):
        if works_list.index(work)==0 and barcodedata_list[i][9] == None:
            materialid_entry.config(state="normal")
            
        elif works_list.index(work) == 0 and barcodedata_list[i][9] != None:
            materialid_entry.config(state="normal")
            materialid_entry.delete(0,tk.END)
            materialid_entry.insert(0,barcodedata_list[i][9])
            
        elif works_list.index(work) != 0 and barcodedata_list[i][9] != None:
            materialid_entry.config(state="normal")
            materialid_entry.delete(0,tk.END)
            materialid_entry.insert(0,barcodedata_list[i][9])
            materialid_entry.config(state="readonly")
            
        elif works_list.index(work) != 0 and barcodedata_list[i][9] == None:
            materialid_entry.config(state="readonly")
            
        work_box[i]=tk.Label(work_frame,width=10,text=works_list[i],relief=tk.SUNKEN,bd=2,font=font10)
        work_box[i].grid(row=2+i,column=0,padx=2,pady=2)
        macnum_box[i]=tk.Entry(work_frame,width=5,state="disabled",relief=tk.SUNKEN,bd=2,font=font10)
        macnum_box[i].grid(row=2+i,column=1,padx=2)
        if barcodedata_list[i][10] != None:
            macnum_box[i].config(state="normal")
            macnum_box[i].delete(0,tk.END)
            macnum_box[i].insert(0,barcodedata_list[i][10])
            macnum_box[i].config(state="disabled")
        workvol_box[i]=tk.Entry(work_frame,width=5,state="disabled",relief=tk.SUNKEN,bd=2,font=font10)
        workvol_box[i].grid(row=2+i,column=2,padx=2)
        
        if barcodedata_list[i][7] != None:#データベースに作業数が登録されているならデータを反映
            workvol_box[i].config(state="normal")
            workvol_box[i].delete(0,tk.END)
            workvol_box[i].insert(0,barcodedata_list[i][7])
            workvol_box[i].config(state="disabled")
        if works_list[i] == work and i > 0:#選択された工程名の作業順が1以上な場合、前工程の良品数を現工程の作業数に反映
            workvol_box[i].config(state="normal")
            workvol_box[i].delete(0,tk.END)
            workvol_box[i].insert(0,goodpro)
            workvol_box[i].config(state="disabled")
        
        goodpro_box[i]=tk.Entry(work_frame,width=5,state="disabled",relief=tk.SUNKEN,bd=2,font=font10)
        goodpro_box[i].grid(row=2+i,column=3,padx=2)
        if barcodedata_list[i][11] != None:
            goodpro_box[i].config(state="normal")
            goodpro_box[i].delete(0,tk.END)
            goodpro_box[i].insert(0,barcodedata_list[i][11])
            goodpro_box[i].config(state="disabled")
            goodpro=goodpro_box[i].get()
        defeitems_box[i]=tk.Entry(work_frame,width=5,state="disabled",relief=tk.SUNKEN,bd=2,font=font10)
        defeitems_box[i].grid(row=2+i,column=4,padx=2)
        if barcodedata_list[i][12] != None:
            defeitems_box[i].config(state="normal")
            defeitems_box[i].delete(0,tk.END)
            defeitems_box[i].insert(0,barcodedata_list[i][12])
            defeitems_box[i].config(state="disabled")      
        worker_box[i]=tk.Entry(work_frame,width=20,state="disabled",relief=tk.SUNKEN,bd=2,font=font10)
        worker_box[i].grid(row=2+i,column=5,padx=2)
        if barcodedata_list[i][13] != None:
            worker_box[i].config(state="normal")
            worker_box[i].delete(0,tk.END)
            worker_box[i].insert(0,barcodedata_list[i][13])
            worker_box[i].config(state="disabled")
        text_box[i]=tk.Entry(work_frame,width=25,state="disabled",relief=tk.SUNKEN,bd=2,font=font10)
        text_box[i].grid(row=2+i,column=6,padx=2)
        if barcodedata_list[i][14] != None:
            text_box[i].config(state="normal")
            text_box[i].delete(0,tk.END)
            text_box[i].insert(0,barcodedata_list[i][14])
            text_box[i].config(state="disabled")
        row_count+=1#buttonの位置を決めるために必要
        if work_box[i]["text"] == work:#ラベル変数["text"]の書式でラベルウィジェットに格納されているtext値を取得できる、text値に対応する入力欄を書込み可能にする
            macnum_box[i].config(state="normal")
            workvol_box[i].config(state="normal")
            goodpro_box[i].config(state="normal")
            defeitems_box[i].config(state="normal")
            worker_box[i].config(state="normal")
            text_box[i].config(state="normal")
    record_button=tk.Button(work_frame,width=5,text="登録",command=record,relief=tk.RAISED,bd=2,font=font10)
    record_button.grid(row=row_count,column=6)
    

work_list=["プレス","前処理","整備","塗装1号","塗装2号","マスキング",
           "ライン梱包","タレパン","オートマ","組み立て","溶接",
           "ベンダー","サルバ","スポット","梱包","シャーリング"]
combo_frame=tk.Frame(root)
combo_frame.pack()
work_var=tk.StringVar()
work_combo=ttk.Combobox(combo_frame,width=20,values=work_list,textvariable=work_var)
work_combo.pack()
entry_frame=tk.Frame(root)
entry_frame.pack()
barcode_entry=tk.Entry(entry_frame,width=20)
barcode_entry.pack()
barcode_entry.bind('<Return>',push_e)


root.mainloop()
