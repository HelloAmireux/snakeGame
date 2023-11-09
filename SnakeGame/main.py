import math
import random

import cvzone
import cv2
import numpy as np
from  cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)#这里写2会报错
cap.set(3, 1280)#宽
cap.set(4, 720)#高


detector=HandDetector(detectionCon=0.8,maxHands=1)

class SnakeGameClass:
    def __init__(self,pathFood):
        self.points = [] #蛇的全部节点
        self.lengths = [] #蛇的每个结点的长度
        self.currentLength =0 #蛇的当前的长度
        self.allowedLength = 150 #蛇的总长度
        self.previousHead = 0, 0 #蛇的当前的头

        self.imgFood=cv2.imread(pathFood,cv2.IMREAD_UNCHANGED)
        self.hFood,self.wFood,_=self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()
        self.score=0 #分数
        self.gameOver=False

    def randomFoodLocation(self):
        self.foodPoint= random.randint(100,1000),random.randint(100,600)

    def update(self,imgMain,currentHead):

        if self.gameOver:
            cvzone.putTextRect(imgMain,"Game Over",[300,400],scale=7,thickness=5,offset=20)
            cvzone.putTextRect(imgMain, f'YourScore:{self.score}', [300, 550], scale=7, thickness=5, offset=20)

        else:

            px, py = self.previousHead
            cx, cy = currentHead

            self.points.append([cx,cy])
            distance = math.hypot(cx-px,cy-py)#距离
            self.lengths.append(distance)
            self.currentLength +=distance#长度加上去
            self.previousHead= cx,cy#更新当前的长度

            #长度减少
            if self.currentLength > self.allowedLength:
                for i,length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength<self.allowedLength:
                        break

            #检测是否吃到食物
            rx, ry =self.foodPoint
            if rx -self.wFood//2 <cx < rx+self.wFood//2 and ry - self.hFood//2  < cy < ry+self.hFood//2:
                # print("ate")
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score +=1
                print(self.score)






            # 画蛇
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:#不是第一个值
                      cv2.line(imgMain,self.points[i-1],self.points[i],(0,0,255),20)#红色的
                cv2.circle(img, self.points[-1], 20, (200, 0, 200), cv2.FILLED)  # 点的大小

            # 画食物
            rx,ry =self.foodPoint
            imgMain =cvzone.overlayPNG(imgMain,self.imgFood,(rx-self.wFood//2,ry-self.hFood//2))
            cvzone.putTextRect(imgMain,f'Score:{self.score}',[50,80],scale=3,thickness=3,offset=10)


            # 检查碰撞
            pts = np.array(self.points[:-2], np.int32)  # 最后两个不要
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(imgMain, [pts], False, (0, 200, 0), 3)#后面的是颜色
            minDist=cv2.pointPolygonTest(pts,(cx,cy),True)


            if -1<= minDist <=1:
                print(minDist)
                self.gameOver=True
                self.points = []  # 蛇的全部节点
                self.lengths = []  # 蛇的每个结点的长度
                self.currentLength = 0  # 蛇的当前的长度
                self.allowedLength = 150  # 蛇的总长度
                self.previousHead = 0, 0  # 蛇的当前的头
                # self.score=0 #分数重置
                self.randomFoodLocation()



        return imgMain


game=SnakeGameClass("Donut.png")

while True:
    success, img = cap.read()
    img =cv2.flip(img,1)#翻转
    hands,img=detector.findHands(img,flipType=False)

    if hands:
        lmList=hands[0]['lmList']#二维
        pointIndex=lmList[8][0:2]#第八个节点，第0个在手心下面，前四个在大拇指，第八个正好在食指最上面
        game.update(img,pointIndex)
    cv2.imshow('Image',img)
    key=cv2.waitKey(1)#延迟一毫秒
    if key==ord('r'):
        game.gameOver=False
