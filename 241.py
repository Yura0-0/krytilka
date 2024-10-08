import datetime
import multiprocessing
import os
import shutil
import sys
import time
import cv2
import keyboard
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont
from PIL.ImageFile import ImageFile
from colorama import init, Fore
from tqdm import tqdm

# ImageFile.LOAD_TRUNCATED_IMAGES = True

pp = {'в печать 15': 'в печать 15', 'в печать 11': 'в печать 11', 'КАЛЕНДАРЬ-': 'КАЛЕНДАРЬ-', 'Магнит': 'Магнит',
      'Магнит-1': 'Магнит-1', 'Магнит-2': 'Магнит-2', 'Магнит-3': 'Магнит-3', 'в печать': 'в печать',
      'в печать 12': 'в печать 12', 'в печать 2': 'в печать 2', 'в печать 3': 'в печать 3', 'в печать 4': 'в печать 4',
      'в печать 5': 'в печать 5', 'в печать 1': 'в печать 1', 'в печать 13': 'в печать 13',
      'в печать 10': 'в печать 10', 'в печать 8': 'в печать 8', 'в печать 7': 'в печать 7', 'в печать 9': 'в печать 9',
      'Konvert': 'Konvert', 'в печать 6': 'в печать 6', 'ПОСТЕР': 'ПОСТЕР', 'Вымпел': 'Вымпел'}

path_krytilka = r"d:\!!!__АРМИЯ__!!!\вед\крутить"
path_create_papka = r"D:\!!!__АРМИЯ__!!!\вед"

vedomosti = os.listdir(path_krytilka)

mas_brak_fon = []


def key_exit():
    while True:
        if keyboard.is_pressed('q'):
            print("[*ERROR*]  остановка")

            p6.terminate()
            p1.terminate()
            p2.terminate()
            p3.terminate()
            p4.terminate()
            p5.terminate()
            sys.exit(0)


def create_mask(ved, im, name_id, pix, kadr, k):
    # ImageFile.LOAD_TRUNCATED_IMAGES = True
    try:
        ni = np.asarray(im)
    except OSError:
        mas_brak_fon.append(name_id)
        print(f"[** ERROR **] image file is truncated (0 bytes not processed):  {name_id}")

    pix = int(pix)

    r, g, b = im.getpixel((30, 30))
    # print("Red: {0}, Green: {1}, Blue: {2}".format(r, g, b))
    try:
        # зеленый r == 20 and g == 254 and b == 9:
        if any(map(lambda i: 235 <= i <= 255, (g,))) and any(map(lambda ii: 5 <= ii <= 40, (r,))):
            blues = ((ni[:, :, 0] >= 0) & (ni[:, :, 0] <= 70)) & \
                    ((ni[:, :, 1] >= 100) & (ni[:, :, 1] <= 255)) & \
                    ((ni[:, :, 2] >= 0) & (ni[:, :, 2] <= 36))
        # красный r == 255 and g == 0 and b == 255:
        elif any(map(lambda i: 0 <= i <= 20, (g,))) and any(map(lambda ii: 195 <= ii <= 255, (r,))):
            blues = ((ni[:, :, 0] >= 94) & (ni[:, :, 0] <= 255)) & \
                    ((ni[:, :, 1] >= 0) & (ni[:, :, 1] <= 51)) & \
                    ((ni[:, :, 2] >= 120) & (ni[:, :, 2] <= 255))
        else:
            mas_brak_fon.append(name_id)
            # print(Fore.YELLOW + f"[*** ERROR ***] Вед №_{ved},  c {name_id} проблема с фоном ")

        # Image.fromarray((blues * 255).astype(np.uint8)).save(f'mask.png', quality=100)

        img = Image.fromarray((blues * 255).astype(np.uint8))

        # убираем пиксели
        # img = Image.open(f'mask.png')
        mask_im = ImageOps.invert(img)
        # a = np.asarray(mask_im)
        a = np.array(mask_im)
        a[a <= 119] = 0
        a[a >= 120] = 255

        # горизонт
        s = np.roll(a, pix)
        a[a != s] = 0
        s = np.roll(a, -pix)
        a[a != s] = 0

        # верт
        a = a.T
        s = np.roll(a, pix)
        a[a != s] = 0
        s = np.roll(a, -pix)
        a[a != s] = 0
        a = a.T

        # # градиент
        # ss = a[-400:, 0:64]
        # if 255 in ss[:, 1]:
        #     aa = np.arange(0, 255, 4, dtype=np.uint8)
        #     np.copyto(ss, aa, where=ss == 255)
        #     print(a)

        Image.fromarray((a).astype(np.uint8)).save(f'mask-pix_{name_id}_{kadr}_{k}.jpg', quality=100)

        # убираем пятна с формы цвет
        img = cv2.imread(f'mask-pix_{name_id}_{kadr}_{k}.jpg', cv2.IMREAD_UNCHANGED)
        # with open(cv2.imread(f'mask-pix_{name_id}_{kadr}_{k}.jpg', cv2.IMREAD_UNCHANGED)) as img:
        pixel = img[30, 30]
        # print(pixel)
        if not pixel == 0:
            print(Fore.YELLOW + f"[*** ERROR ***] Вед №_{ved},  c {name_id} проблема с фоном (маска) ")

            thresh = 100  # вычитаем из контура подмышки у солдат (cv2.RETR_TREE)
            ret, thresh_img = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)

            # contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            cv2.drawContours(img, contours, -1, (255, 255, 255), -1)

            cv2.imwrite(f'mask-pix_{name_id}_{kadr}_{k}.jpg', img)


    except UnboundLocalError:
        mas_brak_fon.append(name_id)
        print(Fore.YELLOW + f"[*** ERROR ***] Вед №_{ved},  c {name_id} проблема с фоном ")


def v_pechat(pix):  # 1 6

    for ved in vedomosti:

        id_region = ved.split('-')[2]
        if int(id_region) < 100:

            papka_1 = os.path.join(path_krytilka, ved, "СКом", "01_К")
            papka_2 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_2_К")
            papka_3 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_3_К")
            jpg1 = sorted(os.listdir(papka_1))
            jpg2 = os.listdir(papka_2)
            jpg3 = os.listdir(papka_3)

            # проверка верстки
            rm = np.array(['Thumbs.db', '.DS_Store'])
            q1 = np.asarray(jpg1)
            idx = np.in1d(q1, rm)
            q1 = q1[~idx]

            q2 = np.asarray(jpg2)
            idx = np.in1d(q2, rm)
            q2 = q2[~idx]

            q3 = np.asarray(jpg3)
            idx = np.in1d(q3, rm)
            q3 = q3[~idx]

            try:
                if (q1 != q2).any() or (q1 != q3).any():
                    init(autoreset=True)
                    print(Fore.RED + f'[**ERROR**] имена jpg в №_{ved} не совпадают:\n ')
                    continue
            except ValueError:
                print(Fore.RED + f'[**ERROR**] количество jpg в №_{ved} не совпадает')
                continue

            ved = ved.split('-')[1]

            for jpg in q1:
                name_id = jpg.split('.')[0]

                if not name_id is mas_brak_fon:

                    path_jpg_1 = os.path.join(papka_1, jpg)
                    im1 = Image.open(path_jpg_1)

                    # create_mask
                    create_mask(ved, im1, name_id, pix, kadr='1', k='v')

                    try:
                        # вставка на фон
                        mask_im1 = Image.open(f'mask-pix_{name_id}_1_v.jpg')
                        mask_im1_blur = mask_im1.filter(ImageFilter.GaussianBlur(1))
                    except FileNotFoundError:
                        break
                    # mask_i = ImageOps.invert(mask_im1)

                    im_v_pechat = Image.open(r'241/в печать/203х305 синий фон.jpg')
                    im_v_pechat_6 = Image.open(r'241/в печать 6/2022 Армия 210x297.jpg')

                    mask_teni = ImageOps.invert(mask_im1).convert("RGBA")

                    # в печать
                    basewidth = 2550
                    wpercent = (basewidth / float(im1.size[0]))
                    hsize = int((float(im1.size[1]) * float(wpercent)))
                    im1 = im1.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                    wpercent = (basewidth / float(mask_im1_blur.size[0]))
                    hsize = int((float(mask_im1_blur.size[1]) * float(wpercent)))
                    mask_im1_blur = mask_im1_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                    # тень человека для папки в печать
                    wpercent = (basewidth / float(mask_teni.size[0]))
                    hsize = int((float(mask_teni.size[1]) * float(wpercent)))
                    mask_teni = mask_teni.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                    ni = np.array(mask_teni)
                    bl = ((ni[:, :, 0] == 255) & (ni[:, :, 1] == 255) & (ni[:, :, 2] == 255))
                    ni[:, :, 3] = 35  # прозрачность
                    ni[bl, 3] = 0
                    # .putalpha(128)
                    teni = Image.fromarray((ni).astype(np.uint8))  # .save('PNG.png', quality=100)
                    teni_blur = teni.filter(ImageFilter.GaussianBlur(50))

                    im_v_pechat.paste(teni_blur, (45, 210), mask=teni_blur)
                    im_v_pechat.paste(im1, (-45, 207), mask_im1_blur)

                    # нумерация
                    draw = ImageDraw.Draw(im_v_pechat)
                    font = ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 40)
                    draw.text((110, 3450), f"{name_id}", (255, 255, 255), font=font)

                    path_out = os.path.join(path_create_papka, ved, f'{pp["в печать"]}', f'{name_id}.jpg')
                    im_v_pechat.save(path_out, dpi=(300, 300), quality=95)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать"]}', f'{name_id}.jpg')
                    im_v_pechat.save(path_out, dpi=(300, 300), quality=95)

                    # в печать 6
                    basewidth = 2150
                    wpercent = (basewidth / float(im1.size[0]))
                    hsize = int((float(im1.size[1]) * float(wpercent)))
                    im1 = im1.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    wpercent = (basewidth / float(mask_im1_blur.size[0]))
                    hsize = int((float(mask_im1_blur.size[1]) * float(wpercent)))
                    mask_im1_blur = mask_im1_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                    im_v_pechat_6.paste(im1, (350, 117), mask_im1_blur)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 6"]}', f'{name_id}.jpg')
                    im_v_pechat_6.save(path_out, dpi=(300, 300), quality=95)

                    # водяной знак в печать
                    im_voda = Image.open(r'241/в печать 11/водяной .png')
                    maxsize = (355, 355)
                    im_v_pechat.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_v_pechat.paste(im_voda, mask=im_voda)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать"]}', f'{name_id}.jpg')
                    im_v_pechat.save(path_out, dpi=(60, 60))
                    # водяной знак в печать 6
                    im_voda_big = Image.open(r'241/в печать 11/водяной .png')
                    im_v_pechat_6.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_v_pechat_6.paste(im_voda_big, (5, 0), mask=im_voda_big)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 6"]}', f'{name_id}.jpg')
                    im_v_pechat_6.save(path_out, dpi=(60, 60))

                    im_voda_big.close()
                    im_voda.close()
                    im_v_pechat_6.close()
                    im_v_pechat.close()
                    mask_im1_blur.close()
                    mask_im1.close()
                    im1.close()

                    # удаление масок
                    os.remove(f'mask-pix_{name_id}_1_v.jpg')

                else:
                    break


