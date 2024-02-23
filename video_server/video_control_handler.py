import requests
import rospy
from std_msgs.msg import Int32

# Replace the URL with the actual endpoint of your Flask server
url = "http://localhost:5001/control_robot"

# Make a GET request to the server
response = requests.get(url)
rospy.init_node('video_control_handler', anonymous=True)
data_publisher = rospy.Publisher('/cam_mode', Int32, queue_size=10)
previous_cam_mode = None
def publish_data(video_mode):
    # Create a ROS Int32MultiArray message
    data_msg = Int32()
    
    data_msg.data = video_mode


    # Publish the message to the ROS topic
    data_publisher.publish(data_msg)

    #rospy.loginfo("Published data: %d, video_mode)

def flask_data_callback(_):
    global previous_cam_mode

    response = requests.get(url)

    if response.status_code == 200:
        # Parse and use the response data (assuming it's a list of three integers)
        received_data = response.json()

        # Assuming the response is a list of three integers
        if len(received_data) == 3 and all(isinstance(value, int) for value in received_data):
            throttle, twist, cam_mode = received_data
            print(cam_mode)

            # Check if the value of the third integer has changed
            if cam_mode != previous_cam_mode:
                # Publish the data to the ROS topic
                
                publish_data(cam_mode)
                

                # Update the previous value of the third integer
                previous_cam_mode = cam_mode
        else:
            rospy.logwarn("Invalid response format")
    else:
        rospy.logerr("Failed to retrieve data. Status code: %d", response.status_code)


# Check if the request was successful (status code 200)
rospy.Timer(rospy.Duration(1.0), flask_data_callback)
rospy.spin()