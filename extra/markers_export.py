# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 14:05:49 2022

@author: ilia
"""
import cv2
import numpy as np

aruco = cv2.aruco
p_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
camera = cv2.VideoCapture(0)


def saveMarkersToFile():
    marker =  [0] * 4 #Initialization
    for i in range(len(marker)):
        marker[i] = aruco.drawMarker(p_dict, i, 75) # 75x75 px
        cv2.imwrite(f'marker{i}.svg', marker[i])
        
        
def DetectMarkers():
    while True:
        
        imgtaken, img = camera.read()
        if imgtaken:
            corners, ids, rejectedImgPoints = aruco.detectMarkers(img, p_dict) #detection
            img_marked = aruco.drawDetectedMarkers(img.copy(), corners, ids)   #Overlay detection results
            cv2.imshow('Markers', img_marked) #display
        
        key = cv2.waitKey(3)
        if key == ord('q'):
            cv2.destroyAllWindows()
            break
    
def ConvertImage():
    while True:
        
        imgtaken, img = camera.read()
        if imgtaken:
            cv2.imshow('Original', img)
            corners, ids, rejectedImgPoints = aruco.detectMarkers(img, p_dict) #detection
            img_marked = aruco.drawDetectedMarkers(img.copy(), corners, ids)   #Overlay detection results
            cv2.imshow('Marked', img_marked)
            
            #Store the "center coordinates" of the marker in m in order from the upper left in the clockwise direction.
            marks = m = np.empty((4,2))
            try:
                for i,c in zip(ids.ravel(), corners):
                        m[i] = c[0].mean(axis=0)
            except:
                pass
            finally:
                marks = m
            
            width, height = (500,500) #Image size after transformation
            
            marker_coordinates = np.float32(marks)
            true_coordinates   = np.float32([[0,0],[width,0],[width,height],[0,height]])
            try:
                trans_mat = cv2.getPerspectiveTransform(marker_coordinates,true_coordinates)
                img_trans = cv2.warpPerspective(img,trans_mat,(width, height))
                cv2.imshow('Converted', img_trans)
            except:
                pass
                ###cv2.imshow('Converted', img_trans)
                
        
        key = cv2.waitKey(3)
        if key == ord('q'):
            cv2.destroyAllWindows()
            break
    
    
    
saveMarkersToFile()

camera.release()