def v_pechat_11(pix):  # в печать 11 2 3 4 7 9 konvert
    count = 1
    for ved in vedomosti:

        print(f"{count}) в работе №__{ved}")
        count += 1
        time.sleep(0.1)

        id_region = ved.split('-')[2]
        if int(id_region) < 100:

            papka_1 = os.path.join(path_krytilka, ved, "СКом", "01_К")
            papka_2 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_2_К")
            papka_3 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_3_К")
            jpg1 = sorted(os.listdir(papka_1))
            jpg2 = os.listdir(papka_2)
            jpg3 = os.listdir(papka_3)

            # проверка верстки
            rm = np.array(['Thumbs.db', '.DS_Store'])
            q1 = np.asarray(jpg1)
            idx = np.in1d(q1, rm)
            q1 = q1[~idx]

            q2 = np.asarray(jpg2)
            idx = np.in1d(q2, rm)
            q2 = q2[~idx]

            q3 = np.asarray(jpg3)
            idx = np.in1d(q3, rm)
            q3 = q3[~idx]

            try:
                if (q1 != q2).any() or (q1 != q3).any():
                    continue
            except ValueError:
                continue

            ved = ved.split('-')[1]

            for jpg in tqdm(q1):
                name_id = jpg.split('.')[0]

                if not name_id is mas_brak_fon:
                    path_jpg_1 = os.path.join(papka_1, jpg)
                    path_jpg_2 = os.path.join(papka_2, jpg)
                    path_jpg_3 = os.path.join(papka_3, jpg)

                    im1 = Image.open(path_jpg_1)
                    im2 = Image.open(path_jpg_2)
                    im3 = Image.open(path_jpg_3)

                    # create_mask
                    create_mask(ved, im1, name_id, pix, kadr='1', k='v1')
                    create_mask(ved, im2, name_id, pix, kadr='2', k='v1')

                    try:
                        # вставка на фон
                        mask1 = f'mask-pix_{name_id}_1_v1.jpg'
                        mask2 = f'mask-pix_{name_id}_2_v1.jpg'
                        mask_im1 = Image.open(mask1)
                        mask_im2 = Image.open(mask2)
                        mask_im1_blur = mask_im1.filter(ImageFilter.GaussianBlur(1))
                        mask_im2_blur = mask_im2.filter(ImageFilter.GaussianBlur(1))
                    except FileNotFoundError:
                        break

                    im_foto_sh = Image.open(r'241/в печать 11/в печать 1 шаблон.jpg')
                    im_foto_sh1 = Image.open(r'241/в печать 11/1.jpg')
                    im_foto_sh_kamyf = Image.open(r'241/в печать 11/10x15-камуфляж.jpg')
                    im_foto_sh_ykaz = Image.open(r'241/в печать 11/Указ лето22 152х203.jpg')
                    im_foto_sh_ykaz_t = Image.open(r'241/в печать 11/Указ лето22 152х203.png')
                    im_ramka_big = Image.open(r'241/в печать 11/рамка 152х203.png')
                    im_ramka = Image.open(r'241/в печать 12/10x15 рамка.png')
                    im_ykaz_zel = Image.open(r'241/в печать 7/указ-лето2022.jpg')
                    im_vert = Image.open(r'241/в печать 9/210х297 вертолетыАрмия.jpg')
                    im_vert_png = Image.open(r'241/в печать 9/210х297 вертолетыАрмия.png')

                    # размер im3
                    basewidth = 1350
                    wpercent = (basewidth / float(im3.size[0]))
                    hsize = int((float(im3.size[1]) * float(wpercent)))
                    im3 = im3.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    # в печать 4
                    im_foto_sh1.paste(im3, (-90, 0))
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 4"]}', f'{name_id}.jpg')
                    im_foto_sh1.save(path_out, dpi=(300, 300), quality=95)
                    im_foto_sh1.paste(im_ramka, mask=im_ramka)

                    # размер im2
                    # basewidth = 1300
                    basewidth = 1200
                    wpercent = (basewidth / float(im2.size[0]))
                    hsize = int((float(im2.size[1]) * float(wpercent)))
                    im2 = im2.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    wpercent = (basewidth / float(mask_im2_blur.size[0]))
                    hsize = int((float(mask_im2_blur.size[1]) * float(wpercent)))
                    mask_im2_blur = mask_im2_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    # камуфляж
                    im_foto_sh_kamyf.paste(im2, (-30, 145), mask_im2_blur)
                    im_foto_sh_kamyf.paste(im_ramka, mask=im_ramka)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 2"]}', f'{name_id}.jpg')
                    im_foto_sh_kamyf.save(path_out, dpi=(300, 300), quality=95)

                    # размер im2
                    basewidth = 1700
                    wpercent = (basewidth / float(im2.size[0]))
                    hsize = int((float(im2.size[1]) * float(wpercent)))
                    im2 = im2.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    wpercent = (basewidth / float(mask_im2_blur.size[0]))
                    hsize = int((float(mask_im2_blur.size[1]) * float(wpercent)))
                    mask_im2_blur = mask_im2_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                    # в печать 7 (зеленый указ)
                    im_ykaz_zel_shablon = Image.open(r'241/в печать 7/указ-лето2022.png')
                    im_ykaz_zel.paste(im2, (777, 1203), mask_im2_blur)
                    im_ykaz_zel.paste(im_ykaz_zel_shablon, mask=im_ykaz_zel_shablon)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 7"]}', f'{name_id}.jpg')
                    im_ykaz_zel.save(path_out, dpi=(300, 300), quality=95)
                    im_ykaz_zel_shablon.close()

                    # размер im2
                    basewidth = 2600
                    wpercent = (basewidth / float(im2.size[0]))
                    hsize = int((float(im2.size[1]) * float(wpercent)))
                    im2 = im2.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    wpercent = (basewidth / float(mask_im2_blur.size[0]))
                    hsize = int((float(mask_im2_blur.size[1]) * float(wpercent)))
                    mask_im2_blur = mask_im2_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    # в печать 9 (поле)
                    im_vert.paste(im2, (-60, 50), mask_im2_blur)
                    im_vert.paste(im_vert_png, mask=im_vert_png)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 9"]}', f'{name_id}.jpg')
                    im_vert.save(path_out, dpi=(300, 300), quality=95)

                    # размер im1
                    basewidth = 1500
                    wpercent = (basewidth / float(im1.size[0]))
                    hsize = int((float(im1.size[1]) * float(wpercent)))
                    im1 = im1.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    wpercent = (basewidth / float(mask_im1_blur.size[0]))
                    hsize = int((float(mask_im1_blur.size[1]) * float(wpercent)))
                    mask_im1_blur = mask_im1_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    # указ
                    im_foto_sh_ykaz.paste(im1, (300, 352), mask_im1_blur)
                    im_foto_sh_ykaz.paste(im_foto_sh_ykaz_t, mask=im_foto_sh_ykaz_t)
                    im_foto_sh_ykaz.paste(im_ramka_big, mask=im_ramka_big)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 3"]}', f'{name_id}.jpg')
                    im_foto_sh_ykaz.save(path_out, dpi=(300, 300), quality=95)

                    # вставка 3 фотки
                    im_foto_sh_ykaz = im_foto_sh_ykaz.rotate(90, expand=True)
                    im_foto_sh.paste(im_foto_sh_ykaz, (12, 25))
                    im_foto_sh.paste(im_foto_sh1, (10, 1800))
                    im_foto_sh.paste(im_foto_sh_kamyf, (1214, 1800))

                    # нумерация
                    draw = ImageDraw.Draw(im_foto_sh)
                    font = ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 40)
                    draw.text((80, 3480), f"{name_id}", (255, 255, 255), font=font)

                    path_out = os.path.join(path_create_papka, ved, f'{pp["в печать 11"]}', f'{name_id}.jpg')
                    im_foto_sh.save(path_out, dpi=(300, 300), quality=95)
                    time.sleep(0.1)
                    # размер im3 konvert
                    maxsize = (629, 629)
                    im3.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    path_out = os.path.join(path_create_papka, ved, f'{pp["Konvert"]}', f'{name_id}.jpg')
                    im3.save(path_out, dpi=(200, 200))

                    # размер водяной знак
                    im_foto_sh_ykaz = im_foto_sh_ykaz.rotate(-90, expand=True)
                    im_voda = Image.open(r'241/в печать 11/водяной .png')
                    maxsize = (355, 355)
                    im_foto_sh_ykaz.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_foto_sh_ykaz.paste(im_voda, mask=im_voda)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 3"]}', f'{name_id}.jpg')
                    im_foto_sh_ykaz.save(path_out, dpi=(60, 60))
                    im_voda_big = Image.open(r'241/в печать 11/водяной .png')
                    # размер водяной знак
                    maxsize = (355, 355)
                    im_vert.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_vert.paste(im_voda_big, (5, 0), mask=im_voda_big)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 9"]}', f'{name_id}.jpg')
                    im_vert.save(path_out, dpi=(60, 60))
                    # размер водяной знак
                    maxsize = (355, 355)
                    im_ykaz_zel.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_ykaz_zel.paste(im_voda_big, (5, 0), mask=im_voda_big)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 7"]}', f'{name_id}.jpg')
                    im_ykaz_zel.save(path_out, dpi=(60, 60))
                    # размер водяной знак
                    maxsize = (355, 355)
                    im_foto_sh_kamyf.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_foto_sh_kamyf.paste(im_voda, mask=im_voda)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 2"]}', f'{name_id}.jpg')
                    im_foto_sh_kamyf.save(path_out, dpi=(60, 60))
                    time.sleep(0.1)
                    # размер водяной знак
                    maxsize = (355, 355)
                    im_foto_sh1.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_foto_sh1.paste(im_voda, mask=im_voda)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 4"]}', f'{name_id}.jpg')
                    im_foto_sh1.save(path_out, dpi=(60, 60))

                    im_foto_sh.close()
                    im_foto_sh1.close()
                    im_foto_sh_kamyf.close()
                    im_foto_sh_ykaz.close()
                    im_foto_sh_ykaz_t.close()
                    im_ramka_big.close()
                    im_ramka.close()
                    im_ykaz_zel.close()
                    im_vert.close()
                    im_vert_png.close()
                    im1.close()
                    im2.close()
                    im3.close()
                    mask_im1.close()
                    mask_im2.close()
                    im_voda_big.close()
                    im_voda.close()

                    # удаление масок
                    os.remove(f'mask-pix_{name_id}_1_v1.jpg')
                    os.remove(f'mask-pix_{name_id}_2_v1.jpg')

                else:
                    break
        # else:
        #     continue

        # if int(id_region) < 100:
        init(autoreset=True)
        print(Fore.GREEN + f'[INFO] Прокрутил №__{ved}.\n')
        time.sleep(0.1)


