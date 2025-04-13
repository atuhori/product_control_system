import tkinter as tk
from tkinter import ttk
import psycopg as psy
import pandas as pd
from datetime import datetime
from tkinter import messagebox
from dotenv import load_dotenv
import os

load_dotenv()



root=tk.Tk()
root.title("データ追跡ソフト")
root.geometry("400x500")
root.resizable(width=False,height=False)

def tree_select(event):
    try:
        conn=psy.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
            )
        cur=conn.cursor()
    except psy.OperationalError as e:
        tk.messaggebox.showerror("データベース接続エラー",f"\nエラー名{e}")
        cur.close()
        conn.close()
        return
    tree_id=search_tree.focus()
    value=search_tree.item(tree_id,"values")
    if not value or len(value) !=4:
        return
    try:
        cur.execute("select * from update_history where (project_name=%s and task_name=%s and barcode_id=%s and lot_no=%s and status='完了')",value)
    except TypeError:
        return
    process_control_data=cur.fetchall()
    pcl=sorted(process_control_data,key=lambda x: x[21],reverse=True)
    pcl=sorted(pcl,key=lambda x: x[19])
    
    works_list=[i[4] for i in process_control_data]
    works_list=list(dict.fromkeys(works_list))

    #pandasを使って特定のインデックスの値（この場合はbarcode_id）の重複を解除、一番最後のデータを残す
    font12=("","12","bold")
    font10=("","10","bold")
    time_list=[pd.Timestamp(i[20]) for i in pcl]
    entry_time=[i.date() for i in time_list]
                                 
    process_control_sheet=tk.Toplevel()
    process_control_sheet.title("工程管理表")
    process_control_sheet.geometry("800x400")
    process_control_sheet.resizable(width=False,height=False)
    process_control_sheet.config(bg="white")
    project_frame=tk.Frame(process_control_sheet)
    project_frame.pack()
    info_frame=tk.Frame(process_control_sheet)
    info_frame.pack()
    work_frame=tk.Frame(process_control_sheet)
    work_frame.pack()
    seihin_label=tk.Label(project_frame,width=8,text="製品名",relief=tk.SOLID,bd=2,font=font12)
    seihin_label.grid(row=0,column=0,padx=2)
    project_label=tk.Label(project_frame,width=15,text=pcl[0][2],bg="white",relief=tk.SOLID,bd=2,font=("","20","bold"))
    project_label.grid(row=0,column=1,padx=2)
    barcode_label=tk.Label(project_frame,width=15,text=pcl[0][5],bg="white",relief=tk.SOLID,bd=2,font=("","20","bold"))
    barcode_label.grid(row=0,column=2,padx=2)
    task_label=tk.Label(info_frame,width=30,text=pcl[0][3],font=font12,relief=tk.SOLID,bd=2)
    task_label.grid(row=0,column=0,padx=2)
    dimension_label=tk.Label(info_frame,width=30,text=pcl[0][8],relief=tk.SOLID,bd=2,font=font12)
    dimension_label.grid(row=0,column=1,padx=2)
    materialid_label=tk.Label(work_frame,width=10,text="材料ロット",relief=tk.SUNKEN,bd=2,font=font10)
    materialid_label.grid(row=0,column=0,padx=2)
    materialid_entry=tk.Entry(work_frame,width=60,relief=tk.SOLID,bd=2,font=font12)
    materialid_entry.grid(row=0,column=1,columnspan=8,sticky=tk.W)
    materialid_entry.insert(0,pcl[0][9])
    materialid_entry.config(state="readonly")
    work_box,macnum_box,workvol_box,goodpro_box,defeitems_box,worker_box,time_box,text_box=[[None] * len(works_list) for _ in range(8)]#work_box=[None]*7,macnum_box=[None]*7等を一括作成
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
    time_label=tk.Label(work_frame,width=15,text="作業日",relief=tk.SUNKEN,bd=2,font=font10)
    time_label.grid(row=1,column=6,padx=2)
    text_label=tk.Label(work_frame,width=25,text="コメント",relief=tk.SUNKEN,bd=2,font=font10)
    text_label.grid(row=1,column=7,padx=2)
    for i in range(len(works_list)):
        work_box[i]=tk.Label(work_frame,width=10,text=works_list[i],relief=tk.SUNKEN,bd=2,font=font10)
        work_box[i].grid(row=2+i,column=0,padx=2,pady=2)
        macnum_box[i]=tk.Entry(work_frame,width=5,relief=tk.SUNKEN,bd=2,font=font10)
        macnum_box[i].grid(row=2+i,column=1,padx=2)
        macnum_box[i].insert(0,pcl[i][10])
        macnum_box[i].config(state="readonly")
        workvol_box[i]=tk.Entry(work_frame,width=5,relief=tk.SUNKEN,bd=2,font=font10)
        workvol_box[i].grid(row=2+i,column=2,padx=2)
        workvol_box[i].insert(0,pcl[i][7])
        workvol_box[i].config(state="readonly")
        goodpro_box[i]=tk.Entry(work_frame,width=5,relief=tk.SUNKEN,bd=2,font=font10)
        goodpro_box[i].grid(row=2+i,column=3,padx=2)
        goodpro_box[i].insert(0,pcl[i][11])
        goodpro_box[i].config(state="readonly")
        defeitems_box[i]=tk.Entry(work_frame,width=5,relief=tk.SUNKEN,bd=2,font=font10)
        defeitems_box[i].grid(row=2+i,column=4,padx=2)
        defeitems_box[i].insert(0,pcl[i][12])
        defeitems_box[i].config(state="readonly")
        worker_box[i]=tk.Entry(work_frame,width=20,relief=tk.SUNKEN,bd=2,font=font10)
        worker_box[i].grid(row=2+i,column=5,padx=2)
        worker_box[i].insert(0,pcl[i][13])
        worker_box[i].config(state="readonly")
        time_box[i]=tk.Entry(work_frame,width=15,relief=tk.SUNKEN,bd=2,font=font10)
        time_box[i].grid(row=2+i,column=6,padx=2)
        time_box[i].insert(0,entry_time[i])
        time_box[i].config(state="readonly")
        text_box[i]=tk.Entry(work_frame,width=25,relief=tk.SUNKEN,bd=2,font=font10)
        text_box[i].grid(row=2+i,column=7,padx=2)
        text_box[i].insert(0,pcl[i][14])
        text_box[i].config(state="readonly")
    
    
    conn.commit()
    cur.close()
    conn.close()
    pass
    

