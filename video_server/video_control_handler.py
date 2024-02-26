import threading
import requests
import rospy
import rospkg
import roslaunch
import subprocess
from std_msgs.msg import Int32
from std_srvs.srv import Trigger, TriggerResponse

# Replace the URL with the actual endpoint of your Flask server
url = "http://localhost:5001/control_robot"
processes = {}

# Make a GET request to the server
response = requests.get(url)

data_publisher = rospy.Publisher('/cam_mode', Int32, queue_size=10)

previous_cam_mode = None
def publish_data(video_mode):
    # Create a ROS Int32MultiArray message
    data_msg = Int32()
    
    data_msg.data = video_mode


    # Publish the message to the ROS topic
    data_publisher.publish(data_msg)

    #rospy.loginfo("Published data: %d, video_mode)

def kill_node(node_name):
    subprocess.call(["rosnode", "kill", node_name])
    

def prep_launch():
    kill_node('image_proc')
    kill_node('rgb_flask_server_node')
    kill_node('ir_flask_server_node')
    kill_node('depth_flask_server_node')

def run_launch_file(package, launch_file):
    #uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
    #roslaunch.configure_logging(uuid)
    
    
    #launch = roslaunch.parent.ROSLaunchParent(uuid, [launch_file])
    #launch.start()
    #launch.spin()
    subprocess.Popen(['roslaunch', package, launch_file])



def flask_data_callback(_):
    global previous_cam_mode

    response = requests.get(url)
    print("response received")

    if response.status_code == 200:
        # Parse and use the response data (assuming it's a list of three integers)
        received_data = response.json()
        print(received_data)

        # Assuming the response is a list of three integers
        if len(received_data) == 3 and all(isinstance(value, int) for value in received_data):
            throttle, twist, cam_mode = received_data
            print(cam_mode)
            print("all data points received")

            # Check if the value of the third integer has changed
            if cam_mode != previous_cam_mode:
                # Publish the data to the ROS topic
                print("cam mode switched")
                
                if(cam_mode == 0):
                    publish_data(cam_mode)
                    #prep_launch()

                    #package = 'video_server'
                    #launch_file = 'rgb_proc.launch'
                    
                    


                    #run_launch_file("rgb proc", package, launch_file)
                    #print("rgb_proc launch file executed")
                    #launch_file = 'rgb_stream.launch'
                    #run_launch_file(package, launch_file)
                    print("changed cam mode: "+str(cam_mode))


                elif(cam_mode == 1):
                    publish_data(cam_mode)
                    #prep_launch()

                    #package = 'video_server'
                    
                    #launch_file = 'ir_stream.launch'
                    #run_launch_file(package, launch_file)
                    print("changed cam mode: "+str(cam_mode))
                elif(cam_mode == 2):
                    publish_data(cam_mode)
                    #kill_node('rgb_flask_server_node')
                    #kill_node('ir_flask_server_node')
                    #kill_node('depth_flask_server_node')
                    #prep_launch()

                    #package = 'video_server'
                    
                    #launch_file = 'depth_stream.launch'
                    #run_launch_file(package, launch_file)
                    print("changed cam mode: "+str(cam_mode))
                else:
                    print("launched none womp womp")

                

                # Update the previous value of the third integer
                previous_cam_mode = cam_mode
        else:
            rospy.logwarn("Invalid response format")
    else:
        rospy.logerr("Failed to retrieve data. Status code: %d", response.status_code)
    

# Check if the request was successful (status code 200)
if __name__ == '__main__':
    rospy.init_node('video_control_handler', anonymous=True)
    publish_data(0)
    
    #flask_data_callback()
    print("called the cb")
    rospy.Timer(rospy.Duration(1.0), flask_data_callback)

    rospy.spin()