def img_big_kal(pix):  # 15
    for ved in vedomosti:

        id_region = ved.split('-')[2]
        if int(id_region) < 100:

            papka_1 = os.path.join(path_krytilka, ved, "СКом", "01_К")
            papka_2 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_2_К")
            papka_3 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_3_К")
            jpg1 = sorted(os.listdir(papka_1))
            jpg2 = os.listdir(papka_2)
            jpg3 = os.listdir(papka_3)

            # проверка верстки
            rm = np.array(['Thumbs.db', '.DS_Store'])
            q1 = np.asarray(jpg1)
            idx = np.in1d(q1, rm)
            q1 = q1[~idx]

            q2 = np.asarray(jpg2)
            idx = np.in1d(q2, rm)
            q2 = q2[~idx]

            q3 = np.asarray(jpg3)
            idx = np.in1d(q3, rm)
            q3 = q3[~idx]

            try:
                if (q1 != q2).any() or (q1 != q3).any():
                    continue
            except ValueError:
                continue

            ved = ved.split('-')[1]

            for jpg in q1:
                name_id = jpg.split('.')[0]

                if not name_id is mas_brak_fon:

                    path_jpg_1 = os.path.join(papka_1, jpg)
                    path_jpg_2 = os.path.join(papka_2, jpg)

                    im1 = Image.open(path_jpg_1)
                    im2 = Image.open(path_jpg_2)

                    # create_mask
                    create_mask(ved, im1, name_id, pix, kadr='1', k='big')
                    create_mask(ved, im2, name_id, pix, kadr='2', k='big')

                    try:
                        # вставка на фон
                        mask_im1 = Image.open(f'mask-pix_{name_id}_1_big.jpg')
                        mask_im2 = Image.open(f'mask-pix_{name_id}_2_big.jpg')
                        mask_im1_blur = mask_im1.filter(ImageFilter.GaussianBlur(1))
                        mask_im2_blur = mask_im2.filter(ImageFilter.GaussianBlur(1))
                    except FileNotFoundError:
                        break

                    im_big_kal_c = Image.open("241/в печать 15/Calendar_320х620_2022-23год_Шаблон.jpg")

                    basewidth = 1200
                    wpercent = (basewidth / float(im1.size[0]))
                    hsize = int((float(im1.size[1]) * float(wpercent)))
                    im1 = im1.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                    wpercent = (basewidth / float(mask_im1_blur.size[0]))
                    hsize = int((float(mask_im1_blur.size[1]) * float(wpercent)))
                    mask_im1_blur = mask_im1_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                    wpercent = (basewidth / float(im2.size[0]))
                    hsize = int((float(im2.size[1]) * float(wpercent)))
                    im2 = im2.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                    wpercent = (basewidth / float(mask_im2_blur.size[0]))
                    hsize = int((float(mask_im2_blur.size[1]) * float(wpercent)))
                    mask_im2_blur = mask_im2_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                    # im_big_kal_c.paste(im2, (1320, 56), mask_im2_blur)
                    # im_big_kal_c.paste(im1, (40, 3282), mask_im1_blur)
                    im_big_kal_c.paste(im2, (100, 60), mask_im2_blur)
                    im_big_kal_c.paste(im1, (1250, 3285), mask_im1_blur)

                    # нумерация
                    draw = ImageDraw.Draw(im_big_kal_c)
                    font = ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 25)
                    draw.text((2312, 3230), f"{name_id}", (0, 0, 0), font=font)
                    # save
                    path_out = os.path.join(path_create_papka, ved, f'{pp["в печать 15"]}', f'{name_id}.jpg')
                    im_big_kal_c.save(path_out, dpi=(200, 200), quality=95)

                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 15"]}', f'{name_id}.jpg')
                    im_big_kal_c.save(path_out, dpi=(200, 200), quality=95)

                    # водяной знак
                    im_voda = Image.open('241/в печать 15/водяной_биг.png')
                    maxsize = (458, 458)
                    im_big_kal_c.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_big_kal_c.paste(im_voda, mask=im_voda)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 15"]}', f'{name_id}.jpg')
                    im_big_kal_c.save(path_out, dpi=(60, 60))

                    im1.close()
                    im2.close()
                    mask_im1.close()
                    mask_im2.close()
                    im_voda.close()
                    im_big_kal_c.close()

                    # удаление масок
                    os.remove(f'mask-pix_{name_id}_1_big.jpg')
                    os.remove(f'mask-pix_{name_id}_2_big.jpg')
                else:
                    break


