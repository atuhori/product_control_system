import psycopg as psy
import tkinter as tk
from tkinter import ttk
from collections import defaultdict
from tkinter import messagebox
#from db_config import db_config
from dotenv import load_dotenv
import os

load_dotenv()


root=tk.Tk()
root.title("進捗表示")
root.geometry("700x700")
root.resizable(width=False,height=False)


def update():
    try:#データベース接続に失敗したときのエラー処理
        conn=psy.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
           )
        cur=conn.cursor()
    except psy.OperationalError as e:
        tk.messagebox.showerror("データベース接続エラー",f"\nエラー名{e}")
        cur.close()
        conn.close()
        return
    cur.execute("select * from barcodedata")
    
    progress_data=cur.fetchall()#barcodedataのすべてのデータを取得
    progress_sort=sorted(progress_data,key=lambda x: (x[2],x[19]),reverse=True)
    comp_dict=defaultdict(list)
    for i in progress_sort:
        key=(i[2],i[15])
        comp_dict[key].append(i)#製品名とlot_noで識別された製品が一つの辞書にまとまる
    for i in comp_dict:
        comp_dict[i]=sorted(comp_dict[i],key=lambda x: (x[2],x[3],x[19]))
    comp_work=""
    touch_list=[]
    
    for i in comp_dict:
        all_work=len(comp_dict[i])
        untouch_work=""
        comp_val=0
        
        for x in comp_dict[i]:
            if x[6] == "完了":
                comp_val+=1
                comp_work=x[4]
            elif x[6] == "未着手" and untouch_work == "":
                untouch_work=x[4]
        comp_rate=comp_val/all_work*100
        comp_tuple=i[0],i[1],int(comp_rate),comp_work,comp_dict[i][0][17],comp_dict[i][0][16],untouch_work
        touch_list.append(list(comp_tuple))
    comp_list=[i for i in touch_list if i[2] != 0]#進捗率０の場合はリストから除外
    untouched_list=[i for i in touch_list if i[2] == 0]#進捗率０のデータをリスト化
    comp_list=sorted(comp_list,key=lambda x: (x[4],-x[2]))#-x[2]で降順
    
    project_frame=["None"]*len(comp_list)
    projectname_label=["None"]*len(comp_list)
    lot_label=["None"]*len(comp_list)
    rate_label=["None"]*len(comp_list)
    work_label=["None"]*len(comp_list)
    end_label=["None"]*len(comp_list)
    def win_cut():
        for i in range(len(comp_list)):
            project_frame[i].destroy()
    for i in range(len(comp_list)):
        project_frame[i]=tk.Frame(inprogress_tab)
        project_frame[i].pack()
        projectname_label[i]=tk.Label(project_frame[i],width=20,text=comp_list[i][0])
        projectname_label[i].grid(row=0,column=0,padx=2)
        lot_label[i]=tk.Label(project_frame[i],width=15,text=comp_list[i][1])
        lot_label[i].grid(row=0,column=1,padx=2)
        progress_bar=ttk.Progressbar(project_frame[i],length=113,mode="determinate")
        progress_bar.grid(row=0,column=2,padx=2)
        progress_bar["value"]=int(comp_list[i][2])
        rate_label[i]=tk.Label(project_frame[i],width=5,text=int(comp_list[i][2]))
        rate_label[i].grid(row=0,column=3,padx=2)
        work_label[i]=tk.Label(project_frame[i],width=20,text=comp_list[i][3])
        work_label[i].grid(row=0,column=4,padx=3)
        end_label[i]=tk.Label(project_frame[i],width=10,text=comp_list[i][4])
        end_label[i].grid(row=0,column=5,padx=2)


    ###未着手タブ
    untouched_list=sorted(untouched_list,key=lambda x: (x[4]))
    untouched_frame=[None]*len(untouched_list)
    untouchedproject=[None]*len(untouched_list)
    untouchedlotno=[None]*len(untouched_list)
    untouchedstandbyprocess=[None]*len(untouched_list)
    untouchedstart=[None]*len(untouched_list)
    untouchedend=[None]*len(untouched_list)
    def pend_cut():
        for i in range(len(untouched_list)):
            untouched_frame[i].destroy()
    for i in range(len(untouched_list)):
        untouched_frame[i]=tk.Frame(untouched_tab)
        untouched_frame[i].pack()
        untouchedproject[i]=tk.Label(untouched_frame[i],text=untouched_list[i][0],width=20)
        untouchedproject[i].grid(row=0,column=0,padx=2)
        untouchedlotno[i]=tk.Label(untouched_frame[i],text=untouched_list[i][1],width=15)
        untouchedlotno[i].grid(row=0,column=1,padx=2)
        untouchedstandbyprocess[i]=tk.Label(untouched_frame[i],text=untouched_list[i][6],width=20)
        untouchedstandbyprocess[i].grid(row=0,column=2,padx=2)
        untouchedstart[i]=tk.Label(untouched_frame[i],text=untouched_list[i][5],width=15)
        untouchedstart[i].grid(row=0,column=3,padx=2)
        untouchedend[i]=tk.Label(untouched_frame[i],text=untouched_list[i][4],width=15)
        untouchedend[i].grid(row=0,column=4,padx=2)


    ###各種工程タブ 表示関数
    def cate_up(category):
        category_datalist=[]
        for i in comp_dict:
            project_keylist=[x for x in comp_dict[i] if any(y in x for y in category)]
            category_datalist.extend(project_keylist)#リストとリストを結合していくためappendではなくextend
        category_datalist=sorted(category_datalist,key=lambda x: (x[16]))
        return category_datalist

    def cut(value,frames):#フレーム削除の関数
        for i in range(value):
            frames[i].destroy()

    ###プレスタブのウィジェット配置
            
    press_category=["プレス","タレパン","オートマ","シャーリング"]#分類されたプレス工程リスト
    presses=len(cate_up(press_category))
    press=cate_up(press_category)
    press_frame=[None]*presses
    pressproject=[None]*presses
    presstask=[None]*presses
    presswork=[None]*presses
    presslotno=[None]*presses
    pressstatus=[None]*presses
    pressdeadline=[None]*presses
    for i in range(presses):
        press_frame[i]=tk.Frame(press_tab)
        press_frame[i].pack()
        pressproject[i]=tk.Label(press_frame[i],text=press[i][2],width=18)
        pressproject[i].grid(row=0,column=0,padx=2)
        presstask[i]=tk.Label(press_frame[i],text=press[i][3],width=18)
        presstask[i].grid(row=0,column=1,padx=2)
        presswork[i]=tk.Label(press_frame[i],text=press[i][4],width=15)
        presswork[i].grid(row=0,column=2,padx=2)
        presslotno[i]=tk.Label(press_frame[i],text=press[i][15],width=15)
        presslotno[i].grid(row=0,column=3,padx=2)
        pressstatus[i]=tk.Label(press_frame[i],text=press[i][6],width=8)
        pressstatus[i].grid(row=0,column=4,padx=2)
        pressdeadline[i]=tk.Label(press_frame[i],text=press[i][17],width=10)
        pressdeadline[i].grid(row=0,column=5,padx=2)

    ###板金・サルバタブ
    sheetmetal_category=["組み立て","溶接","サルバ","ベンダー","スポット"]
    sheetmetals=len(cate_up(sheetmetal_category))
    sheetmetal=cate_up(sheetmetal_category)
    sheetmetal_frame=[None]*sheetmetals
    sheetmetalproject=[None]*sheetmetals
    sheetmetaltask=[None]*sheetmetals
    sheetmetalwork=[None]*sheetmetals
    sheetmetallotno=[None]*sheetmetals
    sheetmetalstatus=[None]*sheetmetals
    sheetmetaldeadline=[None]*sheetmetals
    for i in range(sheetmetals):
        sheetmetal_frame[i]=tk.Frame(sheetmetal_tab)
        sheetmetal_frame[i].pack()
        sheetmetalproject[i]=tk.Label(sheetmetal_frame[i],text=sheetmetal[i][2],width=18)
        sheetmetalproject[i].grid(row=0,column=0,padx=2)
        sheetmetaltask[i]=tk.Label(sheetmetal_frame[i],text=sheetmetal[i][3],width=18)
        sheetmetaltask[i].grid(row=0,column=1,padx=2)
        sheetmetalwork[i]=tk.Label(sheetmetal_frame[i],text=sheetmetal[i][4],width=15)
        sheetmetalwork[i].grid(row=0,column=2,padx=2)
        sheetmetallotno[i]=tk.Label(sheetmetal_frame[i],text=sheetmetal[i][15],width=15)
        sheetmetallotno[i].grid(row=0,column=3,padx=2)
        sheetmetalstatus[i]=tk.Label(sheetmetal_frame[i],text=sheetmetal[i][6],width=8)
        sheetmetalstatus[i].grid(row=0,column=4,padx=2)
        sheetmetaldeadline[i]=tk.Label(sheetmetal_frame[i],text=sheetmetal[i][17],width=10)
        sheetmetaldeadline[i].grid(row=0,column=5,padx=2)

    ###前処理タブのウィジェット配置

    treatment_category=["前処理"]
    treatments=len(cate_up(treatment_category))
    treatment=cate_up(treatment_category)
    treatment_frame=[None]*treatments
    treatmentproject=[None]*treatments
    treatmenttask=[None]*treatments
    treatmentwork=[None]*treatments
    treatmentlotno=[None]*treatments
    treatmentstatus=[None]*treatments
    treatmentdeadline=[None]*treatments
    for i in range(treatments):
        treatment_frame[i]=tk.Frame(pretreatment_tab)
        treatment_frame[i].pack()
        treatmentproject[i]=tk.Label(treatment_frame[i],text=treatment[i][2],width=18)
        treatmentproject[i].grid(row=0,column=0,padx=2)
        treatmenttask[i]=tk.Label(treatment_frame[i],text=treatment[i][3],width=18)
        treatmenttask[i].grid(row=0,column=1,padx=2)
        treatmentwork[i]=tk.Label(treatment_frame[i],text=treatment[i][4],width=15)
        treatmentwork[i].grid(row=0,column=2,padx=2)
        treatmentlotno[i]=tk.Label(treatment_frame[i],text=treatment[i][15],width=15)
        treatmentlotno[i].grid(row=0,column=3,padx=2)
        treatmentstatus[i]=tk.Label(treatment_frame[i],text=treatment[i][6],width=8)
        treatmentstatus[i].grid(row=0,column=4,padx=2)
        treatmentdeadline[i]=tk.Label(treatment_frame[i],text=treatment[i][17],width=10)
        treatmentdeadline[i].grid(row=0,column=5,padx=2)

    ###塗装タブのウィジェット配置

    coating_category=["塗装1号","塗装2号","マスキング","ライン梱包"]
    coatings=len(cate_up(coating_category))
    coating=cate_up(coating_category)
    coating_frame=[None]*coatings
    coatingproject=[None]*coatings
    coatingtask=[None]*coatings
    coatingwork=[None]*coatings
    coatinglotno=[None]*coatings
    coatingstatus=[None]*coatings
    coatingdeadline=[None]*coatings
    for i in range(coatings):
        coating_frame[i]=tk.Frame(coating_tab)
        coating_frame[i].pack()
        coatingproject[i]=tk.Label(coating_frame[i],text=coating[i][2],width=18)
        coatingproject[i].grid(row=0,column=0,padx=2)
        coatingtask[i]=tk.Label(coating_frame[i],text=coating[i][3],width=18)
        coatingtask[i].grid(row=0,column=1,padx=2)
        coatingwork[i]=tk.Label(coating_frame[i],text=coating[i][4],width=15)
        coatingwork[i].grid(row=0,column=2,padx=2)
        coatinglotno[i]=tk.Label(coating_frame[i],text=coating[i][15],width=15)
        coatinglotno[i].grid(row=0,column=3,padx=2)
        coatingstatus[i]=tk.Label(coating_frame[i],text=coating[i][6],width=8)
        coatingstatus[i].grid(row=0,column=4,padx=2)
        coatingdeadline[i]=tk.Label(coating_frame[i],text=coating[i][17],width=10)
        coatingdeadline[i].grid(row=0,column=5,padx=2)

    ###整備タブのウィジェット配置

    maintenance_category=["整備","梱包"]
    maintenances=len(cate_up(maintenance_category))
    maintenance=cate_up(maintenance_category)
    maintenance_frame=[None]*maintenances
    maintenanceproject=[None]*maintenances
    maintenancetask=[None]*maintenances
    maintenancework=[None]*maintenances
    maintenancelotno=[None]*maintenances
    maintenancestatus=[None]*maintenances
    maintenancedeadline=[None]*maintenances
    for i in range(maintenances):
        maintenance_frame[i]=tk.Frame(maintenance_tab)
        maintenance_frame[i].pack()
        maintenanceproject[i]=tk.Label(maintenance_frame[i],text=maintenance[i][2],width=18)
        maintenanceproject[i].grid(row=0,column=0,padx=2)
        maintenancetask[i]=tk.Label(maintenance_frame[i],text=maintenance[i][3],width=18)
        maintenancetask[i].grid(row=0,column=1,padx=2)
        maintenancework[i]=tk.Label(maintenance_frame[i],text=maintenance[i][4],width=15)
        maintenancework[i].grid(row=0,column=2,padx=2)
        maintenancelotno[i]=tk.Label(maintenance_frame[i],text=maintenance[i][15],width=15)
        maintenancelotno[i].grid(row=0,column=3,padx=2)
        maintenancestatus[i]=tk.Label(maintenance_frame[i],text=maintenance[i][6],width=8)
        maintenancestatus[i].grid(row=0,column=4,padx=2)
        maintenancedeadline[i]=tk.Label(maintenance_frame[i],text=maintenance[i][17],width=10)
        maintenancedeadline[i].grid(row=0,column=5,padx=2)
    

    cur.close()
    conn.close()
    root.update_idletasks()
    root.after(9990,win_cut)
    root.after(9990,pend_cut)
    root.after(9990,lambda: cut(presses,press_frame))
    root.after(9990,lambda: cut(sheetmetals,sheetmetal_frame))
    root.after(9990,lambda: cut(treatments,treatment_frame))
    root.after(9990,lambda: cut(coatings,coating_frame))
    root.after(9990,lambda: cut(maintenances,maintenance_frame))
    root.after(10000,lambda: update())
    pass





