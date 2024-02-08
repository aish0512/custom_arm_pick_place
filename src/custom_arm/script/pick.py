#!/usr/bin/env python3
import sys
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
import tf
from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive

class ManipulatorPickAndPlace(object):
    def __init__(self, arm_group_name, gripper_group_name):
        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node('manipulator_pick_and_place', anonymous=True)

        self.robot = moveit_commander.RobotCommander()
        self.scene = moveit_commander.PlanningSceneInterface()
        self.arm_group = moveit_commander.MoveGroupCommander(arm_group_name)
        self.gripper_group = moveit_commander.MoveGroupCommander(gripper_group_name)
        self.listener = tf.TransformListener()
    
    def open_gripper(self):
        # Set the gripper group to its "open" pose
        self.gripper_group.set_named_target("gripper_open")
        self.gripper_group.go(wait=True)

    def close_gripper(self):
        # Set the gripper group to its "closed" pose
        self.gripper_group.set_named_target("gripper_close")
        self.gripper_group.go(wait=True)

    def pick(self, pose):
        self.arm_group.set_planning_time(20.0)  # Set this to a higher value

        self.arm_group.set_pose_target(pose)
        # Add pick logic here, e.g., approach, grip, lift
        planning_output = self.arm_group.plan()
        # Check if planning was successful
        if len(planning_output) > 1 and planning_output[0]:
            plan = planning_output[1]  # Extract the plan
            print(plan)
            # Execute the plan
            #self.open_gripper()
            self.arm_group.execute(plan, wait=True)
            #self.close_gripper()
        else:
            rospy.logerr("Planning failed for the pick operation")

    def place(self, pose):
        # Add place logic here
        self.arm_group.set_pose_target(pose)
        plan = self.arm_group.plan()
        self.arm_group.execute(plan, wait=True)

    def get_object_pose(self, object_name):
        try:
            (trans, rot) = self.listener.lookupTransform('/link1', object_name, rospy.Time(0))
            object_pose = Pose()
            object_pose.position.x = trans[0]
            object_pose.position.y = trans[1]
            object_pose.position.z = trans[2]
            object_pose.orientation.x = rot[0]
            object_pose.orientation.y = rot[1]
            object_pose.orientation.z = rot[2]
            object_pose.orientation.w = rot[3]
            return object_pose
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            rospy.logerr("TF lookup failed")
            return None

def main():
    # Initialize the planning scene interface (interface to the world surrounding the robot)
    planning_scene_interface = moveit_commander.PlanningSceneInterface()
    
    # Define and add the cube to the planning scene
    cube = CollisionObject()
    cube.id = "my_cube"
    cube.header.frame_id = "world"
    primitive = SolidPrimitive()
    primitive.type = primitive.BOX
    primitive.dimensions = [0.03, 0.03, 0.05]  # Replace with your dimensions
    cube_pose = Pose()
    cube_pose.position.x = 0.1  # Replace with the cube's position
    cube_pose.position.y = 0.0
    cube_pose.position.z =0.0
    cube.primitives = [primitive]
    cube.primitive_poses = [cube_pose]
    cube.operation = cube.ADD
    planning_scene_interface.add_object(cube)

    arm_group_name = "arm"  # Replace with your arm's group name
    gripper_group_name = "gripper"  # Replace with your gripper's group name
    manipulator = ManipulatorPickAndPlace(arm_group_name, gripper_group_name)

    # Wait for TF to become available
    rospy.sleep(2)

    # Get the pose of the object
    object_name = "my_cube"  # Replace with the TF frame name of your object
    object_pose = manipulator.get_object_pose(object_name)
    

    if object_pose is not None:
        # Define the pose to place the object
        place_pose = Pose()
        place_pose.position.x = 1.0  # Specify the desired position
        place_pose.position.y = 0.0
        place_pose.position.z = 0.5
        place_pose.orientation.w = 1.0  # Assuming a neutral orientation
        #print(object_pose)
        manipulator.pick(object_pose)
        #manipulator.place(place_pose)

if __name__ == '__main__':
    main()
