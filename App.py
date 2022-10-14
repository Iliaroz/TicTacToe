# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 10:02:55 2022

@author: ilia
"""

from PyQt6 import QtGui, QtWidgets, QtGui, QtCore, uic
import sys, os, time
import cv2
import numpy as np
from enum import Enum
## model, detection
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import config_util
from object_detection.utils import visualization_utils
from object_detection.builders import model_builder


###########################################################
###########################################################
### Video detection classs
###########################################################
###########################################################

class VideoMode(Enum):
    Board = 1
    Original = 2
    Markers = 3
    Detections = 4

    
class VideoThread(QtCore.QThread):
    signal_change_pixmap = QtCore.pyqtSignal(np.ndarray)
    signal_detection_matrix = QtCore.pyqtSignal(np.ndarray)
    

    def __init__(self, videoPort, gameSize = 3):
        super().__init__()
        self.videoPort = videoPort
        self._run_flag = True
        self.gameSize = gameSize
        self.RedSign = -1
        self.BlueSign = 1
        self.width = 640
        self.height = 480
        self.mode = VideoMode.Original
        self.markers_dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.boardMarkers = np.empty((4,2))
        ### output videos
        self.image_original = {}
        self.image_original['available'] = False
        self.image_original['frame'] = self.generateImage("No video")
        self.image_board = {}
        self.image_board['available'] = False
        self.image_board['frame'] = self.generateImage("No board detected")
        self.image_markers = {}
        self.image_markers['available'] = False
        self.image_markers['frame'] = self.generateImage("No markers detected")
        self.image_detections = {}
        self.image_detections['available'] = False
        self.image_detections['frame'] = self.generateImage("No cups detected")
        
    ### -----------------------------------------
    ### ----------  thread and gui   ------------
    ### -----------------------------------------
    
    def setGameSize(self, size):
        self.gameSize = size

    def run(self):
        image_show = self.generateImage("Connecting...")
        self.signal_change_pixmap.emit(image_show)
        ## load detection model...
        self.initDetectionModel()
        # capture from web cam
        self.camera = cv2.VideoCapture(self.videoPort)
        flag_disconnect = False
        while self._run_flag:
            image_show = self.generateImage("No video device")
            if ((self.camera is None) or (not self.camera.isOpened()) or flag_disconnect == True):
                print ('Warning: unable to open video source: ', self.videoPort)
                try:
                    self.camera.release()
                except: pass
                del(self.camera)
                time.sleep(5)
                self.camera = cv2.VideoCapture(self.videoPort)
                flag_disconnect = False
            else:
                ret, image_camera = self.camera.read()
                if ret:
                    if self.isImageEmpty(image_camera):
                        print("Empty image!!!!!!!!!!!!!!!")
                        flag_disconnect = True
                else:
                    flag_disconnect = True
                self.ParseVideoFrame(ret, image_camera)
                image_show = self.getVideoFrameToShow()
            self.signal_change_pixmap.emit(image_show)
        # shut down capture system
        self.camera.release()
        ### end of thread
        
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

    ### -----------------------------------------
    ### ---------------  video   ----------------
    ### -----------------------------------------
    
    def getVideoFrameToShow(self):
        image_show = self.image_original['frame']
        if (self.mode == VideoMode.Board):
            image_show = self.image_board['frame']
        elif (self.mode == VideoMode.Markers):
            image_show = self.image_markers['frame']
        elif (self.mode == VideoMode.Detections):
            image_show = self.image_detections['frame']
        
        return image_show
        
    def isImageEmpty(self, image):
        """Check all image pixels are equal, that means, probably, it's fake image"""
        pixel= image[0, 0]
        res = (image[:,:] == pixel).all()
        return res
        
    def ParseVideoFrame(self, retrived, camera_image):
        if not retrived:
            self.image_original['frame'] = self.generateImage("No video")
            self.image_board['frame'] = self.generateImage("No video board")
            self.image_markers['frame'] = self.generateImage("No video markers")
            self.image_detections['frame'] = self.generateImage("No video detection")
            return
        
        # cv2.imshow('Original', camera_image)
        self.image_original['frame'] = camera_image
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(camera_image, self.markers_dictionary) #detection
        img_marked = cv2.aruco.drawDetectedMarkers(camera_image.copy(), corners, ids)   #Overlay detection results
        # cv2.imshow('Marked', img_marked)
        self.image_markers['frame'] = img_marked
        
        markers_number = len(corners)
        #Store the "center coordinates" of the marker in m in order from the upper left in the clockwise direction.
        m = np.empty((4,2))
        try:
            for i,c in zip(ids.ravel(), corners):
                m[i] = c[0][0] # board only ### c[0].mean(axis=0) # center of markers
        except:
            pass
        if markers_number == 4:
            self.boardMarkers = m
        
        
        width = height = min(self.width, self.height) #Image size after transformation
        
        marker_coordinates = np.float32(self.boardMarkers)
        true_coordinates   = np.float32([[0,0],[width,0],[width,height],[0,height]])
        try:
            trans_mat = cv2.getPerspectiveTransform(marker_coordinates,true_coordinates)
            img_trans = cv2.warpPerspective(camera_image,trans_mat,(width, height))
            # cv2.imshow('Converted', img_trans)
            self.image_board['frame'] = img_trans
        except:
            pass
        self.CupsPositionDetection(img_trans, (self.gameSize, self.gameSize))
        pass
    
    def generateImage(self, text):
        blank_image = np.zeros((self.height, self.width,3), np.uint8)
        blank_image[:,:] = (128,0,0)
        font                   = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10,self.width // 2)
        fontScale              = 1
        fontColor              = (255,255,255)
        thickness              = 2
        lineType               = 2
        
        cv2.putText(blank_image,text, 
            bottomLeftCornerOfText, 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)
        return blank_image

    ### -----------------------------------------
    ### ---------------  model   ----------------
    ### -----------------------------------------
    def initDetectionModel(self, ):
        MODEL_DIR = '.' + '/model/'
        
        pipeline_config = MODEL_DIR + 'pipeline.config'
        model_dir_test = MODEL_DIR + 'checkpoint/ckpt-0'
        configs = config_util.get_configs_from_pipeline_file(pipeline_config)
        model_config = configs['model']
        detection_model = model_builder.build(
                    model_config=model_config, is_training=False)
        
        ckpt = tf.compat.v2.train.Checkpoint(
                    model=detection_model)
        ckpt.restore(os.path.join(model_dir_test))
        # load labelmap, map them to it's labels and load the detector

        self.detect_fn = self.get_model_detection_function(detection_model)
        
        #map labels for inference decoding
        label_map_path = MODEL_DIR + 'labelmap.pbtxt'
        label_map = label_map_util.load_labelmap(label_map_path)
        categories = label_map_util.convert_label_map_to_categories(
                label_map,
                max_num_classes=label_map_util.get_max_label_map_index(label_map),
                use_display_name=True)
        self.detect_category_index = label_map_util.create_category_index(categories)
        self.detect_label_index = label_map_util.get_label_map_dict(label_map_path)
        label_map_dict = label_map_util.get_label_map_dict(label_map, use_display_name=True)
        

    def CupsPositionDetection(self, board_image, board_shape):
        FILL = 0.7
        DETECTION_THRESHOLD = 0.7
        def define_fit_boxes():
            BX = []
            H,W,_ = board_image.shape
            R,C = board_shape
            dH = int(H * FILL / R)
            dW = int(W * FILL / C)
            for r in range(C):
                for c in range(R):
                    x1 = int((r+0.5)*W/C - dW/2)
                    x2 = int((r+0.5)*W/C + dW/2)
                    y1 = int((c+0.5)*H/R - dH/2)
                    y2 = int((c+0.5)*H/R + dH/2)
                    BX.append(np.array([x1, y1, x2, y2]))
            return BX
            
        def draw_game_boxes():
            for box in game_fit_boxes:
                cv2.rectangle(
                    image_np_with_detections,
                    (box[0], box[1]),
                    (box[2], box[3]),
                    (0,255,0), # color in BGR
                    2, # thickness
                    )
        def draw_detected_boxes():
            visualization_utils.visualize_boxes_and_labels_on_image_array(
                        image_np_with_detections,
                        detections['detection_boxes'][0].numpy(),
                        (detections['detection_classes'][0].numpy() + label_id_offset).astype(int),
                        detections['detection_scores'][0].numpy(),
                        self.detect_category_index,
                        use_normalized_coordinates=True,
                        max_boxes_to_draw=20,
                        min_score_thresh=DETECTION_THRESHOLD,
                        agnostic_mode=False,
                        skip_scores=True,
            )
        def draw_detected_centers():
            boxes = detections['detection_boxes'][0].numpy()
            center_points = []
            for box in boxes:
                cp = np.array( [np.mean(box[0:3:2]), np.mean(box[1:4:2])])
                center_points.append(cp)
            center_points = np.asarray(center_points)
            visualization_utils.draw_keypoints_on_image_array(
                        image_np_with_detections,
                        center_points,
                        keypoint_scores=detections['detection_scores'][0].numpy(),
                        min_score_thresh=DETECTION_THRESHOLD,
                        color='red',
                        radius=self.height // 50 + 1,
                        use_normalized_coordinates=True,
                        keypoint_edges=None,
                        keypoint_edge_color='green',
                        keypoint_edge_width=2)
            
        def getDetectionCupsArray():
            #TODO: nightmare code, rewrite normally
            H,W,_ = board_image.shape
            R,C = board_shape
            newGB = np.zeros((R, C))
            detBx = detections['detection_boxes'][0].numpy()
            detCl = detections['detection_classes'][0].numpy()
            detSc = detections['detection_scores'][0].numpy()
            for i, dBx in enumerate(detBx):
                if ( detSc[i] >= DETECTION_THRESHOLD ):
                    cp = np.array( [W*np.mean(dBx[0:3:2]), H*np.mean(dBx[1:4:2])] )
                    for igb, gBx in enumerate(game_fit_boxes):
                        if (
                            (cp[0] > gBx[0]) and
                            (cp[1] > gBx[1]) and
                            (cp[0] < gBx[2]) and
                            (cp[1] < gBx[3])  ):
                            if ( detCl[i]+label_id_offset == self.detect_label_index['red'] ):    ## +1 because index start from 1 in label list
                                newGB[igb // R, igb % C] = self.RedSign
                            if ( detCl[i]+label_id_offset == self.detect_label_index['blue'] ):
                                newGB[igb // R, igb % C] = self.BlueSign
            return newGB
            
        ####
        ## IMAGE dETECTION
        ####
        ## convert to TF color format
        image_np =  cv2.cvtColor(board_image, cv2.COLOR_BGR2RGB)
        input_tensor = tf.convert_to_tensor(
                np.expand_dims(image_np, 0), dtype=tf.float32)
        detections, predictions_dict, shapes = self.detect_fn(input_tensor)
    
        label_id_offset = 1
        image_np_with_detections = image_np.copy()
        
        ## draw predictions and other stuff
        game_fit_boxes = define_fit_boxes()
        draw_game_boxes()
        draw_detected_boxes()
        draw_detected_centers()
        GB = getDetectionCupsArray()
        ###print(GB)
        self.signal_detection_matrix.emit(GB)
        
        ### back to openCV colorspace
        image_np_with_detections = cv2.cvtColor(image_np_with_detections, cv2. COLOR_RGB2BGR)
        self.image_detections['frame'] = image_np_with_detections
    
    
    def get_model_detection_function(self, model):
        """Get a tf.function for detection."""
    
        @tf.function
        def detect_fn(image):
            """Detect objects in image."""
    
            image, shapes = model.preprocess(image)
            prediction_dict = model.predict(image, shapes)
            detections = model.postprocess(prediction_dict, shapes)
    
            return detections, prediction_dict, tf.reshape(shapes, [-1])
    
        return detect_fn

###########################################################
###########################################################
### Application classs
###########################################################
###########################################################

class AppTicTacToe(QtWidgets.QMainWindow):
    class selectPlayerUI(QtWidgets.QDialog):
        def __init__(self, parent, usernum):
            super().__init__()
            uic.loadUi('user-select.ui', self)
            self.parent = parent
            self.usernum = usernum
            
            self.selection = None
    
            self.parent.setGameButtonIcon( self.btnHuman, "user" + str(self.usernum))
            self.parent.setGameButtonIcon( self.btnComputer, "dobot" + str(self.usernum))
            self.show()
    
        def btn_human_selected(self):
            print("settings Function call:" + "btn_human_selected")
            self.selection = "user"
            self.accept()
            pass
        
        def btn_computer_selected(self):
            print("settings Function call:" + "btn_computer_selected")
            self.selection = "dobot"
            self.accept()
            pass
    

    def __init__(self):
        super().__init__()
        uic.loadUi('app.ui', self)
        ## non-resizable main window
        self.setFixedSize(self.size())
        ## icons list
        self.icons = {
            "dobot1"    : "dobot1.png",
            "dobot2"    : "dobot2.png",
            "user1"     : "user1.png",
            "user2"     : "user2.png",
            "red"       : "red.png",
            "blue"      : "blue.png",
            "empty"     : "empty.png",
            }
        self.GameSize = 3
        self.setWindowTitle("Qt tic-tac-toe game")
        self.display_width = 320
        self.display_height = 240
        ## create the label that holds the image
        self.cameraImageLabel.resize(self.display_width, self.display_height)
        self.cameraImageLabel.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.cameraImageLabel.customContextMenuRequested.connect(self.video_on_context_menu)
        
        ## Log editors for read only
        self.logPlayer1.setReadOnly(True)
        self.logPlayer2.setReadOnly(True)
        ## player types (and images on button )
        self.Player1Type = "dobot"
        self.Player2Type = "user"
        
        self.makeGameArea()
        ## create the video capture thread
        self.threadVideo = VideoThread(0)
        ## connect its signal to the update_image slot
        self.threadVideo.signal_change_pixmap.connect(self.update_image)
        self.threadVideo.signal_detection_matrix.connect(self.update_game_buttons)
        ## start the thread
        #self.threadVideo.start()

    @property
    def Player1Type(self):
        return self._Player1Type
    @Player1Type.setter
    def Player1Type(self, val):
        self._Player1Type = val
        self.setPlayerPic(1, val)

    @property
    def Player2Type(self):
        return self._Player2Type
    @Player1Type.setter
    def Player2Type(self, val):
        self._Player2Type = val
        self.setPlayerPic(2, val)

    def closeEvent(self, event):
        print("Close event received.")
        self.threadVideo.stop()
        event.accept()

    def btn_player1_clicked(self):
        print("Player1 button clicked.")
        dialog = self.selectPlayerUI(self, 1)   # player number 1
        dialog.exec()
        print("Exit player selection dialog")
        if dialog.selection != None:
            self.Player1Type = dialog.selection
        pass

    def btn_player2_clicked(self):
        print("Player2 button clicked.")
        dialog = self.selectPlayerUI(self, 2)   # player number 2
        dialog.exec()
        print("Exit player selection dialog")
        if dialog.selection != None:
            self.Player2Type = dialog.selection
        pass

    def setPlayerPic(self, playernum, icon):
        """
        Set picture of player in user interface

        Parameters
        ----------
        playernum : TYPE
            DESCRIPTION.
        icon : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        path = os.path.dirname(os.path.abspath(__file__))
        lbl = self.findChild(QtWidgets.QLabel, 'lblPlayer' + str(playernum))
        lbl.setPixmap(QtGui.QPixmap(
            os.path.join(path, self.icons[icon + str(playernum)])).scaled(self.display_width, self.display_height, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        
    def btn_game_pressed(self, ):
        btn = self.sender()
        print("GameButton pressed.", 'r=', btn.row, 'c=', btn.col)
#        self.setGameButtonIcon(btn, "red")
        pass

        

    def setGameButtonIcon(self, btn, icon):
        """
        

        Parameters
        ----------
        btn : TYPE
            DESCRIPTION.
        icon : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        ico = QtGui.QIcon(self.icons[icon])
        btn.setIcon(ico)
        btn.setIconSize(btn.size())
        pass


    def makeGameArea(self):
        ## delete all existed buttons
        for i in reversed(range(self.gameLayout.count())): 
            self.gameLayout.itemAt(i).widget().setParent(None)
        ## create buttons
        for c in range(self.GameSize):
            for r in range(self.GameSize):
                btn = QtWidgets.QPushButton("")
                btn.setFixedSize(100,100)
                self.setGameButtonIcon(btn, "empty")
                btn.clicked.connect(self.btn_game_pressed)
                btn.row = r
                btn.col = c
                self.gameLayout.addWidget(btn, r, c)
                pass


    def video_on_context_menu(self, pos):
        contextMenu = QtWidgets.QMenu(self)
        Acts = []
        for i, mode in enumerate(VideoMode):
            act = QtGui.QAction(mode.name, self)
            act.modeToSwitch = mode
            Acts.append(act)
        contextMenu.addActions(Acts)
        action = contextMenu.exec(self.cameraImageLabel.mapToGlobal(pos))   ## contextMenu for cameraImageLabel only, so use it for position search
        ## pass action to video class
        if action != None:
            self.setVideoSource(action.modeToSwitch)

    def setVideoSource(self, mode):
        print("setVideoSource: mode=", mode)
        self.threadVideo.mode = mode


    @QtCore.pyqtSlot(np.ndarray)
    def update_game_buttons(self, GB):
        """Updates the images of game buttons"""
        color_map = {-1 : "red", 0 : "empty", 1 : "blue" }
        for i in reversed(range(self.gameLayout.count())): 
            btn = self.gameLayout.itemAt(i).widget()
            self.setGameButtonIcon(btn, color_map[ GB[btn.row, btn.col] ])


    @QtCore.pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.cameraImageLabel.setPixmap(qt_img)


    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)
    
if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    a = AppTicTacToe()
    a.show()
    sys.exit(app.exec())