def v_pechat_12(pix):  # в печать 12 1 5 13 10 8

    for ved in vedomosti:

        id_region = ved.split('-')[2]
        if int(id_region) < 100:

            papka_1 = os.path.join(path_krytilka, ved, "СКом", "01_К")
            papka_2 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_2_К")
            papka_3 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_3_К")
            jpg1 = sorted(os.listdir(papka_1))
            jpg2 = os.listdir(papka_2)
            jpg3 = os.listdir(papka_3)

            # проверка верстки
            rm = np.array(['Thumbs.db', '.DS_Store'])
            q1 = np.asarray(jpg1)
            idx = np.in1d(q1, rm)
            q1 = q1[~idx]

            q2 = np.asarray(jpg2)
            idx = np.in1d(q2, rm)
            q2 = q2[~idx]

            q3 = np.asarray(jpg3)
            idx = np.in1d(q3, rm)
            q3 = q3[~idx]

            try:
                if (q1 != q2).any() or (q1 != q3).any():
                    continue
            except ValueError:
                continue

            ved = ved.split('-')[1]
            # kol_vo_1 = len(q1)

            for jpg in q1:

                name_id = jpg.split('.')[0]
                name_reg = name_id.split('-')[0]

                if not name_id is mas_brak_fon:

                    path_jpg_1 = os.path.join(papka_1, jpg)
                    path_jpg_2 = os.path.join(papka_2, jpg)
                    path_jpg_3 = os.path.join(papka_3, jpg)

                    im1 = Image.open(path_jpg_1)
                    im2 = Image.open(path_jpg_2)
                    im3 = Image.open(path_jpg_3)

                    # create_mask
                    create_mask(ved, im1, name_id, pix, kadr='1', k='v2')
                    create_mask(ved, im2, name_id, pix, kadr='2', k='v2')

                    try:
                        # вставка на фон
                        mask_im1 = Image.open(f'mask-pix_{name_id}_1_v2.jpg')
                        mask_im2 = Image.open(f'mask-pix_{name_id}_2_v2.jpg')
                        mask_im1_blur = mask_im1.filter(ImageFilter.GaussianBlur(1))
                        mask_im2_blur = mask_im2.filter(ImageFilter.GaussianBlur(1))
                    except FileNotFoundError:
                        break

                    if name_reg == '016' or name_reg == '16':
                        im_foto_flag = Image.open('241/в печать 12/казань.jpg')
                    elif name_reg == "002" or name_reg == "02":
                        im_foto_flag = Image.open('241/в печать 12/уфа.jpg')
                    else:
                        im_foto_flag = Image.open('241/в печать 12/флаг.jpg')

                    im_foto_flag_dyma = Image.open('241/в печать 12/флаг и дума.jpg')
                    im_foto_sh = Image.open('241/в печать 12/в печать 2 шаблон.jpg')
                    im_ramka = Image.open('241/в печать 12/10x15 рамка.png')
                    im_big = Image.open('241/в печать 12/фон.jpg')
                    im_kal_poster_sh = Image.open('241/в печать 10/календарь 2022-2023.jpg')
                    im_kal_poster = Image.open('241/в печать 10/календарь 2022-2023.png')
                    im_poster_big_sh = Image.open('241/в печать 8/210х297 с окном.jpg')
                    im_poster_big = Image.open('241/в печать 8/210х297 с окном.png')

                    # размер im1
                    basewidth = 1300
                    wpercent = (basewidth / float(im1.size[0]))
                    hsize = int((float(im1.size[1]) * float(wpercent)))
                    im1 = im1.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    wpercent = (basewidth / float(mask_im1_blur.size[0]))
                    hsize = int((float(mask_im1_blur.size[1]) * float(wpercent)))
                    mask_im1_blur = mask_im1_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    # флаг
                    im_foto_flag.paste(im1, (-90, 40), mask_im1_blur)
                    im_foto_flag.paste(im_ramka, mask=im_ramka)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 1"]}', f'{name_id}.jpg')
                    im_foto_flag.save(path_out, dpi=(300, 300), quality=95)

                    # размер im2
                    basewidth = 1250
                    wpercent = (basewidth / float(im2.size[0]))
                    hsize = int((float(im2.size[1]) * float(wpercent)))
                    im2 = im2.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    wpercent = (basewidth / float(mask_im2_blur.size[0]))
                    hsize = int((float(mask_im2_blur.size[1]) * float(wpercent)))
                    mask_im2_blur = mask_im2_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    # дума
                    im_foto_flag_dyma.paste(im2, (-90, 80), mask_im2_blur)
                    im_foto_flag_dyma.paste(im_ramka, mask=im_ramka)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 13"]}', f'{name_id}.jpg')
                    im_foto_flag_dyma.save(path_out, dpi=(300, 300), quality=95)

                    # размер im3
                    basewidth = 1775
                    wpercent = (basewidth / float(im3.size[0]))
                    hsize = int((float(im3.size[1]) * float(wpercent)))
                    im3 = im3.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    # в печать 5
                    im_big.paste(im3, (0, 0))
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 5"]}', f'{name_id}.jpg')
                    im_big.save(path_out, dpi=(300, 300), quality=95)

                    # размер im3
                    basewidth = 1950
                    wpercent = (basewidth / float(im3.size[0]))
                    hsize = int((float(im3.size[1]) * float(wpercent)))
                    im3 = im3.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    # в печать 8
                    im_poster_big_sh.paste(im3, (235, 282))
                    im_poster_big_sh.paste(im_poster_big, (5, 0), mask=im_poster_big)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 8"]}', f'{name_id}.jpg')
                    im_poster_big_sh.save(path_out, dpi=(300, 300), quality=95)

                    # размер im3
                    basewidth = 1580
                    wpercent = (basewidth / float(im3.size[0]))
                    hsize = int((float(im3.size[1]) * float(wpercent)))
                    im3 = im3.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    # кал постер
                    im_kal_poster_sh.paste(im3, (71, 135))
                    im_kal_poster_sh.paste(im_kal_poster, mask=im_kal_poster)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 10"]}', f'{name_id}.jpg')
                    im_kal_poster_sh.save(path_out, dpi=(300, 300), quality=95)

                    # размер im3
                    basewidth = 1735
                    wpercent = (basewidth / float(im_big.size[0]))
                    hsize = int((float(im_big.size[1]) * float(wpercent)))
                    im_big = im_big.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                    # вставка 3х фоток в одну большую
                    im_foto_sh_im3 = im_big.rotate(90, expand=True)
                    im_foto_sh.paste(im_foto_sh_im3, (42, 53))
                    im_foto_sh.paste(im_foto_flag_dyma, (4, 1818))
                    im_foto_sh.paste(im_foto_flag, (1214, 1820))

                    # нумерация
                    draw = ImageDraw.Draw(im_foto_sh)
                    font = ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 40)
                    draw.text((75, 3500), f"{name_id}", (255, 255, 255), font=font)

                    path_out = os.path.join(path_create_papka, ved, f'{pp["в печать 12"]}', f'{name_id}.jpg')
                    im_foto_sh.save(path_out, dpi=(300, 300), quality=95)

                    # водяной знак флаг
                    im_voda = Image.open('241/в печать 11/водяной .png')
                    maxsize = (355, 355)
                    im_foto_flag.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_foto_flag.paste(im_voda, mask=im_voda)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 1"]}', f'{name_id}.jpg')
                    im_foto_flag.save(path_out, dpi=(60, 60))
                    # водяной знак флаг дума
                    maxsize = (355, 355)
                    im_foto_flag_dyma.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_foto_flag_dyma.paste(im_voda, mask=im_voda)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 13"]}', f'{name_id}.jpg')
                    im_foto_flag_dyma.save(path_out, dpi=(60, 60))
                    # размер водяной знак
                    im_voda_big = Image.open('241/в печать 11/водяной .png')
                    maxsize = (355, 355)
                    im_big.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_big.paste(im_voda_big, (10, 0), mask=im_voda_big)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 5"]}', f'{name_id}.jpg')
                    im_big.save(path_out, dpi=(60, 60))
                    im_voda_big.close()
                    # водяной знак постер большой синий
                    im_voda_big = Image.open('241/в печать 11/водяной .png')
                    maxsize = (355, 355)
                    im_poster_big_sh.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_poster_big_sh.paste(im_voda_big, mask=im_voda_big)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 8"]}', f'{name_id}.jpg')
                    im_poster_big_sh.save(path_out, dpi=(60, 60))
                    # водяной знак календарь постер
                    maxsize = (355, 355)
                    im_kal_poster_sh.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_kal_poster_sh.paste(im_voda, mask=im_voda)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 10"]}', f'{name_id}.jpg')
                    im_kal_poster_sh.save(path_out, dpi=(60, 60))

                    im1.close()
                    im2.close()
                    im3.close()
                    mask_im1.close()
                    mask_im2.close()
                    im_foto_flag_dyma.close()
                    im_foto_sh.close()
                    im_ramka.close()
                    im_big.close()
                    im_kal_poster_sh.close()
                    im_foto_flag.close()
                    im_kal_poster.close()
                    im_poster_big_sh.close()
                    im_poster_big.close()
                    im_voda_big.close()

                    # удаление масок
                    os.remove(f'mask-pix_{name_id}_1_v2.jpg')
                    os.remove(f'mask-pix_{name_id}_2_v2.jpg')
                else:
                    break

        # else:
        #     continue

        # if int(id_region) < 100:
        # init(autoreset=True)
        # print(Fore.GREEN + f'[INFO] Прокрутил №__{ved}.\n')
        # time.sleep(0.1)


