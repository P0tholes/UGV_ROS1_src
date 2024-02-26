#!/usr/bin/env python3


from flask import Flask, render_template, Response, request
import cv2
from numpy import int32
from cv_bridge import CvBridge
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import Header
import threading
from std_msgs.msg import Int32

app_kinect = Flask(__name__)
app_control_robot = Flask(__name__)
bridge = CvBridge()
imageModePath = '/camera/ir/image_rect'
cv_image = None


def kinect_image_callback(msg):
    global cv_image
    try:
        
        cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        
        
        
        

    except Exception as e:
        rospy.logerr("Error processing Kinect image: {}".format(str(e)))

image_subscriber = rospy.Subscriber(imageModePath, Image, kinect_image_callback)





def generate():
    while True:
        if cv_image is not None:
            _, jpeg = cv2.imencode('.jpg', cv_image)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            
@app_kinect.route('/')
def index():
    return render_template('index.html')

@app_kinect.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')    




def listener():
    global image_subscriber
    global imageModePath
    cv_image = None
    rospy.init_node('ir_flask_server_node')
    
    image_subscriber = rospy.Subscriber(imageModePath, Image, kinect_image_callback)
    
    print(imageModePath)
    
    app_kinect.run(host='0.0.0.0', port=5000, debug=True)
    rate = rospy.Rate(20)
    while not rospy.is_shutdown():
        rate.sleep()




if __name__ == '__main__':
    
    
    listener()
    
    #listener()
    print("running listener thread")