"""---------------------------

ui総合

---------------------------"""

notebook=ttk.Notebook(root,width=680,height=680)
inprogress_tab=tk.Frame(notebook)
untouched_tab=tk.Frame(notebook)
press_tab=tk.Frame(notebook)
sheetmetal_tab=tk.Frame(notebook)
pretreatment_tab=tk.Frame(notebook)
coating_tab=tk.Frame(notebook)
maintenance_tab=tk.Frame(notebook)
notebook.add(inprogress_tab,text="製品進捗",padding=3)
notebook.add(untouched_tab,text="未着手",padding=3)
notebook.add(press_tab,text="プレス",padding=3)
notebook.add(sheetmetal_tab,text="板金・サルバ",padding=3)
notebook.add(pretreatment_tab,text="前処理",padding=3)
notebook.add(coating_tab,text="塗装1号・塗装２号",padding=3)
notebook.add(maintenance_tab,text="整備",padding=3)
notebook.pack()

"""-----------------------------

製品進捗タブ

-----------------------------"""

menu_frame=tk.Frame(inprogress_tab,relief=tk.SUNKEN,bg="black")
menu_frame.pack()
project_label=tk.Label(menu_frame,width=20,text="製品名")
project_label.grid(row=0,column=0,padx=2,pady=2)
lotno_label=tk.Label(menu_frame,width=15,text="Lot-No")
lotno_label.grid(row=0,column=1,padx=2)
progress_label=tk.Label(menu_frame,width=22,text="進捗率")
progress_label.grid(row=0,column=2,padx=2)
process_label=tk.Label(menu_frame,width=20,text="作業工程")
process_label.grid(row=0,column=3,padx=2)
deadline_label=tk.Label(menu_frame,width=10,text="納期")
deadline_label.grid(row=0,column=4,padx=2)