def img_kal_domik(pix):
    for ved in vedomosti:

        id_region = ved.split('-')[2]
        if int(id_region) < 100:

            papka_1 = os.path.join(path_krytilka, ved, "СКом", "01_К")
            papka_2 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_2_К")
            papka_3 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_3_К")

            jpg1 = sorted(os.listdir(papka_1))
            jpg2 = os.listdir(papka_2)
            jpg3 = os.listdir(papka_3)

            # проверка верстки
            rm = np.array(['Thumbs.db', '.DS_Store'])
            q1 = np.asarray(jpg1)
            idx = np.in1d(q1, rm)
            q1 = q1[~idx]

            q2 = np.asarray(jpg2)
            idx = np.in1d(q2, rm)
            q2 = q2[~idx]

            q3 = np.asarray(jpg3)
            idx = np.in1d(q3, rm)
            q3 = q3[~idx]

            try:
                if (q1 != q2).any() or (q1 != q3).any():
                    continue
            except ValueError:
                continue

            ved = ved.split('-')[1]

            for jpg in q1:
                name_id = jpg.split('.')[0]

                if not name_id is mas_brak_fon:

                    path_jpg_1 = os.path.join(papka_1, jpg)
                    path_jpg_3 = os.path.join(papka_3, jpg)

                    im1 = Image.open(path_jpg_1)
                    im3 = Image.open(path_jpg_3)

                    # create_mask
                    create_mask(ved, im1, name_id, pix, kadr='1', k='dom')

                    try:
                        # вставка на фон
                        mask_im1 = Image.open(f'mask-pix_{name_id}_1_dom.jpg')
                        mask_im1_blur = mask_im1.filter(ImageFilter.GaussianBlur(1))
                    except FileNotFoundError:
                        break

                    im_kal_domik = Image.open('241/кал_домик/Calendar-domik.png')
                    im_kal_domik_1 = Image.open('241/кал_домик/Calendar-domik-1.jpg')

                    maxsize = (885, 885)
                    im3.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im3 = im3.rotate(180, expand=True)

                    maxsize = (1120, 1120)
                    im1.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    mask_im1_blur.thumbnail(maxsize, Image.Resampling.LANCZOS)

                    im_kal_domik_1.paste(im3, (126, 240))
                    im_kal_domik_1.paste(im_kal_domik, mask=im_kal_domik)
                    im_kal_domik_1.paste(im1, (135, 1175), mask_im1_blur)

                    # нумерация
                    draw = ImageDraw.Draw(im_kal_domik_1)
                    font = ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 30)
                    draw.text((2185, 80), f"{name_id}", (0, 0, 0), font=font)

                    path_out = os.path.join(path_create_papka, ved, f'{pp["КАЛЕНДАРЬ-"]}', f'{name_id}.jpg')
                    im_kal_domik_1.save(path_out, dpi=(300, 300), quality=95)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["КАЛЕНДАРЬ-"]}', f'{name_id}.jpg')
                    im_kal_domik_1.save(path_out, dpi=(300, 300), quality=95)
                    # размер водяной знак
                    im_voda = Image.open('241/в печать 11/водяной .png')
                    maxsize = (333, 333)
                    im_kal_domik_1.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_kal_domik_1.paste(im_voda, mask=im_voda)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["КАЛЕНДАРЬ-"]}', f'{name_id}.jpg')
                    im_kal_domik_1.save(path_out, dpi=(60, 60))

                    im1.close()
                    im3.close()
                    mask_im1.close()
                    im_kal_domik.close()
                    im_kal_domik_1.close()
                    im_voda.close()

                    # удаление масок
                    os.remove(f'mask-pix_{name_id}_1_dom.jpg')
                else:
                    break


def img_magnit(pix):
    for ved in vedomosti:
        ImageFile.LOAD_TRUNCATED_IMAGES = True

        id_region = ved.split('-')[2]
        if int(id_region) < 100:

            papka_1 = os.path.join(path_krytilka, ved, "СКом", "01_К")
            papka_2 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_2_К")
            papka_3 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_3_К")

            jpg1 = sorted(os.listdir(papka_1))
            jpg2 = os.listdir(papka_2)
            jpg3 = os.listdir(papka_3)

            # проверка верстки
            rm = np.array(['Thumbs.db', '.DS_Store'])
            q1 = np.asarray(jpg1)
            idx = np.in1d(q1, rm)
            q1 = q1[~idx]

            q2 = np.asarray(jpg2)
            idx = np.in1d(q2, rm)
            q2 = q2[~idx]

            q3 = np.asarray(jpg3)
            idx = np.in1d(q3, rm)
            q3 = q3[~idx]

            try:
                if (q1 != q2).any() or (q1 != q3).any():
                    continue
            except ValueError:
                continue

            ved = ved.split('-')[1]

            for jpg in q1:
                name_id = jpg.split('.')[0]

                if not name_id is mas_brak_fon:

                    path_jpg_1 = os.path.join(papka_1, jpg)
                    path_jpg_2 = os.path.join(papka_2, jpg)

                    im1 = Image.open(path_jpg_1)
                    im2 = Image.open(path_jpg_2)

                    # create_mask
                    create_mask(ved, im1, name_id, pix, kadr='1', k='mag')
                    create_mask(ved, im2, name_id, pix, kadr='2', k='mag')

                    try:
                        # вставка на фон
                        mask_im1 = Image.open(f'mask-pix_{name_id}_1_mag.jpg')
                        mask_im2 = Image.open(f'mask-pix_{name_id}_2_mag.jpg')
                        mask_im1_blur = mask_im1.filter(ImageFilter.GaussianBlur(1))
                        mask_im2_blur = mask_im2.filter(ImageFilter.GaussianBlur(1))
                    except FileNotFoundError:
                        break

                    im_magnit_sh = Image.open('241/магнит/магнит_шаблон.jpg')
                    im_magnit_1 = Image.open('241/магнит/магнит-1.jpg')
                    im_magnit_2 = Image.open('241/магнит/магнит-2.jpg')
                    im_magnit_3 = Image.open('241/магнит/магнит-3.jpg')

                    # левый
                    # maxsize = (1050, 1050)
                    # im1.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    # mask_im1_blur.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    # im_magnit_1.paste(im1, (150, 180), mask_im1_blur)

                    # левый
                    maxsize = (900, 900)
                    im2.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    mask_im2_blur.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_magnit_1.paste(im2, (30, 30), mask_im2_blur)
                    # центр
                    maxsize = (900, 900)
                    im1.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    mask_im1_blur.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_magnit_2.paste(im1, (500, 30), mask_im1_blur)
                    # правый
                    maxsize = (900, 900)
                    im1.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    mask_im1_blur.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_magnit_3.paste(im1, (500, 30), mask_im1_blur)

                    # save магазин
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["Магнит-1"]}', f'{name_id}.jpg')
                    im_magnit_1.save(path_out, dpi=(300, 300), quality=95)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["Магнит-2"]}', f'{name_id}.jpg')
                    im_magnit_2.save(path_out, dpi=(300, 300), quality=95)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["Магнит-3"]}', f'{name_id}.jpg')
                    im_magnit_3.save(path_out, dpi=(300, 300), quality=95)

                    # save на печать
                    # im_magnit_1 = im_magnit_1.rotate(90, expand=True)
                    im_magnit_sh.paste(im_magnit_1, (33, 32))
                    im_magnit_sh.paste(im_magnit_2, (1240, 32))
                    im_magnit_sh.paste(im_magnit_3, (2455, 32))
                    # нумерация
                    draw = ImageDraw.Draw(im_magnit_sh)
                    font = ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 30)
                    draw.text((3465, 35), f"{name_id}", (0, 0, 0), font=font)
                    # save на печать
                    path_out = os.path.join(path_create_papka, ved, f'{pp["Магнит"]}', f'{name_id}.jpg')
                    im_magnit_sh.save(path_out, dpi=(300, 300), quality=95)

                    # водяной знак маг
                    im_voda_gor = Image.open('241/магнит/водяной_маг_горизонт.png')
                    im_voda = Image.open('241/в печать 11/водяной .png')
                    # im_magnit_1 = im_magnit_1.rotate(-90, expand=True)
                    # 1
                    maxsize = (337, 337)
                    im_magnit_1.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_magnit_1.paste(im_voda, mask=im_voda)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["Магнит-1"]}', f'{name_id}.jpg')
                    im_magnit_1.save(path_out, dpi=(60, 60))
                    # 2
                    maxsize = (236, 236)
                    im_magnit_2.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_magnit_2.paste(im_voda_gor, mask=im_voda_gor)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["Магнит-2"]}', f'{name_id}.jpg')
                    im_magnit_2.save(path_out, dpi=(60, 60))
                    # 3
                    maxsize = (236, 236)
                    im_magnit_3.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_magnit_3.paste(im_voda_gor, mask=im_voda_gor)
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["Магнит-3"]}', f'{name_id}.jpg')
                    im_magnit_3.save(path_out, dpi=(60, 60))

                    im1.close()
                    im2.close()
                    mask_im1.close()
                    mask_im2.close()
                    im_magnit_sh.close()
                    im_magnit_1.close()
                    im_magnit_2.close()
                    im_magnit_3.close()
                    im_voda_gor.close()
                    im_voda.close()

                    # удаление масок
                    os.remove(f'mask-pix_{name_id}_1_mag.jpg')
                    os.remove(f'mask-pix_{name_id}_2_mag.jpg')
                else:
                    break


