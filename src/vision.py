import rospy

# ROS Image message
from sensor_msgs.msg import Image

# OpenCV2 for saving an image
import cv2 as cv
import numpy as np

# ROS Image message -> OpenCV2 image converter
from cv_bridge import CvBridge, CvBridgeError

from krti2023_pi.srv import Activate, ActivateResponse
from krti2023_pi.msg import DResult

# get range from qr/target/elp
from nav_msgs.msg import Odometry
from math import tan, radians
import random as rng
from copy import deepcopy
#   LIST OF Service TOPIC
#   - vision/activate/target
#   - vision/verbose
#
#   LIST OF Publisher TOPIC
#   - vision/result
#
#   LIST OF Subscriber TOPIC
#   - down_facing_camera/image_raw
#

# TODO:
# -   add a service to request qr and target dx dy in m based on lidar data and fov
#        https://jamboard.google.com/d/1Iu5qJZLyZbIiGC8b8oDcwbF_GfKyBcttvh0o2xGcWHI/viewer?f=6


# Instantiate VERBOSE variable globally for verbose mode



class Vision:
    """
    vision.py
    This Node is responsible for detecting target and publishing the DResult to the '/vision/target/result' topic.
    to activate target detection we should activate
    using service under '/vision/activate/target' topic.
    """

    
    target = False
    # front_img = np.array([None for _ in range(10)])
    down_img = np.array([None for _ in range(10)])
    alt= -99

    def __init__(self):
        # initialize node
        rospy.init_node("vision")
        # Instantiate CvBridge for converting ROS Image messages to OpenCV2
        self.bridge = CvBridge()
        self.which_target = 1
        self.last_time = rospy.Time.now()
        # get param from launchfile
        camera_index = rospy.get_param("/vision/camera_index")
        self.down_fov = {
            "x": rospy.get_param("/vision/down_fov_x"),
            "y": rospy.get_param("/vision/down_fov_y"),
        }
        self.target_lower_hsv = np.array(rospy.get_param("/vision/target_lower_hsv"))
        self.target_upper_hsv = np.array(rospy.get_param("/vision/target_upper_hsv"))
        
        self.target2_lower_hsv = np.array(rospy.get_param("/vision/target2_lower_hsv"))
        self.target2_upper_hsv = np.array(rospy.get_param("/vision/target2_upper_hsv"))

        self.sim = rospy.get_param("/vision/use_sim")
        self.sim_camera_topic = "/camera/down/image_raw"
        # setup VideoCapture 
        if not self.sim:
            self.down_cap = cv.VideoCapture(camera_index)
            # self.down_cap.set(cv.CAP_PROP_FRAME_WIDTH, 360)
            # self.down_cap.set(cv.CAP_PROP_FRAME_HEIGHT, 360)    
            self.down_cap.set(cv.CAP_PROP_FRAME_WIDTH, 720)
            self.down_cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)    
            rospy.Timer(rospy.Duration(0.1), self.read_camera)
            
        if self.sim:
            # subscribe to image_topic from sim
            self.img_sub = rospy.Subscriber(
                self.sim_camera_topic, Image, self.callback_img
            )

        self.pose_sub = rospy.Subscriber("/mavros/local_position/odom", Odometry, self.pose_cb)

        
        print("target lower hsv : {}".format(self.target_lower_hsv))
        print("target upper hsv : {}".format(self.target_upper_hsv))
        print("down fov : {}".format(self.down_fov))

        self.timestamp = rospy.Time.now()
        # to start subscribing to the image_topic and starting the QR code detection
        self.activate_target = rospy.Service(
            "vision/activate/target", Activate, self.activate_target
        )
        
        # PUBLISHER
        # create publisher for target detection result
        self.target_result_pub = rospy.Publisher(
            "/vision/target/result", DResult, queue_size=10
        )

        # publisher for processed image
        self.target_img_pub = rospy.Publisher(
            "/vision/target/image", Image, queue_size=10
        )

        self.down_pub = rospy.Publisher("/camera/down/image", Image, queue_size=10)

    def activate_target(self, data):
        """
        This function called when the service '/vision/activate/target' is called.
        It activates the target detection.
        """
        if data.data:
            # check if using sim
            
            # if using real robot
            self.target = True
            self.which_target = data.target
            
            rospy.loginfo("Target detect activated")

        else:
            rospy.loginfo("Target detect deactivated")
            self.img_sub.unregister()
            self.target = False
        
        return ActivateResponse(True)
    
    def read_camera(self, msg):
        _, self.down_img = self.down_cap.read()
        msg = self.bridge.cv2_to_imgmsg(self.down_img)
        self.down_pub.publish(msg)


    def callback_img(self, msg):
        """
        This function is called when the image_topic is published.
        It gets the image from the topic and convert from ROS Image msgs to OpenCV2 Image.
        """
        rospy.loginfo_throttle(0.1, "image_received")
        try:
            # Convert your ROS Image message to OpenCV2
            self.down_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")

        except CvBridgeError as e:
            print(Warning("Conversion failed: {}".format(e)))

    def pose_cb(self, msg: Odometry):
        """
        Gets the raw pose of the drone and processes it for use in control.

        Args:
                msg (nav_msgs/Odometry): Raw pose of the drone.
        """
        # save current alt
        self.alt = msg.pose.pose.position.z

    def detect_target(self):
        """
        This function is called when the target detection is activated.
        this function called from the main
        It detects the target from the image and publishes the result.
        It will publish to the /vision/target/result topic
        with msg type DResult
        """
        thres = 100
        # try:
        img = self.down_img
        img_copy = deepcopy(img)
        Fwidth = img.shape[1]
        Fheight = img.shape[0]
    # except:
    #     pass
    # else:
        FWcenter = Fwidth // 2
        FHcenter = Fheight // 2
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        if self.which_target == 1:
            mask = cv.inRange(hsv, self.target_lower_hsv, self.target_upper_hsv)
            rospy.logdebug(f"mask value {mask}")
        elif self.which_target == 2:
            mask = cv.inRange(hsv, self.target2_lower_hsv, self.target2_upper_hsv)
            rospy.logdebug(f"mask value {mask}")


        # FILTER
        # morph size for the filter
        MORPH_SIZE = 3
        # create kernel for filter
        element = cv.getStructuringElement(
            cv.MORPH_RECT, (2 * MORPH_SIZE, 2 * MORPH_SIZE), (MORPH_SIZE, MORPH_SIZE)
        )

        # morphological transformation:
        # https://www.youtube.com/watch?v=xSzsD4kXhRw
        # apply filter morphology opening to the image
        # erode and dilate to remove noise
        mask_opening = cv.morphologyEx(mask, cv.MORPH_OPEN, element, iterations=1)
        # apply filter morphology closing to the image
        # dilate and erode to fill holes
        mask_closing = cv.morphologyEx(
            mask_opening, cv.MORPH_CLOSE, element, iterations=2
        )

        # find contours in the masked and filtered image
        contours, hierarchy = cv.findContours(
            mask_closing, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
        )
        rospy.logdebug_throttle(0.2,f"countours : {len(contours)}")

        # isolate object from background

        res = cv.bitwise_and(img, img, mask=mask_closing)

        # find the biggest contour
        dtype = [("area",float),("boundrect",tuple),("dx",int),("dy",int)]
        data=[]
        # data = [(0,0,0,0)]
        # print("contours", contours)
        if len(contours) == 0:
            cv.putText(
                    img_copy,
                    "NO TARGET",
                    (10, 100),
                    cv.FONT_HERSHEY_DUPLEX,
                    2,
                    (0, 0, 255),
                    1,
                )
            cv.putText(
                    img_copy,
                    "DETECTED",
                    (10, 200),
                    cv.FONT_HERSHEY_DUPLEX,
                    2,
                    (0, 0, 255),
                    1,
                )
            fps = 1/ ( rospy.Time.now()-self.last_time).to_sec()
            self.last_time = rospy.Time.now()
            cv.putText(img_copy, f"{round(fps,2)}", (0, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
            msg = self.bridge.cv2_to_imgmsg(img_copy, "bgr8")
            self.target_img_pub.publish(msg)
            return
        for i, contour in enumerate(contours):
            # calculate area of the contours
            area = cv.contourArea(contour)
            rect = cv.boundingRect(contour)
            x, y, w, h = rect
            dx = int(w / 2 + x - FWcenter)
            dy = int(h / 2 + y - FHcenter)
            data.append((area,
                            rect,
                            dx,
                            dy))
        
        data = np.array(data, dtype=dtype)
        data = np.sort(data, order="area")
        remove = np.where(data["area"] < thres)
        # print(remove)
        data = np.delete(data, remove)
        # print("data : ", data)
        # rospy.loginfo_throttle(0.2,f"")
        if len(data) == 0:
            self.target_result_pub.publish(DResult(False, 0, 0, 0, 0))
            cv.putText(
                img_copy,
                "NO TARGET",
                (10, 100),
                cv.FONT_HERSHEY_PLAIN,
                3,
                (0, 0, 255),
                1,
            )
            fps = 1/(rospy.Time.now()-self.last_time ).to_sec()
            self.last_time = rospy.Time.now()
            cv.putText(img_copy, f"{round(fps,2)}", (   0, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
            msg = self.bridge.cv2_to_imgmsg(img_copy, "bgr8")
            self.target_img_pub.publish(msg)
            return
        
        if np.max(data["area"]) < thres :
            # if no target is detected, publish false
            self.target_result_pub.publish(DResult(False, 0, 0, 0, 0))
            cv.putText(
                img_copy,
                "NO TARGET",
                (10, 100),
                cv.FONT_HERSHEY_PLAIN,
                3,
                (0, 0, 255),
                1,
            )
            fps = 1/(rospy.Time.now()-self.last_time ).to_sec()
            self.last_time = rospy.Time.now()
            cv.putText(img_copy, f"{round(fps,2)}", (   0, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
            msg = self.bridge.cv2_to_imgmsg(img_copy, "bgr8")
            self.target_img_pub.publish(msg)
            return

        avgx = np.mean(data["dx"])
        stdx = np.std(data["dx"])
        avgy = np.mean(data["dy"])
        stdy = np.std(data["dy"])
        
        if len(data) > 1 or stdx != 0 or stdy != 0:
            thr = 1.2
            validx = []
            validy = []
            print("avgx ", avgx)
            print("stdx ", stdx)
            for i in range(len(data)):
                z_scorex = (data["dx"][i]-avgx)/stdx
                z_scorey = (data["dy"][i]-avgy)/stdy

                if abs(z_scorex) < thr:
                    validx.append(data["dx"][i])
                if abs(z_scorey) < thr:
                    validy.append(data["dy"][i])

            # calculate the difference in meters, currently not working as expected
            if len(validx) == 0 or len(validy) == 0:
                dx = int(np.mean(data["dx"]))
                dy = int(np.mean(data["dy"]))
            else:
                dx = int(np.mean(validx))
                dy = int(np.mean(validy))
                print(f"dx:{validx}, dy:{validy}")
                print(f"dx:{dx}, dy:{dy}")
        else:
            dx = int(np.mean(data["dx"]))
            dy = int(np.mean(data["dy"]))
            print(f"dx:{dx}, dy:{dy}")
        x_m, y_m = self.calculate_meter_from_pixel(dx, dy, Fwidth, Fheight)

        rospy.logdebug_throttle(0.2, f"dx:, {dx}, dy:, {dy}, x_m:, {x_m}, y_m:, {y_m}")
        self.target_result_pub.publish(DResult(True, dx, dy, x_m, y_m))

        color = (
            rng.randint(0, 256),
            rng.randint(0, 256),
            rng.randint(0, 256),
        )

        for i in range(len(contours)):
            cv.drawContours(img_copy, contours, i, (0, 0, 255), 2)
    
        dx = int(dx)
        dy = int(dy)

        cv.line(
            img_copy,
            (FWcenter, FHcenter),
            (FWcenter + dx, FHcenter + dy),
            color,
            3
        )

        cv.circle(img_copy, (FWcenter + dx, FHcenter), 3, (0, 255, 255), -1)
        cv.circle(img_copy, (FWcenter, FWcenter + dy), 3, (0, 255, 255), -1)
        cv.putText(
            img_copy,
            "dx:" + str(dx),
            (FWcenter + dx // 2, FHcenter + 10),
            cv.FONT_HERSHEY_PLAIN,
            1,
            (0, 100, 255),
            1
        )
        cv.putText(
            img_copy,
            "dy:" + str(dy),
            (FWcenter - 10, FHcenter + dy // 2),
            cv.FONT_HERSHEY_PLAIN,
            1,
            (0, 100, 255),
            1
        )
        # # draw horizontal line
        cv.line(
            img_copy,
            (0, FHcenter),
            (Fwidth, FHcenter),
            (0, 255, 0),
            2
        )
        cv.line(
            img_copy,
            (FWcenter, 0),
            (FWcenter, Fheight),
            (0, 255, 0),
            2
        )
        fps = 1/ (rospy.Time.now()-self.last_time).to_sec()
        self.last_time = rospy.Time.now()
        cv.putText(img_copy, f"{round(fps,2)}", (0, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
        try:
            # Convert opencv2 img to ros Image
            msg = self.bridge.cv2_to_imgmsg(img_copy, "bgr8")
        except CvBridgeError as e:
            print(Warning("Conversion failed: {}".format(e)))
        self.target_img_pub.publish(msg)
                

    def calculate_meter_from_pixel(self, dx, dy, Fw, Fh):
        """
        this function is used to calculate the position in meter we should move
        based on error in pixel, lidar, and the fov of the camera
        https://jamboard.google.com/d/1lls6bwxasvXhjlHUzlAPdn7H457EWCQQhZ9MEsxx3u0
        """
        
        if self.alt == -99:
            return 0, 0
        Rx = tan(radians(self.down_fov["x"] / 2)) * self.alt
        Ry = tan(radians(self.down_fov["y"] / 2)) * self.alt

        x = dx * Rx / (Fw / 2)
        y = dy * Ry / (Fh / 2)
        return float(x), float(y)


    def main(self):
        last = rospy.Time.now()
        r = rospy.Rate(10)
        while not rospy.is_shutdown():
            rospy.loginfo_throttle(1,"Vision Node Heartbeat")
            if self.target:
                rospy.loginfo_once(f"[Vision] Target-{self.which_target} Activate")
                self.detect_target()

            r.sleep()


if __name__ == "__main__":
    try:
        vision = Vision()
        vision.main()
    except rospy.ROSInterruptException:
        pass