"""------------------------------

未着手タブ

------------------------------"""
pend_frame=tk.Frame(untouched_tab,relief=tk.SUNKEN,bg="black")
pend_frame.pack()
pendprojeckt_label=tk.Label(pend_frame,width=20,text="製品名")
pendprojeckt_label.grid(row=0,column=0,padx=2,pady=2)
pendlotno_label=tk.Label(pend_frame,width=15,text="Lot-No")
pendlotno_label.grid(row=0,column=1,padx=2)
standbyprocess_label=tk.Label(pend_frame,width=20,text="待機工程")
standbyprocess_label.grid(row=0,column=2,padx=2)
pendstart_label=tk.Label(pend_frame,width=15,text="開始予定")
pendstart_label.grid(row=0,column=3,padx=2)
pendend_label=tk.Label(pend_frame,width=15,text="出荷日時")
pendend_label.grid(row=0,column=4,padx=2)

"""^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

プレスタブ

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"""
pressmenu_frame=tk.Frame(press_tab,relief=tk.SUNKEN,bg="black")
pressmenu_frame.pack()
pressmenu_project=tk.Label(pressmenu_frame,width=18,text="製品名")
pressmenu_project.grid(row=0,column=0,padx=2,pady=2)
pressmenu_task=tk.Label(pressmenu_frame,width=18,text="作業名")
pressmenu_task.grid(row=0,column=1,padx=2)
pressmenu_work=tk.Label(pressmenu_frame,width=15,text="作業工程")
pressmenu_work.grid(row=0,column=2,padx=2)
pressmenu_lotno=tk.Label(pressmenu_frame,width=15,text="Lot-No")
pressmenu_lotno.grid(row=0,column=3,padx=2)
pressmenu_status=tk.Label(pressmenu_frame,width=8,text="状態")
pressmenu_status.grid(row=0,column=4,padx=2)
pressmenu_deadline=tk.Label(pressmenu_frame,width=10,text="納期")
pressmenu_deadline.grid(row=0,column=5,padx=2)

