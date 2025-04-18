import tkinter as tk
from tkinter import ttk
import psycopg as psy
from dotenv import load_dotenv
import os

load_dotenv()
schedule_widget=16#schedule_frameに配置するwidgetの数


root=tk.Tk()
root.title("製品登録")
root.geometry("500x600")
root.resizable(width=False,height=False)
conn=psy.connect(
            dbname=os.getenv("DB_NAME2"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
           )
cur=conn.cursor()
cur.execute("select product_name,product_val from product")
project_list=cur.fetchall()
cur.close()
conn.close()
project_value=[i[0] for i in project_list]
project_dict={i[0]:i[1] for i in project_list}

def combo_bind(event,a):
    print(a)
    lotval_entry[a].delete(0,tk.END)
    b=project_combo[a].get()
    print(2,b)
    lotval_entry[a].insert(0,project_dict[b])
    

def command_push():
    with psy.connect(dbname= os.getenv("DB_NAME"),user= os.getenv("DB_USER"),password= os.getenv("DB_PASS"),host= os.getenv("DB_HOST"),port= int(os.getenv("DB_PORT"))) as conn:
        with conn.cursor() as cur:
            a=cuf.fetchall()

###タブ作成


notebook=ttk.Notebook(root,width=490,height=580)
schedule_tab=tk.Frame(notebook)
processrecord_tab=tk.Frame(notebook)
notebook.add(schedule_tab,text="作業計画",padding=4)#paddingを設定するとタブごとの枠の太さを変更することができる
notebook.add(processrecord_tab,text="製品データ登録",padding=4)
notebook.pack()

###作業計画タブの中身

schedule_frame=tk.Frame(schedule_tab)
schedule_frame.pack()
project_label=tk.Label(schedule_frame,width=10,text="製品名")
project_label.grid(row=0,column=0,padx=10,pady=10)
lotval_label=tk.Label(schedule_frame,width=10,text="ロット作業数")
lotval_label.grid(row=0,column=1,padx=5,pady=10)
startdate_label=tk.Label(schedule_frame,width=10,text="開始日")
startdate_label.grid(row=0,column=2,padx=5,pady=10)
enddate_label=tk.Label(schedule_frame,width=10,text="終了予定日")
enddate_label.grid(row=0,column=3,padx=5,pady=10)
lotnum_label=tk.Label(schedule_frame,width=10,text="ロットナンバー")
lotnum_label.grid(row=0,column=4,padx=5,pady=10)
project_combo,lotval_entry,startdate_entry,enddate_entry,lotnum_entry=([None]*schedule_widget for i in range(5))#ジェネレータ式を使ったけど、リスト内包式でも大丈夫
for i in range(schedule_widget):
    project_combo[i]=ttk.Combobox(schedule_frame,width=15,values=project_value)
    project_combo[i].grid(row=1+i,column=0,pady=5)
    #a=i
    #project_combo[i].bind("<<ComboboxSelected>>",lambda event, a :combo_bind(event,a))
    #上の記述ではダメな理由
    #lambdaは関数、関数で使う引数は関数の外で定義した変数とは別物
    #そのためlambda event,a:combo_bind(event,a)はエラーになる。一見引数aにはiが入っているように見えるけどaはlambdaで新しく設定された引数のaのため、lambdaの引数としてlambda event,a=iと設定してあげないとエラーになる
    #project_combo[i].bind("<<ComboboxSelected>>".lambda event :combo_bind(event,a))これだとコールバック関数のcombo_bind(event,a)のaには何も入っていない
    #project_combo[i].bind("<<ComboboxSelected>>",lambda event :combo_bind(event,i))これで実行するとfor構文の参照値を実行してしまう。つまりiには一番最後の数字15が入って正しい挙動にならなくなる、iを直接引数に指定するとmainloopが実行し終わった後のiに上書きされてしまう
    project_combo[i].bind("<<ComboboxSelected>>",lambda event,a=i : combo_bind(event,a))#この記述ならa=iに現在値を入れて実行することが可能。つまり正しい挙動になる、この場合event（コンボが選択されたタイミング）のiをaに固定することができるため正しい挙動
    #for構文の中でlambdaを定義するときは引数にデフォルト値を設定することで現在値を固定することができる
    lotval_entry[i]=tk.Entry(schedule_frame,width=10,relief=tk.SUNKEN,bd=2)
    lotval_entry[i].grid(row=1+i,column=1,pady=5)
    startdate_entry[i]=tk.Entry(schedule_frame,width=13,relief=tk.SUNKEN,bd=2)
    startdate_entry[i].grid(row=1+i,column=2,pady=5)
    enddate_entry[i]=tk.Entry(schedule_frame,width=13,relief=tk.SUNKEN,bd=2)
    enddate_entry[i].grid(row=1+i,column=3,pady=5)
    lotnum_entry[i]=tk.Entry(schedule_frame,width=10,relief=tk.SUNKEN,bd=2)
    lotnum_entry[i].grid(row=1+i,column=4,pady=5)

###製品データ登録タブの中身

#pro_val=[
#project_combo=ttk.Combobox(frame,width=20,



root.mainloop()