def search_command():
    conn=psy.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
            )
    cur=conn.cursor()
    lot_no=lot_entry.get()
    if lot_no == "":
        return None
    product=product_entry.get()
    if product != "":
        cur.execute("select * from update_history where (lot_no=%s and project_name=%s and status=%s )",(lot_no,product,"完了"))
    else:
        cur.execute("select * from update_history where (lot_no=%s and status=%s)",(lot_no,"完了"))
    data_list=cur.fetchall()
    df=pd.DataFrame(data_list,columns=["updateid","projectid","project_name","task_name",
                                       "work_name","barcode_id","status","work_volume",
                                       "dimension_value","material_number",
                                       "machine_number","goodproduct_volume",
                                       "defectiveitems_number","worker",
                                       "special_notes","lot_no","start_date",
                                       "end_date","progress_data","work_procedure",
                                       "end_time_date","update_at"])
    df=df.drop_duplicates(subset=["barcode_id"],keep="last")
    unique_data=df.values.tolist()
    #pandasを使って特定のインデックスの値（この場合はbarcode_id）の重複を解除、一番最後のデータを残す
    
    dictindex_list=[2,3,5,15]#製品名、作業名、バーコード、ロットナンバーを取り出すためのインデックス
    tree_list=[[i[x] for x in dictindex_list] for i in unique_data]#unique_dataの中の製品名、作業名、バーコード、ロットナンバーを取り出す
    all_treeindex=search_tree.get_children()
    search_tree.delete(*all_treeindex)
    for i in tree_list:
        
        search_tree.insert("","end",values=i)
    conn.commit()
    cur.close()
    conn.close()



entry_frame=tk.Frame(root)
entry_frame.pack(expand=True,fill="both")
lot_label=tk.Label(entry_frame,text="LOT_NO",width=8,relief=tk.SUNKEN,bd=2)
lot_label.grid(row=0,column=0,padx=3,pady=5)
lot_entry=tk.Entry(entry_frame,width=12,relief=tk.SOLID,bd=2)
lot_entry.grid(row=1,column=0,padx=3)
product_label=tk.Label(entry_frame,text="製品名",width=8,relief=tk.SUNKEN,bd=2)
product_label.grid(row=0,column=1,pady=5)
product_entry=tk.Entry(entry_frame,width=20,relief=tk.SOLID,bd=2)
product_entry.grid(row=1,column=1)
lot_button=tk.Button(entry_frame,width=5,relief=tk.RAISED,bd=3,text="検索",command=search_command)
lot_button.grid(row=1,column=2,padx=5)
tree_frame=tk.Frame(root)
tree_frame.pack(expand=True,fill="both")
search_tree=ttk.Treeview(tree_frame,height=20,show="headings",column=("product","task","barcode","LOT_NO"))
search_tree.heading("product",text="製品名")
search_tree.heading("task",text="作業名")
search_tree.heading("barcode",text="バーコード")
search_tree.heading("LOT_NO",text="Lot_No")

search_tree.column("product",width=100)
search_tree.column("task",width=100)
search_tree.column("LOT_NO",width=90)
search_tree.column("barcode",width=100)
search_tree.pack()
search_tree.bind("<<TreeviewSelect>>",tree_select)



root.mainloop()