"""--------------------------------

板金・サルバタブ

--------------------------------"""
metalmenu_frame=tk.Frame(sheetmetal_tab,relief=tk.SUNKEN,bg="black")
metalmenu_frame.pack()
metalmenu_project=tk.Label(metalmenu_frame,text="製品名",width=18)
metalmenu_project.grid(row=0,column=0,padx=2,pady=2)
metalmenu_task=tk.Label(metalmenu_frame,text="作業名",width=18)
metalmenu_task.grid(row=0,column=1,padx=2)
metalmenu_work=tk.Label(metalmenu_frame,text="作業工程",width=15)
metalmenu_work.grid(row=0,column=2,padx=2)
metalmenu_lotno=tk.Label(metalmenu_frame,text="Lot-No",width=15)
metalmenu_lotno.grid(row=0,column=3,padx=2)
metalmenu_status=tk.Label(metalmenu_frame,text="状態",width=8)
metalmenu_status.grid(row=0,column=4,padx=2)
metalmenu_deadline=tk.Label(metalmenu_frame,text="出荷日",width=10)
metalmenu_deadline.grid(row=0,column=5,padx=2)

"""--------------------------------

前処理タブ

--------------------------------"""
treatmentmenu_frame=tk.Frame(pretreatment_tab,relief=tk.SUNKEN,bg="black")
treatmentmenu_frame.pack()
treatmentmenu_project=tk.Label(treatmentmenu_frame,text="製品名",width=18)
treatmentmenu_project.grid(row=0,column=0,padx=2,pady=2)
treatmentmenu_task=tk.Label(treatmentmenu_frame,text="作業名",width=18)
treatmentmenu_task.grid(row=0,column=1,padx=2)
treatmentmenu_work=tk.Label(treatmentmenu_frame,text="作業工程",width=15)
treatmentmenu_work.grid(row=0,column=2,padx=2)
treatmentmenu_lotno=tk.Label(treatmentmenu_frame,text="Lot-No",width=15)
treatmentmenu_lotno.grid(row=0,column=3,padx=2)
treatmentmenu_status=tk.Label(treatmentmenu_frame,text="状態",width=8)
treatmentmenu_status.grid(row=0,column=4,padx=2)
treatmentmenu_deadline=tk.Label(treatmentmenu_frame,text="出荷日",width=10)
treatmentmenu_deadline.grid(row=0,column=5,padx=2)