def ptk_ppls(pix):  # постер 4 кал 12 конверт 1 2 5 календарь вымпел и биг магнит

    for ved in vedomosti:

        id_region = ved.split('-')[2]
        if int(id_region) > 100:

            # print(f"в работе №__{ved}")
            # time.sleep(0.2)

            papka_1 = os.path.join(path_krytilka, ved, "СКом", "01_К")
            papka_2 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_2_К")
            papka_3 = os.path.join(path_krytilka, ved, "СКом", "01_Кадр_3_К")
            jpg1 = sorted(os.listdir(papka_1))
            jpg2 = os.listdir(papka_2)
            jpg3 = os.listdir(papka_3)

            # проверка верстки
            rm = np.array(['Thumbs.db', '.DS_Store'])
            q1 = np.asarray(jpg1)
            idx = np.in1d(q1, rm)
            q1 = q1[~idx]

            q2 = np.asarray(jpg2)
            idx = np.in1d(q2, rm)
            q2 = q2[~idx]

            q3 = np.asarray(jpg3)
            idx = np.in1d(q3, rm)
            q3 = q3[~idx]

            try:
                if (q1 != q2).any() or (q1 != q3).any():
                    init(autoreset=True)
                    print(Fore.RED + f'[**ERROR**] имена jpg в №_{ved} не совпадают:\n ')
                    continue
            except ValueError:
                print(Fore.RED + f'[**ERROR**] количество jpg в №_{ved} не совпадает')
                continue

            ved = ved.split('-')[1]

            # kol_vo_1 = len(q1)
            # for jpg in tqdm(q1):
            for jpg in q1:
                name_id = jpg.split('.')[0]

                if not name_id is mas_brak_fon:

                    path_jpg_1 = os.path.join(papka_1, jpg)
                    path_jpg_2 = os.path.join(papka_2, jpg)
                    path_jpg_3 = os.path.join(papka_3, jpg)

                    im1 = Image.open(path_jpg_1)
                    im2 = Image.open(path_jpg_2)
                    im3 = Image.open(path_jpg_3)

                    # create_mask
                    create_mask(ved, im1, name_id, pix, kadr='1', k='ptk')

                    try:
                        # вставка на фон
                        mask_im1 = Image.open(f'mask-pix_{name_id}_1_ptk.jpg')
                        mask_im1_blur = mask_im1.filter(ImageFilter.GaussianBlur(1))
                    except FileNotFoundError:
                        break

                    im_v_shablon = Image.open(r'241/ПТК_ППЛС/в печать 12 шаблон.jpg')
                    im_v_shablon_png = Image.open(r'241/ПТК_ППЛС/в печать 12 шаблон.png')
                    im_10x15_shablon = Image.open(r'241/ПТК_ППЛС/10x15.jpg')
                    vimpel_shablon = Image.open(r'241/ПТК_ППЛС/вымпел.png')

                    if int(id_region) == 330:  # Ковров ППЛС
                        im_10x15_ = Image.open(r'241/ПТК_ППЛС/10x15 Ковров ППЛС.jpg')
                        im_poster = Image.open(r'241/ПТК_ППЛС/Постер Ковров ППЛС.jpg')
                        # im_kal_pryzinka = Image.open(r'241/ПТК_ППЛС/Календарь Ковров ППЛС.jpg')
                    elif int(id_region) == 512:  # Североморск
                        im_10x15_ = Image.open(r'241/ПТК_ППЛС/10х15 Североморск.jpg')
                        im_vimpel = Image.open(r"241\ПТК_ППЛС\вымпел северный.jpg")
                        im_magnit = Image.open(r"241\ПТК_ППЛС\магнит_СФ.jpg")
                        # im_poster = Image.open(r'241/ПТК_ППЛС/Постер Североморск Северодвинск.jpg')
                        # im_kal_pryzinka = Image.open(r'241/ПТК_ППЛС/Календарь Североморск.jpg')
                    elif int(id_region) == 291:  # Северодвинск
                        im_10x15_ = Image.open(r'241/ПТК_ППЛС/10х15 Северодвинск.jpg')
                        im_vimpel = Image.open(r"241\ПТК_ППЛС\вымпел северный.jpg")
                        im_magnit = Image.open(r"241\ПТК_ППЛС\магнит_СФ.jpg")
                        # im_poster = Image.open(r'241/ПТК_ППЛС/Постер Североморск Северодвинск.jpg')
                        # im_kal_pryzinka = Image.open(r'241/ПТК_ППЛС/Календарь Северодвинск.jpg')
                    elif int(id_region) == 391:  # Калининград ПТК
                        im_10x15_ = Image.open(r'241/ПТК_ППЛС/10х15 Калининград.jpg')
                        im_vimpel = Image.open(r"241\ПТК_ППЛС\вымпел балтийский.jpg")
                        im_magnit = Image.open(r"241\ПТК_ППЛС\магнит_БФ.jpg")
                        # im_poster = Image.open(r'241/ПТК_ППЛС/Постер Калининград.jpg')
                        # im_kal_pryzinka = Image.open(r'241/ПТК_ППЛС/Календарь Калининград.jpg')
                    else:
                        print(f" [** ERROR **] {id_region} - нет такого региона")
                        break

                    # в печать 12
                    # размер im1
                    basewidth = 1130
                    wpercent = (basewidth / float(im1.size[0]))
                    hsize = int((float(im1.size[1]) * float(wpercent)))
                    im1 = im1.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    wpercent = (basewidth / float(mask_im1_blur.size[0]))
                    hsize = int((float(mask_im1_blur.size[1]) * float(wpercent)))
                    mask_im1_blur = mask_im1_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                    # im_10x15_  Ковров  Северный флот
                    if int(id_region) == 330:
                        im_10x15_.paste(im1, (90, 270), mask_im1_blur)  # Ковров
                    elif int(id_region) == 291 or int(id_region) == 512:
                        im_10x15_.paste(im1, (90, 33), mask_im1_blur)  # Северный флот
                    elif int(id_region) == 391:
                        im_10x15_.paste(im1, (90, 4), mask_im1_blur)  # Калиниград
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 1"]}', f'{name_id}.jpg')
                    im_10x15_.save(path_out, dpi=(300, 300), quality=95)

                    # размер im2
                    basewidth = 1330
                    wpercent = (basewidth / float(im2.size[0]))
                    hsize = int((float(im2.size[1]) * float(wpercent)))
                    im2 = im2.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    im_10x15_shablon.paste(im2, (-20, 0))
                    # save
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 2"]}', f'{name_id}.jpg')
                    im_10x15_shablon.save(path_out, dpi=(300, 300), quality=95)

                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 5"]}', f'{name_id}.jpg')
                    im3.save(path_out, dpi=(300, 300), quality=95)

                    # вставка 3 фотки
                    im3 = im3.rotate(90, expand=True)
                    im_v_shablon.paste(im3, (12, 25))
                    im_v_shablon.paste(im2, (0, 1818))

                    im_v_shablon.paste(im_10x15_, (1214, 1800))
                    im_v_shablon.paste(im_v_shablon_png, mask=im_v_shablon_png)
                    # нумерация
                    draw = ImageDraw.Draw(im_v_shablon)
                    font = ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 40)
                    draw.text((80, 3500), f"{name_id}", (255, 255, 255), font=font)
                    # save
                    path_out = os.path.join(path_create_papka, ved, f'{pp["в печать 12"]}', f'{name_id}.jpg')
                    im_v_shablon.save(path_out, dpi=(300, 300), quality=95)
                    im3 = im3.rotate(270, expand=True)

                    # Магнит большой
                    basewidth = 900
                    wpercent = (basewidth / float(im1.size[0]))
                    hsize = int((float(im1.size[1]) * float(wpercent)))
                    im1 = im1.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    wpercent = (basewidth / float(mask_im1_blur.size[0]))
                    hsize = int((float(mask_im1_blur.size[1]) * float(wpercent)))
                    mask_im1_blur = mask_im1_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                    im_magnit.paste(im1, (20, 100), mask_im1_blur)

                    # нумерация
                    draw = ImageDraw.Draw(im_magnit)
                    font = ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 27)
                    draw.text((1570, 30), f"{name_id}", (0, 0, 0), font=font)
                    # save
                    path_out = os.path.join(path_create_papka, ved, f'{pp["Магнит"]}', f'{name_id}.jpg')
                    im_magnit.save(path_out, dpi=(300, 300), quality=95)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["Магнит"]}', f'{name_id}.jpg')
                    im_magnit.save(path_out, dpi=(300, 300), quality=95)

                    # # ПОСТЕР
                    # basewidth = 2550
                    # wpercent = (basewidth / float(im1.size[0]))
                    # hsize = int((float(im1.size[1]) * float(wpercent)))
                    # im1 = im1.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    # wpercent = (basewidth / float(mask_im1_blur.size[0]))
                    # hsize = int((float(mask_im1_blur.size[1]) * float(wpercent)))
                    # mask_im1_blur = mask_im1_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    #
                    # im_poster.paste(im1, (20, 267), mask_im1_blur)
                    # # нумерация
                    # draw = ImageDraw.Draw(im_poster)
                    # font = ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 35)
                    # draw.text((2171, 100), f"{name_id}", (0, 0, 0), font=font)
                    # # save
                    # path_out = os.path.join(path_create_papka, ved, f'{pp["ПОСТЕР"]}', f'{name_id}.jpg')
                    # im_poster.save(path_out, dpi=(300, 300), quality=95)
                    # path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["ПОСТЕР"]}', f'{name_id}.jpg')
                    # im_poster.save(path_out, dpi=(300, 300), quality=95)

                    # Вымпел
                    basewidth = 1750
                    wpercent = (basewidth / float(im1.size[0]))
                    hsize = int((float(im1.size[1]) * float(wpercent)))
                    im1 = im1.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    wpercent = (basewidth / float(mask_im1_blur.size[0]))
                    hsize = int((float(mask_im1_blur.size[1]) * float(wpercent)))
                    mask_im1_blur = mask_im1_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)

                    im_vimpel.paste(im1, (20, 600), mask_im1_blur)
                    im_vimpel.paste(vimpel_shablon, mask=vimpel_shablon)

                    # нумерация с поворотом
                    tim = Image.new('RGBA', (190, 50), (0, 0, 0, 0))
                    dr = ImageDraw.Draw(tim)
                    ft = ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 37)
                    dr.text((0, 0), f"{name_id}", font=ft, fill=(0, 0, 0))

                    tim = tim.rotate(90, expand=1)
                    im_vimpel.paste(tim, (1670, 1210), tim)

                    # save
                    path_out = os.path.join(path_create_papka, ved, f'{pp["Вымпел"]}', f'{name_id}.jpg')
                    im_vimpel.save(path_out, dpi=(300, 300), quality=95)
                    path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["Вымпел"]}', f'{name_id}.jpg')
                    # im_vimpel = im_vimpel.convert('CMYK')
                    im_vimpel.save(path_out, dpi=(300, 300), quality=95)

                    # # Календарь пружинка
                    # basewidth = 1400
                    # wpercent = (basewidth / float(im1.size[0]))
                    # hsize = int((float(im1.size[1]) * float(wpercent)))
                    # im1 = im1.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    # wpercent = (basewidth / float(mask_im1_blur.size[0]))
                    # hsize = int((float(mask_im1_blur.size[1]) * float(wpercent)))
                    # mask_im1_blur = mask_im1_blur.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    #
                    # im_kal_pryzinka.paste(im1, (650, 54), mask_im1_blur)
                    # # нумерация
                    # draw = ImageDraw.Draw(im_kal_pryzinka)
                    # font = ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 40)
                    # draw.text((3262, 120), f"{name_id}", (0, 0, 0), font=font)
                    # # save
                    # path_out = os.path.join(path_create_papka, ved, f'{pp["КАЛЕНДАРЬ-"]}', f'{name_id}.jpg')
                    # im_kal_pryzinka.save(path_out, dpi=(300, 300), quality=95)
                    # path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["КАЛЕНДАРЬ-"]}', f'{name_id}.jpg')
                    # im_kal_pryzinka.save(path_out, dpi=(300, 300), quality=95)

                    # # в печать 4 (203x305)
                    # basewidth = 2737
                    # wpercent = (basewidth / float(im3.size[0]))
                    # hsize = int((float(im3.size[1]) * float(wpercent)))
                    # im3 = im3.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    #
                    # im_203x305_fon = Image.open(r'241/ПТК_ППЛС/в печать 4 (203x305).jpg')
                    # im_203x305_fon.paste(im3, (-200, 0))
                    # # нумерация
                    # draw = ImageDraw.Draw(im_203x305_fon)
                    # font = ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 40)
                    # draw.text((100, 3500), f"{name_id}", (255, 255, 255), font=font)
                    # # save
                    # path_out = os.path.join(path_create_papka, ved, f'{pp["в печать 4"]}', f'{name_id}.jpg')
                    # im_203x305_fon.save(path_out, dpi=(300, 300), quality=95)
                    # path_out = os.path.join(path_create_papka, ved + "_P", f'{pp["в печать 4"]}', f'{name_id}.jpg')
                    # im_203x305_fon.save(path_out, dpi=(300, 300), quality=95)

                    # размер im3 konvert
                    maxsize = (629, 629)
                    im3.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    path_out = os.path.join(path_create_papka, ved, f'{pp["Konvert"]}', f'{name_id}.jpg')
                    im3.save(path_out, dpi=(200, 200))

                    im_voda = Image.open(r'241/в печать 11/водяной .png')
                    # # водяной знак в постер
                    # maxsize = (355, 355)
                    # im_poster.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    # im_poster.paste(im_voda, mask=im_voda)
                    # path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["ПОСТЕР"]}', f'{name_id}.jpg')
                    # im_poster.save(path_out, dpi=(60, 60))

                    # # водяной знак в печать 4
                    # im_203x305_fon.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    # im_203x305_fon.paste(im_voda, mask=im_voda)
                    # path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 4"]}', f'{name_id}.jpg')
                    # im_203x305_fon.save(path_out, dpi=(60, 60))

                    # водяной знак в печать 5
                    im3.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im3.paste(im_voda.resize(im3.size), (0, 0), mask=im_voda.resize(im3.size))
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 5"]}', f'{name_id}.jpg')
                    im3.save(path_out, dpi=(60, 60))

                    # водяной знак в печать 2
                    im_10x15_shablon.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_10x15_shablon.paste(im_voda.resize(im_10x15_shablon.size), (0, 0),
                                           mask=im_voda.resize(im_10x15_shablon.size))
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 2"]}', f'{name_id}.jpg')
                    im_10x15_shablon.save(path_out, dpi=(60, 60))

                    # водяной знак в печать 1
                    im_10x15_.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_10x15_.paste(im_voda.resize(im_10x15_.size), (0, 0), mask=im_voda.resize(im_10x15_.size))
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["в печать 1"]}', f'{name_id}.jpg')
                    im_10x15_.save(path_out, dpi=(60, 60))

                    # водяной магнит
                    im_magnit.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_magnit.paste(im_voda.resize(im_magnit.size), (0, 0), mask=im_voda.resize(im_magnit.size))
                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["Магнит"]}', f'{name_id}.jpg')
                    im_magnit.save(path_out, dpi=(60, 60))
                    # region
                    # # водяной знак календарь пружинка
                    # im_kal_pryzinka.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    # im_kal_pryzinka.paste(im_voda.resize(im_kal_pryzinka.size), (0, 0),
                    #                       mask=im_voda.resize(im_kal_pryzinka.size))
                    # path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["КАЛЕНДАРЬ-"]}', f'{name_id}.jpg')
                    # im_kal_pryzinka.save(path_out, dpi=(60, 60))
                    # endregion
                    # водяной вымпел
                    vimpel_V_png = Image.open("241/ПТК_ППЛС/вымпел_V.png")
                    vimpel_V_jpg = Image.open("241/ПТК_ППЛС/вымпел_V.jpg")
                    maxsize = (700, 700)
                    im_vimpel.thumbnail(maxsize, Image.Resampling.LANCZOS)
                    im_vimpel.paste(im_voda.resize(im_vimpel.size), (0, 0), mask=im_voda.resize(im_vimpel.size))
                    vimpel_V_jpg.paste(im_vimpel, (64, 15))
                    vimpel_V_jpg.paste(vimpel_V_png, mask=vimpel_V_png)

                    path_out = os.path.join(path_create_papka, ved + "_V", f'{pp["Вымпел"]}', f'{name_id}.jpg')
                    vimpel_V_jpg.save(path_out, dpi=(60, 60))

                    vimpel_V_png.close()
                    vimpel_V_jpg.close()
                    im1.close()
                    im2.close()
                    im3.close()
                    mask_im1.close()
                    # im_kal_pryzinka.close()
                    # im_203x305_fon.close()
                    # im_poster.close()
                    im_10x15_.close()
                    im_10x15_shablon.close()
                    im_v_shablon_png.close()
                    im_v_shablon.close()
                    im_voda.close()
                    im_vimpel.close()
                    im_magnit.close()
                    vimpel_shablon.close()

                    # удаление масок
                    os.remove(f'mask-pix_{name_id}_1_ptk.jpg')
                else:
                    break
        else:
            continue


