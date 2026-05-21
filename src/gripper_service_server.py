#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from std_srvs.srv import Trigger

class GripperServiceServer(Node):

    def __init__(self):
        super().__init__('gripper_service_server')

        # Declare the controller topic name parameter
        self.declare_parameter('controller_topic', '/lbr/robotiq_gripper_controller/commands')
        topic_name = self.get_parameter('controller_topic').value

        # Publisher to send position commands to the gripper controller
        self.command_pub = self.create_publisher(Float64MultiArray, topic_name, 10)

        # Define specific stroke thresholds (0.000m is open, 0.025m is fully closed)
        self.OPEN_POSITION = 0.020
        self.CLOSE_POSITION = 0.00

        # Create Services
        self.open_srv = self.create_service(Trigger, 'open_gripper', self.open_gripper_callback)
        self.close_srv = self.create_service(Trigger, 'close_gripper', self.close_gripper_callback)

        self.get_logger().info('Gripper Service Server initialized.')
        self.get_logger().info('Available services: /open_gripper and /close_gripper')

    def send_gripper_command(self, position_val):
        """Helper to build and publish the array message to both joints."""
        msg = Float64MultiArray()
        # Since you fixed your limits/axes configuration, both values are positive
        msg.data = [position_val, position_val]
        self.command_pub.publish(msg)

    def open_gripper_callback(self, request, response):
        self.get_logger().info('Received service request to OPEN the gripper.')
        try:
            self.send_gripper_command(self.OPEN_POSITION)
            response.success = True
            response.message = f"Successfully commanded gripper to open ({self.OPEN_POSITION}m)."
        except Exception as e:
            response.success = False
            response.message = f"Failed to command gripper: {str(e)}"
        return response

    def close_gripper_callback(self, request, response):
        self.get_logger().info('Received service request to CLOSE the gripper.')
        try:
            self.send_gripper_command(self.CLOSE_POSITION)
            response.success = True
            response.message = f"Successfully commanded gripper to close ({self.CLOSE_POSITION}m)."
        except Exception as e:
            response.success = False
            response.message = f"Failed to command gripper: {str(e)}"
        return response

def main(args=None):
    rclpy.init(args=args)
    node = GripperServiceServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()