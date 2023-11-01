#ライブラリのインストール
import cv2
import numpy as np
from PIL import Image
import math
from graphillion import GraphSet as gs
import collections

from PIL import ImageGrab
import cv2
import numpy as np
import sys
import time
import pyautogui
import win32gui
import win32con
import copy
import subprocess
import keyboard

paint="NoxPlayer"
#画像を表示する
def display(title,src):
    cv2.imshow(title,src)
    cv2.waitKey()#画像が表示されたウィンドウがキーボードの入力を待っている状態が続く

#浮動小数点を整数値に変える
def fl2int(data):
    data=[int(x) for x in data]# x を int(x) に変換した新しいリストを作る
    return data
#ゲームウィンドを前に持ってくる
def findWin2Fore(paint):
    hwnd= win32gui.FindWindow(None,paint)# 親ウィンドウハンドル(識別番号)を取得
    try:
        win32gui.SetForegroundWindow(hwnd)# アプリケーションをデスクトップの前面に表示
        return hwnd
    except:
        print("No Window")

#読み込んだ画像の変換。PIL形式の画像をOpenCV形式に変換して円を読み込めるように
def pil2cv(image):
    ''' PIL型 -> OpenCV型 '''
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image

# HSVの許容範囲(同一グループ判定に使用)
HUE_MARGIN = 50
SATURATION_MARGIN = 50
VALUE_MARGIN = 50

# ヒストグラム類似度の閾値(同一グループ判定に使用)
HISTOGRAM_SIMILARITY_THRESHOLD = 0.7

# 経路探索範囲(円同士が繋がっていると判定する距離)
SEARCH_RANGE = 85

# 円中心点からの矩形切り取り範囲(色情報の平均化に使用)
CUT_RECTANGLE = 10
# 距離計算関数(円と円の中心間の距離を三平方の定理で求める)
def distance(pos1, pos2):
    return math.sqrt((int(pos1[0]) - int(pos2[0])) ** 2 + (int(pos1[1]) - int(pos2[1])) ** 2)
#近距離座標のデータを連結
def distanceDataGet(circles, circle_id, retData):
    # circle_idが一致する基点データを抽出
    circle = [c for c in circles if  c['circle_id'] == circle_id]

    # 基点データを選択済とする
    circle[0]['select'] = True

    # 基点データとの距離が近い かつ 未選択のグループを取得
    nonSelectedGroup = [c for c in circles if not c['select'] and distance(circle[0]['position'], c['position']) <= SEARCH_RANGE ]

    for nonSelectedCircle in nonSelectedGroup:
        # 範囲内データに追加
        if not (circle_id, nonSelectedCircle['circle_id']) in retData and not (nonSelectedCircle['circle_id'], circle_id) in retData:
            retData.append((circle_id, nonSelectedCircle['circle_id']))

        # 次の基点を指定して再帰呼び出し
        distanceDataGet(circles, nonSelectedCircle['circle_id'], retData)

    # 基点データの選択を解除
    circle[0]['select'] = False

    return retData
####経路探索用関数
'''
 処理名: 経路探索関数
 概要  : グループごとに最長経路を最大で1つ探索しリストを作成
 引数1 : グループ情報(全量)
'''

#３つ以上繋がったルートを探してる
def calcRoute(circle_groups):

    SelectionRoute = []

    # グループごとにループ
    for group in circle_groups:

        # 辺の集合「(1,2)(2,3)」を入れる
        retData = []

        # 辺の集合を作成する関数をコール
        # 各グループの各円を基点にして処理を行う
        retData = []
        for circle in group['circles']:
            _retData = []
            distanceDataGet(group['circles'], circle['circle_id'], _retData)

            # 保持している辺集合よりも要素が多い場合、保持
            if len(retData) < len(_retData):
                retData = _retData

        # 辺の集合最大値が2未満なら次グループへ
        if len(retData) < 2:
            continue

        # ユニバースの作成(retDataがそのままユニバースとして使用可能な形式)
        universe = retData

        # グラフセットの作成
        gs.set_universe(universe)

        # 最長経路探索を行う
        maxPath = []
        for startPoinst in tuple(set(sum(retData, ()))):
            for endPoint in tuple(set(sum(retData, ()))):

                if startPoinst == endPoint:
                    continue

                # 始点と終点を仮設定
                paths = gs.paths(startPoinst, endPoint)

                # 仮の最長経路を取得
                thisMaxPath = next(paths.max_iter())

                # 仮の最長経路と保持している最長経路の長い方を保持
                if len(maxPath) < len(thisMaxPath):
                    maxPath = thisMaxPath
                    s = startPoinst
                    e = endPoint

        # 選択経路変換
        # ※maxPathは辺の集合であり、実際に繋ぐ順番と異なる
        # そのため始点からの順番で選択順番リストを作る
        # リストはpositionを保持、その方が描画および選択する際に楽
        tmpRoute = []
        limit = len(maxPath)
        while len(tmpRoute) < limit:
            for c in range(len(maxPath)):
                #辺の集合体のため、双方から経路を繋いでい
                if maxPath[c][0] == s:
                    tmpRoute.append([c for c in group['circles'] if  c['circle_id'] == s][0]['position'])
                    s = maxPath[c][1]
                    maxPath.pop(c)
                    break
                if maxPath[c][1] == s:
                    tmpRoute.append([c for c in group['circles'] if  c['circle_id'] == s][0]['position'])
                    s = maxPath[c][0]
                    maxPath.pop(c)
                    break

        # 終点のpositionを保持
        tmpRoute.append([c for c in group['circles'] if  c['circle_id'] == e][0]['position'])

        # 選択経路に追加
        SelectionRoute.append(tmpRoute)

    return SelectionRoute

