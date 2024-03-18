#!/usr/bin/env python

import rospy
from sensor_msgs.msg import PointCloud2
from sensor_msgs import point_cloud2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class PointCloudVisualizer:
    def __init__(self):
        rospy.init_node('point_cloud_visualizer', anonymous=True)
        self.bridge = CvBridge()
        self.image_pub = rospy.Publisher('/depth_top_down', Image, queue_size=10)
        rospy.Subscriber('/camera/depth/points', PointCloud2, self.point_cloud_callback)

    def point_cloud_callback(self, msg):
        # Convert point cloud to a 2D numpy array
        pc = point_cloud2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
        points = np.array(list(pc))

        # Transform to top-down view (assuming z is up)
        # You may need to adjust this transformation based on your specific needs
        top_down_points = points[:, [0, 2]]
        top_down_points[:, 1] *= -1

        top_down_points[:, 0] *= 1280 / 10  # Scale x-axis
        top_down_points[:, 1] *= 960 / 10

        top_down_points[:, 0] += 1280 / 2  # Center x-axis
        top_down_points[:, 1] += 960
        top_down_points[:, 1] = 960 - top_down_points[:, 1]

        # Create an image from the top-down points
        image = np.zeros((960, 1280, 3), dtype=np.uint8)  # Assuming 100x100 image size
        for point in top_down_points:
            x, y = int(point[0]), int(point[1])  # Scale and center the points
            if 0 <= x < 1280 and 0 <= y < 960:
                image[y, x] = (0, 255, 0)  # Set point in image to green
        image = cv2.flip(image, 0)

        # Convert image to ROS message and publish
        image_msg = self.bridge.cv2_to_imgmsg(image, "rgb8")
        self.image_pub.publish(image_msg)

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        visualizer = PointCloudVisualizer()
        visualizer.run()
    except rospy.ROSInterruptException:
        pass
