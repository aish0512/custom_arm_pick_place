#! /usr/bin/env python3
import rospy
import time
import tf
from gazebo_msgs.msg import ModelStates



class MultiTfBroadcast(object):

    def __init__(self, robot_name_list, loop_rate=5.0):
        self._robot_name_list = robot_name_list
        self._model_poses = {}
        self._rate = rospy.Rate(loop_rate)
        self._broad_caster_tf = tf.TransformBroadcaster()

        rospy.Subscriber("/gazebo/model_states", ModelStates, self.update_model_poses)
        time.sleep(1)  # Leave enough time to be sure Gazebo is ready
        rospy.loginfo("Ready..Starting to Publish TF data now...")

    def update_model_poses(self, data):
        for i, name in enumerate(data.name):
            if name in self._robot_name_list:
                self._model_poses[name] = data.pose[i]

    def handle_turtle_pose(self, pose_msg, robot_name, reference_frame_data="/link1"):

        self._broad_caster_tf.sendTransform((pose_msg.position.x, pose_msg.position.y, pose_msg.position.z),
                                            (pose_msg.orientation.x, pose_msg.orientation.y,
                                             pose_msg.orientation.z, pose_msg.orientation.w),
                                            rospy.Time.now(),
                                            robot_name,
                                            reference_frame_data)

    def start_loop(self):

        while not rospy.is_shutdown():
            for robot_name in self._robot_name_list:
                pose_now = self._model_poses.get(robot_name)
                if not pose_now:
                    robot_name_msg = "The " + \
                        str(robot_name) + \
                        "'s Pose is not yet available...Please try again later"
                    rospy.loginfo(robot_name_msg)
                else:
                    self.handle_turtle_pose(pose_now, robot_name)
            self._rate.sleep()


def main():

    rospy.init_node('publisher_of_tf_node', anonymous=True)
    multi_tf_broadcast_obj = MultiTfBroadcast(
        robot_name_list=["my_cube"])

    try:
        multi_tf_broadcast_obj.start_loop()
    except rospy.ROSInterruptException:
        pass


if __name__ == '__main__':
    main()