"""---------------------------------

塗装1号、塗装２号タブ

---------------------------------"""
coatingmenu_frame=tk.Frame(coating_tab,relief=tk.SUNKEN,bg="black")
coatingmenu_frame.pack()
coatingmenu_project=tk.Label(coatingmenu_frame,text="製品名",width=18)
coatingmenu_project.grid(row=0,column=0,padx=2,pady=2)
coatingmenu_task=tk.Label(coatingmenu_frame,text="作業名",width=18)
coatingmenu_task.grid(row=0,column=1,padx=2)
coatingmenu_work=tk.Label(coatingmenu_frame,text="作業工程",width=15)
coatingmenu_work.grid(row=0,column=2,padx=2)
coatingmenu_lotno=tk.Label(coatingmenu_frame,text="Lot-No",width=15)
coatingmenu_lotno.grid(row=0,column=3,padx=2)
coatingmenu_status=tk.Label(coatingmenu_frame,text="状態",width=8)
coatingmenu_status.grid(row=0,column=4,padx=2)
coatingmenu_deadline=tk.Label(coatingmenu_frame,text="出荷日",width=10)
coatingmenu_deadline.grid(row=0,column=5,padx=2)

"""---------------------------------

整備タブ

---------------------------------"""
maintenancemenu_frame=tk.Frame(maintenance_tab,relief=tk.SUNKEN,bg="black")
maintenancemenu_frame.pack()
maintenancemenu_project=tk.Label(maintenancemenu_frame,text="製品名",width=18)
maintenancemenu_project.grid(row=0,column=0,padx=2,pady=2)
maintenancemenu_task=tk.Label(maintenancemenu_frame,text="作業名",width=18)
maintenancemenu_task.grid(row=0,column=1,padx=2)
maintenancemenu_work=tk.Label(maintenancemenu_frame,text="作業工程",width=15)
maintenancemenu_work.grid(row=0,column=2,padx=2)
maintenancemenu_lotno=tk.Label(maintenancemenu_frame,text="Lot-No",width=15)
maintenancemenu_lotno.grid(row=0,column=3,padx=2)
maintenancemenu_status=tk.Label(maintenancemenu_frame,text="状態",width=8)
maintenancemenu_status.grid(row=0,column=4,padx=2)
maintenancemenu_deadline=tk.Label(maintenancemenu_frame,text="出荷日",width=10)
maintenancemenu_deadline.grid(row=0,column=5,padx=2)

          

update()#進捗状況の随時更新を実行

root.mainloop()