####範囲内データ抽出関数
'''
 処理名: 範囲内データ抽出関数
 概要  : 再帰呼び出しで繋がっているcircle_idタプルリストを作成
 引数1 : グループ内円情報(全量)
 引数2 : 基点の円情報
 引数3 : 繋がり情報(タプルのリスト)
'''
def detect_route(image):
    #global circles,cropped_img,cropped_img_arr,group,SelectionRoute,circle_groups
    global SelectionRoute
    global circles,copyRoute,circle_groups
    img = image
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)#円を発見するためのグレースケール化
    except:
        print('No Window')
        sys.exit()

    #canny = cv2.Canny(img, threshold1=10, threshold2=200)
    #display("CANNY",canny)


    ####①ハフ変換での円検出
    ##circles = cv2.HoughCircles(canny, cv2.HOUGH_GRADIENT, 1, 20, param1=25, param2=30, minRadius=10, maxRadius=27)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,
                 dp=1, minDist=20, param1=40, param2=40, minRadius=10, maxRadius=40)
    print(circles)
    #円の確認画面を表示する
    '''
    start=time.time()
    for circle in circles[0, :]:
        circle=fl2int(circle)
        # 円周を描画する
        cv2.circle(img, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
        # 中心点を描画する
        cv2.circle(img, (circle[0], circle[1]), 2, (0, 0, 255), 3)
    end=time.time()
    print(end-start)

    display("CIRCLE",img)
    '''
    
    p_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)#円を抜き取るためのグレースケール化
    p_img = Image.fromarray(p_img)

    if circles is not None:
        circles = np.uint16(np.around(circles))#（切り取り範囲を取得するために）円（ピクセル）を16ビットの整数型に変換
        circle_groups = []
        circle_id = 1

        ####②円のグループ化
        for i, circle in enumerate(circles[0, :]):
            #circle=fl2int(circle)
            # 切り取り範囲を取得
            left = max(0, circle[0] - circle[2] + CUT_RECTANGLE)
            upper = max(0, circle[1] - circle[2] + CUT_RECTANGLE)
            right = min(p_img.width, circle[0] + circle[2] - CUT_RECTANGLE)
            lower = min(p_img.height, circle[1] + circle[2] - CUT_RECTANGLE)

            # 円の中心から矩形範囲で切り取り（クロップ）
            try:
                cropped_img = p_img.crop((left, upper, right, lower))
                cropped_img_arr = np.array(cropped_img)

                # ヒストグラムを計算し平坦化
                hist = cv2.calcHist([cropped_img_arr], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                hist = cv2.normalize(hist, hist).flatten()

                # HSVに変換し平均値を取得
                hsv = cv2.cvtColor(cropped_img_arr, cv2.COLOR_RGB2HSV)
                hsv_avg = np.average(np.average(hsv, axis=0), axis=0)
            except:
                pass

            # 円情報をグループ化
            grouped = False
            for group in circle_groups:
                ref_hist = group['hist']
                similarity = cv2.compareHist(hist, ref_hist, cv2.HISTCMP_CORREL)
                ref_hsv_avg = group['hsv']

                # ヒストグラムの類似度とHSVの許容範囲を比較
                if similarity > HISTOGRAM_SIMILARITY_THRESHOLD and \
                    abs(hsv_avg[0] - ref_hsv_avg[0]) < HUE_MARGIN and \
                    abs(hsv_avg[1] - ref_hsv_avg[1]) < SATURATION_MARGIN and \
                    abs(hsv_avg[2] - ref_hsv_avg[2]) < VALUE_MARGIN:

                    group['circles'].append({
                        'circle_id': circle_id,
                        'position': (circle[0], circle[1]),
                        'radius': circle[2],
                        'select': False
                    })
                    grouped = True
                    break

            # 新規グループの場合
            if not grouped:
                circle_groups.append({
                    'circles': [{
                        'circle_id': circle_id,
                        'position': (circle[0], circle[1]),
                        'radius': circle[2],
                        'select': False
                    }],
                    'hist': hist,
                    'hsv': hsv_avg
                })
            circle_id += 17
        for circle in circles[0, :]:
            # 円周を描画する
            cv2.circle(img, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
            # 中心点を描画する
            cv2.circle(img, (circle[0], circle[1]), 2, (0, 0, 255), 3)

        #display("CIRCLE",img)



        # 最長経路リストを取得
        SelectionRoute = calcRoute(circle_groups)#関数で連結してるやつを探してる
        #print("SEL",SelectionRoute)
        copyRoute=copy.deepcopy(SelectionRoute)
        # 最長経路リストを描画
        for RouteStart in SelectionRoute:
            # 始点、終点(要素をずらした始点リストコピー)リストを作成する
            RouteEnd = RouteStart[1:] + RouteStart[:1]
            RouteStart.pop()
            RouteEnd.pop()
            # 矢印の描画
            for i, _ in enumerate(RouteStart):
                cv2.arrowedLine(img, RouteStart[i], RouteEnd[i], (0, 0, 0), 2)

        # capture display
        #cv2.imshow("Image", img)
        #cv2.waitKey()
        time.sleep(0.1)  # わずかな待機
        return copyRoute

import ctypes
#指定ウィンドウのスクリーンショットを取るだけ
def grab():
    global hwnd
    # ウィンドウサイズを取得
    window_size = win32gui.GetWindowRect(hwnd)
    # ずれを調整
    f = ctypes.windll.dwmapi.DwmGetWindowAttribute
    rect = ctypes.wintypes.RECT()
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    f(  ctypes.wintypes.HWND(hwnd),
        ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
        ctypes.byref(rect),
        ctypes.sizeof(rect)
    )
    # 取得したウィンドウサイズでスクリーンショットを撮る
    image = ImageGrab.grab(window_size)
    return image

#NoxPlayerを前面に持って来て
def get_win():
    global hwnd,paint ,window_size,image
    hwnd=findWin2Fore(paint)#L32の関数（前に持ってくる）
    if hwnd:
        # 1秒待つ
        time.sleep(1)
        # ウィンドウサイズを取得
        window_size = win32gui.GetWindowRect(hwnd)
        # 取得したウィンドウサイズでスクリーンショットを撮る
        image=grab()#L317関数（ウィンドウショットとる）
        imagecv=pil2cv(image)#L41関数（CVに変換）
        return hwnd,imagecv,window_size
    else:
        print('入力したタイトルに一致するウィンドウがありません')

#get_win()の実行。hwnd,image,w_sizeを返す。
hwnd,image,w_size=get_win()
#print("Window Handle",hwnd)
#display("IMG",image)

#L186関数。image 内の経路を検出し、SelectionRoute にその情報を格納
SelectionRoute=detect_route(image)

w=w_size[2]-w_size[0]
h=w_size[3]-w_size[1]
win32gui.MoveWindow(hwnd, 0, 0, w, h, True)
window_size = win32gui.GetWindowRect(hwnd)

#１秒ごとにスクリーンショットを取り、経路探索をしてマウスでなぞる処理をする
for i in range(3):
    # 取得したウィンドウサイズでスクリーンショットを撮る
    image = ImageGrab.grab(window_size)

    print("SEL",SelectionRoute)
    for i in range(len(SelectionRoute)):
        data=SelectionRoute[i]
        start=[1,0]
        check=1
        #print(data)
        for x,y in data:
            if check:
                pyautogui.moveTo(x, y)#マウスを指定された座標 (x, y) に移動させる
                pyautogui.mouseDown()#マウスの左ボタンを押し続ける
                check=start[check]
            else:
                pyautogui.moveTo(x, y)
                pyautogui.mouseDown()
        pyautogui.mouseUp()#マウスの左ボタンを離す
    time.sleep(1)
sys.exit()