def papka_Z():
    path_papka_v = r"D:\!!!__АРМИЯ__!!!\вед"
    vedomosti = os.listdir(path_papka_v)
    mas_ved_v = []

    for i in vedomosti:
        if "_V" in i:
            mas_ved_v.append(i)

    for v in mas_ved_v:
        ve = v.split("_")[0]
        vedd = ve + "_Z"
        path_k_papke = os.path.join(path_papka_v, v)
        q = os.listdir(path_k_papke)[0]
        path_k_jpg = os.path.join(path_papka_v, v, q)
        list_id = os.listdir(path_k_jpg)

        for jpg in list_id:
            id = jpg.split('.')[0]
            id_region = id.split("-")[0]

            if int(id_region) < 100:
                path_v_pech = os.path.join(path_k_papke, pp["в печать"], jpg)
                path_v_pech_1 = os.path.join(path_k_papke, pp["в печать 1"], jpg)
                path_v_pech_2 = os.path.join(path_k_papke, pp["в печать 2"], jpg)
                path_v_pech_3 = os.path.join(path_k_papke, pp["в печать 3"], jpg)
                path_v_pech_4 = os.path.join(path_k_papke, pp["в печать 4"], jpg)
                path_v_pech_5 = os.path.join(path_k_papke, pp["в печать 5"], jpg)
                path_v_pech_13 = os.path.join(path_k_papke, pp["в печать 13"], jpg)
                path_v_pech_15 = os.path.join(path_k_papke, pp["в печать 15"], jpg)
                path_kal_dom = os.path.join(path_k_papke, pp["КАЛЕНДАРЬ-"], jpg)
                path_mag_1 = os.path.join(path_k_papke, pp["Магнит-1"], jpg)
                path_mag_2 = os.path.join(path_k_papke, pp["Магнит-2"], jpg)
                path_mag_3 = os.path.join(path_k_papke, pp["Магнит-3"], jpg)

                shablon_Z = Image.open("241/ПТК_ППЛС/Бланк.jpg")

                v_pech = Image.open(path_v_pech).resize((511, 767))
                v_pech_1 = Image.open(path_v_pech_1).resize((420, 630))
                v_pech_2 = Image.open(path_v_pech_2).resize((420, 630))
                v_pech_3 = Image.open(path_v_pech_3).resize((523, 705))
                v_pech_4 = Image.open(path_v_pech_4).resize((420, 630))
                v_pech_5 = Image.open(path_v_pech_5).resize((522, 701))
                v_pech_13 = Image.open(path_v_pech_13).resize((420, 630))
                v_pech_15 = Image.open(path_v_pech_15).resize((584, 1128))
                kal_dom = Image.open(path_kal_dom).resize((577, 814))
                mag_1 = Image.open(path_mag_1).resize((522, 367))
                mag_2 = Image.open(path_mag_2).resize((522, 367))
                mag_3 = Image.open(path_mag_3).resize((522, 367))

                shablon_Z.paste(v_pech)
                shablon_Z.paste(v_pech_1, (506, 1640))
                shablon_Z.paste(v_pech_2, (507, 888))
                shablon_Z.paste(v_pech_3, (561, 0))
                shablon_Z.paste(v_pech_4, (0, 880))
                shablon_Z.paste(v_pech_5, (1127, 0))
                shablon_Z.paste(v_pech_13, (0, 1650))
                shablon_Z.paste(v_pech_15, (1697, 0))
                shablon_Z.paste(kal_dom, (1709, 1379))
                shablon_Z.paste(mag_1, (1074, 880))
                shablon_Z.paste(mag_2, (1074, 1396))
                shablon_Z.paste(mag_3, (1074, 1917))

                path_out = os.path.join(path_create_papka, vedd, f'{id}.jpg')
                shablon_Z.save(path_out, dpi=(300, 300), quality=95)

                shablon_Z.close()
                v_pech.close()
                v_pech_1.close()
                v_pech_2.close()
                v_pech_3.close()
                v_pech_4.close()
                mag_1.close()
                mag_3.close()
                mag_2.close()
                kal_dom.close()
                v_pech_15.close()
                v_pech_13.close()
                v_pech_5.close()


