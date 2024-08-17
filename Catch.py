import os, sys, time, hashlib, subprocess, datetime

import tkinter as tk

import tkinter.ttk as ttk

import tkinter.messagebox as tkmsgbox

import configparser

import re

import signal

from subprocess import Popen, PIPE, STDOUT



# by shun, Discord: 0x9d



CONFIG_FILE = __file__.replace(__file__.split("/")[-1], "") + "config.ini"

conf = configparser.ConfigParser()

conf.read(CONFIG_FILE)



def killProcess():

    if 'proc' in globals():

        proc.terminate()

        proc.wait()

        output, err = proc.communicate()

        output = output.decode('shift_jis')

        print(output)

        

def handler(signum, root):

    print("handler")

    killProcess()



def ghex(length):

    buf = ''

    while len(buf) < length:

        buf += hashlib.md5(os.urandom(100)).hexdigest()

    return buf[0:length]



def save():

    global conf

    if not conf.has_section('data'):

        conf.add_section('data')

    conf.set('data', 'target', txtMACAddr.get())

    conf.set('data', 'count', str(scale.get()))

    with open(CONFIG_FILE,'w') as f:

        conf.write(f)

    if tkmsgbox.askokcancel("random mac address gen", "本当に閉じてもよろしいですか？"):

        root.destroy()



def genMACAddr():

    mtarget = txtMACAddr.get()

    if mtarget[1] == 'x':

        if tkmsgbox.askyesno("random mac address gen", "先頭から二桁目をランダムにするとうまく動作しない場合があるため、動作確認済みのものを指定することをおすすめします。（TL-WN725N で 0, 2, 4, 6, 8, a, c, e のみ動作確認済み）\nそのまま続けますか？") == False:

            return

    if ":" in mtarget:

        if mtarget.count(":") != 5:

            tkmsgbox.showinfo("random mac address gen", "指定された MAC アドレスの形式が不正です")

            return

        if len(mtarget) != 17:

            tkmsgbox.showinfo("random mac address gen", "指定された MAC アドレスの形式が不正です")

            return

        mtarget = mtarget.replace(":", "")

    if len(mtarget) != 12:

        tkmsgbox.showinfo("random mac address gen", "指定された MAC アドレスの形式が不正です")

        return

    pattern = r"[^a-fx-xA-FX-X0-9]"

    if re.search(pattern, mtarget):

        tkmsgbox.showinfo("random mac address gen", "指定された MAC アドレスに数字, A-F , X, : 以外の文字が含まれています。")

        return

    mtlist = list(mtarget)

    print("changing mac address(es)...")

    path_w = __file__.replace(__file__.split("/")[-1], "") + "aps.lst"

    with open(path_w, mode='w') as f:

        for i in range(int(scale.get())):

            addr=""

            for j in range(len(mtlist)):

                c = mtlist[j]

                if mtlist[j] == 'x':

                    c = ghex(1)

                addr += c

                if (j + 1) % 2 == 0:

                    addr += ':'

            addr = addr.rstrip(':')

            f.write(addr + " DENPASPOT" + str(i+1) + "\n")

        f.close()

    print("done")

    print(datetime.datetime.now())

    tkmsgbox.showinfo("random mac address gen", "MAC アドレスリストが正しく更新されました。\n更新した MAC アドレス一覧は aps.lst ファイルから確認できます。")



def lblMACAddrHelp_Clicked():

    tkmsgbox.showinfo("random mac address gen", "指定する場所を数字、ランダムにする場所を x にしてください（例: 12:x4:xx:7x:xa:bc or 12x4xx7xxabc）\n先頭から二桁目をランダムにするとうまく動作しない場合があるため、動作確認済みのものを指定することをおすすめします。（0, 2, 4, 6, 8, a, c, eのみ動作確認済み）")



def updateLblAPSpotsCount(event=None):

    lblAPSpotsCount["text"] = varAPSpots.get()



def startAP():

    global proc

    proc = Popen(["sudo", "mdk4", "wlan0", "b", "-w", "a", "-h", "-c", "1", "-v", __file__.replace(__file__.split("/")[-1], "") + "aps.lst"], stdout=PIPE, stderr=STDOUT)

    lblStatus["text"] = "ステータス: 現在起動中です"

    lblStatus["fg"] = "green"

    

def stopAP():

    killProcess()

    lblStatus["text"] = "ステータス: 現在起動していません"

    lblStatus["fg"] = "red"



def resetConfig():

    if tkmsgbox.askokcancel("random mac address gen", "コンフィグを初期化してもよろしいですか？"):

        global conf

        if not conf.has_section('data'):

            conf.add_section('data')

        conf.set('data', 'target', '00:xx:xx:xx:xx:xx')

        conf.set('data', 'count', '5')

        with open(CONFIG_FILE,'w') as f:

            conf.write(f)

            txtMACAddr.delete(0, tk.END)

            txtMACAddr.insert(0, conf.get("data", "target", fallback="00:xx:xx:xx:xx:xx"))

            scale.set(conf.get("data", "count", fallback = 5))

            tkmsgbox.showinfo("random mac address gen", "コンフィグを初期化が完了しました")



def check(): 

    root.after(500, check)



signal.signal(signal.SIGINT, handler)



root = tk.Tk()

root.after(500, check)

root.title("random mac address gen")

root.geometry("400x200")



lblMACAddr = tk.Label(text = "指定する MAC アドレス")

lblMACAddr.place(x = 10, y = 10)



lblMACAddrHelp = tk.Label(text = "?", fg = "blue", cursor = "hand1")

lblMACAddrHelp.place(x = 155, y = 10)

lblMACAddrHelp.bind("<Button-1>", lambda e:lblMACAddrHelp_Clicked())



txtMACAddr = tk.Entry(root)

txtMACAddr.insert(0, conf.get("data", "target", fallback="00:xx:xx:xx:xx:xx"))

txtMACAddr.place(x = 170, y = 10, width = 220, height = 20)



lblAPSpots = tk.Label(text = "作成するアクセスポイントの数")

lblAPSpots.place(x = 10, y = 30)



lblAPSpotsCount = tk.Label(root, text = "0")

lblAPSpotsCount.place(x = 290, y = 47)



varAPSpots = tk.IntVar()

scale = ttk.Scale(root, from_= 1, to = 10, variable = varAPSpots, command = updateLblAPSpotsCount)

scale.set(conf.get("data", "count", fallback = 5))

scale.pack()

scale.place(x = 200, y = 32, width = 190)



lblStatus = tk.Label(text = "ステータス: 現在起動していません", fg = "red")

lblStatus.place(x = 10, y = 57)



btnChangeMACAddr = tk.Button(root, text = "MAC アドレスリストを更新", command = genMACAddr)

btnChangeMACAddr.place(x = 10, y = 85, width = 380)



btnStartAP = tk.Button(text = "アクセスポイントを起動", command = startAP)

btnStartAP.place(x = 10, y = 115, width = 185)



btnStopAP = tk.Button(text = "アクセスポイントを停止", command = stopAP)

btnStopAP.place(x = 205, y = 115, width = 185)



btnResetConfig = tk.Button(text = "コンフィグを初期化", command = resetConfig)

btnResetConfig.place(x = 10, y = 145, width = 185)



lblCredit = tk.Label(text = "created by shun, discord: 0x9d")

lblCredit.place(x = 192, y = 180)



root.protocol("WM_DELETE_WINDOW", save)

root.mainloop()

