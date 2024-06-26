from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.utils.visualizer import ColorMode, Visualizer
from detectron2 import model_zoo
import matplotlib.pyplot as plt

import cv2
import numpy as np
from collections import defaultdict

class Detector:
    def __init__(self, model_type="OD"):
        self.cfg = get_cfg()
        self.model_type = model_type

        # Load model config and pretrained model
        if model_type == "OD":
            self.cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
            self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml")
        elif model_type == "IS":
            self.cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
            self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
        elif model_type == "LVIS":
            self.cfg.merge_from_file(model_zoo.get_config_file("LVISv0.5-InstanceSegmentation/mask_rcnn_X_101_32x8d_FPN_1x.yaml"))
            self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("LVISv0.5-InstanceSegmentation/mask_rcnn_X_101_32x8d_FPN_1x.yaml")
        elif model_type == "PS":
            self.cfg.merge_from_file(model_zoo.get_config_file("COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml"))
            self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml")
        
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7
        self.cfg.MODEL.DEVICE = "cpu" #cpu or cuda

        self.predictor = DefaultPredictor(self.cfg)
        
        self.objects_detected = defaultdict(int)

    def onImage(self, imagePath):
        image = cv2.imread(imagePath)

        if self.model_type != "PS":
            predictions = self.predictor(image)
            instances = predictions['instances']
            classes = instances.pred_classes.cpu().numpy()
            class_names = MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]).thing_classes
            counts = defaultdict(int)

            for c in classes:
                class_name = class_names[c]
                counts[class_name] += 1

            self.objects_detected = counts
            print(self.objects_detected)

            viz = Visualizer(image[:,:,::-1], metadata=MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]), instance_mode=ColorMode.IMAGE)
            output = viz.draw_instance_predictions(predictions['instances'].to('cpu'))
        else:
            predictions, segmentInfo = self.predictor(image)['panoptic_seg']
            self.objects_detected = predictions
            viz = Visualizer(image[:,:,::-1], MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]))
            output = viz.draw_panoptic_seg_predictions(predictions.to('cpu'), segmentInfo)

        #cv2.imshow("Result", output.get_image()[:,:,::-1])
        #cv2.waitKey(0)


    def onCamera(self, cameraIndex=0, width=640, height=480):
        cap = cv2.VideoCapture(cameraIndex)
        
        cap.set(3, int(width))
        cap.set(4, int(height))

        if(cap.isOpened() == False):
            print("Error opening the video file...")
            return
        
        (success, image) = cap.read()

        while success:
            if self.model_type != "PS":
                predictions = self.predictor(image)
                instances = predictions['instances']
                classes = instances.pred_classes.cpu().numpy()
                class_names = MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]).thing_classes
                counts = defaultdict(int)

                for c in classes:
                    class_name = class_names[c]
                    counts[class_name] += 1

                self.objects_detected = counts

                viz = Visualizer(image[:,:,::-1], metadata=MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]), instance_mode=ColorMode.IMAGE)
                output = viz.draw_instance_predictions(predictions['instances'].to('cpu'))
            else:
                predictions, segmentInfo = self.predictor(image)['panoptic_seg']
                print(predictions)
                viz = Visualizer(image[:,:,::-1], MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]))
                output = viz.draw_panoptic_seg_predictions(predictions.to('cpu'), segmentInfo)
            
            cv2.imshow("Result", output.get_image()[:,:,::-1])

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

            (success, image) = cap.read()

    def getObjectsDetected(self):
        return self.objects_detected
