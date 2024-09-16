#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import win32com.client
from pathlib import Path

mas = ["01_К", "01_Кадр_2_К", "01_Кадр_3_К"]

psApp = win32com.client.Dispatch("Photoshop.Application")

try:
    doc = psApp.Application.ActiveDocument
except:
    print("No active document")
    exit(1)

# path_name = doc.path + doc.name

path_1 = Path.cwd() / doc.path
path = path_1.parent
# print(path)
for i in mas:
    path_2 = Path.cwd() / path / i / doc.name
    try:
        psApp.Open(path_2)
    except:
        pass
        # print(f'[*ERROR*] файла нет в папке {path_2}')
