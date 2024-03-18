#!/usr/bin/env python3


from flask import Flask, render_template, Response, request
import cv2
from numpy import int32
from cv_bridge import CvBridge
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import Header
import threading
from std_msgs.msg import Int32, Float64

app_kinect = Flask(__name__)
app_control_robot = Flask(__name__)
bridge = CvBridge()
imageModePath = '/camera/rgb/image_color'
selected_topic = '/camera/rgb/image_color'
image_subscriber = None
cv_image = None
tilt_angle = 0.0

def tilt_angle_callback(msg):
    global tilt_angle
    angle = msg.data
    #rospy.loginfo("Current tilt angle: %.2f radians" % angle)
    tilt_angle = angle

def calculate_horizon_from_tilt(tilt_angle):
    angle_to_px_ratio = 9.877
    return (-tilt_angle + 24.3)*angle_to_px_ratio




def kinect_image_callback(msg):
    global cv_image
    global tilt_angle
    
    try:
        
        horizon_level = calculate_horizon_from_tilt(tilt_angle)
        cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        cv_image = cv2.rectangle(cv_image.copy(), (300,220), (340,260),(0,255,0),3)
        #cv_image = cv2.line(cv_image.copy(), (60,int(horizon_level)), (280,int(horizon_level)),(0,255,0),3)
        
        
        

    except Exception as e:
        rospy.logerr("Error processing Kinect image: {}".format(str(e)))







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

def integer_callback(msg):
    global selected_topic
    global image_subscriber
    topics = ['/camera/rgb/image_color', '/camera/ir/image_raw', '/depth_top_down']
    new_topic = topics[msg.data]
    if new_topic != selected_topic:
        rospy.loginfo(f"Switching from topic {selected_topic} to topic {new_topic}")
    selected_topic = new_topic
    if image_subscriber is not None:
        image_subscriber.unregister()

    
    image_subscriber = rospy.Subscriber(selected_topic, Image, kinect_image_callback)
  




def listener():
    global selected_topic
    selected_topic = '/camera/rgb/image_color'
    
    rospy.init_node('flask_video_node')
    rospy.Subscriber('/cam_mode', Int32, integer_callback)
    #rospy.Subscriber('/cur_tilt_angle', Float64, tilt_angle_callback)
    
    
    
    print(selected_topic)
    
    app_kinect.run(host='0.0.0.0', port=5000, debug=True)
    #rate = rospy.Rate(60)
    #while not rospy.is_shutdown():
        #rate.sleep()




if __name__ == '__main__':
    
    
    listener()
    
    #listener()
    print("running listener thread")
