#!/usr/bin/env python3
import sys
import rospy
import moveit_commander
import geometry_msgs.msg
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive
import math

class ManipulatorPickAndPlace(object):
    def __init__(self, arm_group_name, gripper_group_name):
        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node('manipulator_pick_and_place', anonymous=True)

        self.robot = moveit_commander.RobotCommander()
        self.scene = moveit_commander.PlanningSceneInterface()
        self.move_group = moveit_commander.MoveGroupCommander(arm_group_name)
        self.gripper_group = moveit_commander.MoveGroupCommander(gripper_group_name)

    def go_to_pose_goal(self, angle1, angle2):
        joint_goal = self.move_group.get_current_joint_values()
        joint_goal[0] = 0
        joint_goal[1] = 0
        joint_goal[2] = angle1
        joint_goal[3] = 0
        joint_goal[4] = angle2
        joint_goal[5] = 0

        self.move_group.go(joint_goal, wait=True)
        self.move_group.stop()

    def open_gripper(self):
        gripper_joint_values = self.gripper_group.get_current_joint_values()
        gripper_joint_values[0] = 0.0  # Adjust these values based on your gripper's configuration
        gripper_joint_values[1] = 0.0  # Adjust these values
        self.gripper_group.go(gripper_joint_values, wait=True)
        self.gripper_group.stop()

    def close_gripper(self):
        gripper_joint_values = self.gripper_group.get_current_joint_values()
        gripper_joint_values[0] = 0.0178  # Adjust these values
        gripper_joint_values[1] = -0.0178  # Adjust these values
        self.gripper_group.go(gripper_joint_values, wait=True)
        self.gripper_group.stop()

    def addObject(self):
        table = CollisionObject()
        table.id = "table"
        table.header.frame_id = "world"
        table_primitive = SolidPrimitive()
        table_primitive.type = table_primitive.BOX
        table_primitive.dimensions = [0.15, 0.4, 0.4]  # dimensions of the table
        table_pose = geometry_msgs.msg.Pose()
        table_pose.position.x = 0.5
        table_pose.position.y = 0
        table_pose.position.z = 0.2
        table_pose.orientation.w = 1.0
        table.primitives = [table_primitive]
        table.primitive_poses = [table_pose]
        table.operation = table.ADD
        self.scene.add_object(table)

        # Add the second object (e.g., another cube)
        cube = CollisionObject()
        cube.id = "cube"
        cube.header.frame_id = "world"
        cube_primitive = SolidPrimitive()
        cube_primitive.type = cube_primitive.BOX
        cube_primitive.dimensions = [0.01, 0.01, 0.2]  # dimensions of the cube
        cube_pose = geometry_msgs.msg.Pose()
        cube_pose.position.x = 0.55  # Adjust the position as needed
        cube_pose.position.y = 0
        cube_pose.position.z = 0.5  # Place it above the table
        cube_pose.orientation.w = 1.0
        cube.primitives = [cube_primitive]
        cube.primitive_poses = [cube_pose]
        cube.operation = cube.ADD
        self.scene.add_object(cube)

    def attach_object(self, object_name, gripper_link):
        grasping_group = 'gripper'  # Name of the gripper group
        touch_links = self.robot.get_link_names(group=grasping_group)
        self.scene.attach_box(gripper_link, object_name, touch_links=touch_links)

def main():
    arm_group_name = "arm"  # Replace with your arm's group name
    gripper_group_name = "gripper"  # Replace with your gripper's group name
    manipulator = ManipulatorPickAndPlace(arm_group_name, gripper_group_name)
    manipulator.addObject()
    manipulator.open_gripper()
    manipulator.go_to_pose_goal((71 * math.pi)/180, (22 * math.pi)/180 )
    manipulator.close_gripper()
    manipulator.attach_object("cube","link6")
    #rospy.sleep(5)
    manipulator.go_to_pose_goal(0,0)
    

if __name__ == '__main__':
    main()