if __name__ == '__main__':

    multiprocessing.freeze_support()
    Flg = 0
    print("241__Призыв_ПТК_ППЛС (с магнитом и вымпелом):  версия - 06.06.24")

    # удаление png и mask
    pyt = os.getcwd()
    put = os.listdir(pyt)
    for i in put:
        if os.path.isfile(i):
            png = i.split('.')[1]
            mask = i.split('-')[0]
            if png == "png" or mask == "mask":
                png_path = os.path.join(pyt, i)
                os.remove(png_path)

    pix = input('введите pix: ')
    if pix == '':
        pix = "2"

    d1 = datetime.datetime.now()  # 2024-07-06 14:32:20.266667
    # if d1.year == 2025 and d1.month == 7:
    if d1.year == 2024 and d1.month == 12:
        print("[ERROR -~ 1558] Обратитесь в тех. поддержку")
        sys.exit(0)

    mas = []

    print(f"-> в работе: {len(vedomosti)} ведомости(ей)\n")
    # создание папок
    for ved in vedomosti:

        ved = ved.split('-')[1]

        for p in pp:
            pap1 = os.path.join(path_create_papka, ved, p)
            pap2 = os.path.join(path_create_papka, ved + "_V", p)
            pap3 = os.path.join(path_create_papka, ved + "_P", p)
            pap4 = os.path.join(path_create_papka, ved + "_Z", p)

            if not os.path.isdir(pap1):
                try:
                    os.makedirs(pap1)
                    os.makedirs(pap2)
                    os.makedirs(pap3)
                    os.makedirs(pap4)
                except FileExistsError:
                    print("[*** ERROR ***] Папки существуют! Удалите прокрученные папки")
            else:
                print(f'[INFO] папка {pap1} существует')

    # thread2 = threading.Thread(target=add_req2, args=(q,), daemon=True)

    p = multiprocessing.Process(target=v_pechat, args=(pix,))
    p1 = multiprocessing.Process(target=v_pechat_11, args=(pix,))
    p2 = multiprocessing.Process(target=v_pechat_12, args=(pix,))
    p3 = multiprocessing.Process(target=img_magnit, args=(pix,))
    p4 = multiprocessing.Process(target=img_kal_domik, args=(pix,))
    p5 = multiprocessing.Process(target=img_big_kal, args=(pix,))
    p7 = multiprocessing.Process(target=ptk_ppls, args=(pix,))
    p6 = multiprocessing.Process(target=key_exit)  # .start()

    mas.append(p)
    mas.append(p1)
    mas.append(p2)
    mas.append(p3)
    mas.append(p4)
    mas.append(p5)
    # mas.append(p6)
    mas.append(p7)

    p.start()
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
    p6.start()
    p7.start()

    for m in mas:
        m.join()

    with open('прокрутил вед.txt', 'a', encoding='utf-8') as prokrytil:
        prokrytil.write("ДАТА: " + str(d1) + '\n')

        # удаление пустых папок и сумма jpg
        sum_jpg = 0
        for ved in vedomosti:
            ved = ved.split('-')[1]
            prokrytil.write("ВЕД: " + ved + '\n')
            for p in pp:
                pap1 = os.path.join(path_create_papka, ved, p)
                pap2 = os.path.join(path_create_papka, ved + "_V", p)
                pap3 = os.path.join(path_create_papka, ved + "_P", p)
                pap4 = os.path.join(path_create_papka, ved + "_Z", p)

                if os.path.isdir(pap1):
                    if not os.listdir(pap1):
                        os.rmdir(pap1)
                if os.path.isdir(pap2):
                    if not os.listdir(pap2):
                        os.rmdir(pap2)
                if os.path.isdir(pap3):
                    if not os.listdir(pap3):
                        os.rmdir(pap3)
                if os.path.isdir(pap4):
                    if not os.listdir(pap4):
                        os.rmdir(pap4)
            try:
                q = f"D:\\!!!__АРМИЯ__!!!\\вед\\{ved}\\Konvert\\"
                qq = os.listdir(q)
                kol_vo_jpg = len(qq)
                sum_jpg = sum_jpg + kol_vo_jpg
            except FileNotFoundError:
                print(f"[*ERROR*] Системе не удается найти указанный путь: 'D:\\!!!__АРМИЯ__!!!\\{ved}\\Konvert\\'")

    # прокрутка папки Z
    papka_Z()

    print('**ГОТОВО ПРОКРУТИЛ**')
    d2 = datetime.datetime.now()
    print(f'Количество jpg: {sum_jpg}')
    print(f"ВРЕМЯ: {d2 - d1}\n--------------------------------------------------\n")

    # копирование папок в места не столь отдаленные

    enter = input("Копировать прокрученные папки? (Нажать Enter):")

    if enter == "":
        input_papki = os.listdir(path_create_papka)

        os.chdir(path_create_papka)  # смена директории

        priz = "241"
        path_To_print = f"T:\\{priz}\\{priz}_TO_print"
        path_V = f"T:\\{priz}\\{priz}_VIEW"
        path_P = f"T:\\{priz}\\{priz}_PRINT"
        path_Z = f"T:\\{priz}\\{priz}_Z\Комплект"
        path_Archiv = f"Y:\\{priz}-Архив"

        for i_p in tqdm(input_papki, total=len(input_papki) - 1):

            if os.path.isdir(i_p):
                if "крутить" in i_p:
                    break
                elif "P" in i_p:
                    path_out = os.path.join(path_P, i_p)
                elif "V" in i_p:
                    path_out = os.path.join(path_V, i_p)
                elif "Z" in i_p:
                    path_out = os.path.join(path_Z, i_p)
                else:
                    path_out = os.path.join(path_To_print, i_p)

                try:
                    shutil.copytree(i_p, path_out, dirs_exist_ok=True)
                except:
                    print(f"[*ERROR*] не скопировал {i_p} в {path_out}")

        for i_p in input_papki:
            if "крутить" in i_p:
                break
            shutil.rmtree(i_p)

        os.chdir(path_krytilka)  # смена директории

        # копируем в архив и удаляем
        for vv in vedomosti:
            pt = os.path.join(path_Archiv, vv)
            try:
                shutil.copytree(vv, pt, dirs_exist_ok=True)
            except:
                print(f"[*ERROR*] не скопировал в архив")
            try:
                shutil.rmtree(vv)
            except:
                print(f"[*ERROR*] не удалил")

        print('** КОПИРНУЛ и УДАЛИЛ **')
        print('[INFO] Теперь можно и рюмочку оформить...')
