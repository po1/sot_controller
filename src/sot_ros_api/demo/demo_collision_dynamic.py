'''
@author: Karsten Knese, Gennaro Raiola
'''
from sot_ros_api import *

from dynamic_graph.dynamic_graph_fcl import DynamicGraphFCL
from dynamic_graph.sot.core.meta_task_dynamic_velocity_damping import MetaTaskDynamicVelocityDamping
from dynamic_graph.sot.core.dyn_oppoint_modifier import DynamicOppointModifier

def followTrajectory():
	createRosExport('matrixHomoStamped',taskRW.featureDes.position,'/hand_pose_publisher/right_hand_ref_pose')
	createRosExport('matrixHomoStamped',taskLW.featureDes.position,'/hand_pose_publisher/left_hand_ref_pose')

def followMarker():
	createRosExport('vector3Stamped',taskGAZE.proj.point3D,'/aruco_single/position')

def followHand():
	createRosExport('vector3Stamped',taskGAZE.proj.point3D,'/hand_pose_publisher/head_ref_point')

def gotoMarker3D():
	createRosExport('matrixHomoStamped',taskRW.featureDes.position,'/aruco_single/transform')
	taskRW.feature.selec.value = 111

def gotoMarker6D():
	createRosExport('matrixHomoStamped',taskRW.featureDes.position,'/aruco_single/transform')
	taskRW.feature.selec.value = 111111

def speedUp(gainvalue):
	taskRW.task.controlGain.value = gainvalue
	taskLW.task.controlGain.value = gainvalue

def avoidMarker():
	createRosExport('matrixHomoStamped',taskDAMPstatic.task.p2_arm_right_tool,'/aruco_single/transform')

def basicStack():
	# Basic stack
	push(taskJL)
	solver.addContact(taskBASE)
    
dynTest = DynamicOppointModifier('bla')
staticOp = DynamicOppointModifier('static')
robot.dynamic.createOpPoint('arm_right_tool_joint','arm_right_tool_joint')
plug(robot.dynamic.arm_right_tool_joint, staticOp.positionIN)
plug(robot.dynamic.Jarm_right_tool_joint, staticOp.jacobianIN)
staticOp.transformationSig.value = (0,0,0)

taskDAMPstatic = MetaTaskDynamicVelocityDamping('velDampstatic', 0.1, 0.07)
taskDAMPstatic.task.set_avoiding_objects('arm_right_tool')
plug(robot.dynamic.arm_right_tool_joint, taskDAMPstatic.task.p1_arm_right_tool)
plug(robot.dynamic.Jarm_right_tool_joint, taskDAMPstatic.task.jVel_arm_right_tool)
collision_point = (0.2,-0.2,1.1)
p2_point = goalDef(collision_point)
taskDAMPstatic.task.p2_arm_right_tool.value = matrixToTuple(p2_point)


collision_objects = ['arm_right_3_joint', 'arm_right_7_joint', 'arm_right_5_joint','torso_1_joint','arm_left_3_joint', 'arm_left_7_joint', 'arm_left_5_joint']
entFCL = DynamicGraphFCL('entFCL')

# setup entity for FCL
collision_string = ''
for collision in collision_objects:
	collision_string += collision+str(':')
collision_string = collision_string[:-1]
print ('setting collision objects: '+str(collision_string))
entFCL.set_collision_joints(collision_string)

# plugging FK into FCL 
for collision in collision_objects:
        robot.dynamic.createOpPoint(collision, collision)
	robot.dynamic.signal(collision).recompute(0)
	plug(robot.dynamic.signal(collision), entFCL.signal(collision))

for i in range(len(collision_objects)):
	for j in range(len(collision_objects)):
		if not(collision_objects[i] == collision_objects[j]):
			signal_name = str(collision_objects[i])+str(collision_objects[j])
			entFCL.signal(signal_name).recompute(0)
'''
TORSO TEST
DYNOP FOR CLOSEST POINT CALUCLATION AND JACOBIAN TWIST
'''
# just for torso test!
#arm right
dynOP7right = DynamicOppointModifier('arm_right_7_joint')
plug(robot.dynamic.arm_right_7_joint, dynOP7right.positionIN)
plug(robot.dynamic.Jarm_right_7_joint, dynOP7right.jacobianIN)
plug(entFCL.oppoint_arm_right_7_jointtorso_1_joint, dynOP7right.transformationSig)

dynOP5right = DynamicOppointModifier('arm_right_5_joint')
plug(robot.dynamic.arm_right_5_joint, dynOP5right.positionIN)
plug(robot.dynamic.Jarm_right_5_joint, dynOP5right.jacobianIN)
plug(entFCL.oppoint_arm_right_5_jointtorso_1_joint, dynOP5right.transformationSig)

dynOP3right = DynamicOppointModifier('arm_right_3_joint')
plug(robot.dynamic.arm_right_3_joint, dynOP3right.positionIN)
plug(robot.dynamic.Jarm_right_3_joint, dynOP3right.jacobianIN)
plug(entFCL.oppoint_arm_right_3_jointtorso_1_joint, dynOP3right.transformationSig)

#arm left
dynOP7left = DynamicOppointModifier('arm_left_7_joint')
plug(robot.dynamic.arm_left_7_joint, dynOP7left.positionIN)
plug(robot.dynamic.Jarm_left_7_joint, dynOP7left.jacobianIN)
plug(entFCL.oppoint_arm_left_7_jointtorso_1_joint, dynOP7left.transformationSig)

dynOP5left = DynamicOppointModifier('arm_left_5_joint')
plug(robot.dynamic.arm_left_5_joint, dynOP5left.positionIN)
plug(robot.dynamic.Jarm_left_5_joint, dynOP5left.jacobianIN)
plug(entFCL.oppoint_arm_left_5_jointtorso_1_joint, dynOP5left.transformationSig)

dynOP3left = DynamicOppointModifier('arm_left_3_joint')
plug(robot.dynamic.arm_left_3_joint, dynOP3left.positionIN)
plug(robot.dynamic.Jarm_left_3_joint, dynOP3left.jacobianIN)
plug(entFCL.oppoint_arm_left_3_jointtorso_1_joint, dynOP3left.transformationSig)

'''
AVOIDANCE TASK
'''
taskDAMP = MetaTaskDynamicVelocityDamping('velDamp', 0.1, 0.07)
taskDAMP.task.set_avoiding_objects('arm_right_7_joint:arm_right_5_joint:arm_right_3_joint:arm_left_7_joint:arm_left_5_joint:arm_left_3_joint')
createRosImport('double', taskDAMP.task.ds, 'rviz_marker_closest_points/ds')
createRosImport('double', taskDAMP.task.di, 'rviz_marker_closest_points/di')
''' THIS HAS TO BE ENTFCL, otherwise the calculation won't get triggered!!!! IMPORTANT'''
''' question is why left arm is different in v compared to right
	
entFCL should return full pose of point, not just point with identity matrix!!

'''
#plug right arm
plug(entFCL.arm_right_7_jointtorso_1_joint, taskDAMP.task.p1_arm_right_7_joint)
plug(entFCL.torso_1_jointarm_right_7_joint, taskDAMP.task.p2_arm_right_7_joint)
plug(dynOP7right.jacobian, taskDAMP.task.jVel_arm_right_7_joint)
createRosImport('matrixHomo', entFCL.torso_1_jointarm_right_7_joint, 'rviz_marker_closest_points/avoid_torso_1_jointarm_right_7_joint')

plug(entFCL.arm_right_5_jointtorso_1_joint, taskDAMP.task.p1_arm_right_5_joint)
plug(entFCL.torso_1_jointarm_right_5_joint, taskDAMP.task.p2_arm_right_5_joint)
plug(dynOP5right.jacobian, taskDAMP.task.jVel_arm_right_5_joint)
createRosImport('matrixHomo', entFCL.torso_1_jointarm_right_5_joint, 'rviz_marker_closest_points/avoid_torso_1_jointarm_right_5_joint')

plug(entFCL.arm_right_3_jointtorso_1_joint, taskDAMP.task.p1_arm_right_3_joint)
plug(entFCL.torso_1_jointarm_right_3_joint, taskDAMP.task.p2_arm_right_3_joint)
plug(dynOP3right.jacobian, taskDAMP.task.jVel_arm_right_3_joint)
createRosImport('matrixHomo', entFCL.torso_1_jointarm_right_3_joint, 'rviz_marker_closest_points/avoid_torso_1_jointarm_right_3_joint')

#plug left arm
plug(entFCL.arm_left_7_jointtorso_1_joint, taskDAMP.task.p1_arm_left_7_joint)
plug(entFCL.torso_1_jointarm_left_7_joint, taskDAMP.task.p2_arm_left_7_joint)
plug(dynOP7left.jacobian, taskDAMP.task.jVel_arm_left_7_joint)
createRosImport('matrixHomo', entFCL.torso_1_jointarm_left_7_joint, 'rviz_marker_closest_points/avoid_torso_1_jointarm_left_7_joint')

plug(entFCL.arm_left_5_jointtorso_1_joint, taskDAMP.task.p1_arm_left_5_joint)
plug(entFCL.torso_1_jointarm_left_5_joint, taskDAMP.task.p2_arm_left_5_joint)
plug(dynOP5left.jacobian, taskDAMP.task.jVel_arm_left_5_joint)
createRosImport('matrixHomo', entFCL.torso_1_jointarm_left_5_joint, 'rviz_marker_closest_points/avoid_torso_1_jointarm_left_5_joint')

plug(entFCL.arm_left_3_jointtorso_1_joint, taskDAMP.task.p1_arm_left_3_joint)
plug(entFCL.torso_1_jointarm_left_3_joint, taskDAMP.task.p2_arm_left_3_joint)
plug(dynOP3left.jacobian, taskDAMP.task.jVel_arm_left_3_joint)
createRosImport('matrixHomo', entFCL.torso_1_jointarm_left_3_joint, 'rviz_marker_closest_points/avoid_torso_1_jointarm_left_3_joint')


# Create basic tasks
taskRW = createEqualityTask('rightWrist', 'arm_right_tool_joint')
taskLW = createEqualityTask('leftWrist', 'arm_left_tool_joint')
taskBASE = createEqualityTask('baseContact','base_joint',10)
taskJL = createJointLimitsTask(500)
safePos = safePosition()
diag = (0,0,0,0,0,0,1.36499,1.49997,0.677897,0.636507,0.170576,0.234007,0.120986,0.0156722,0.0213592,0.687228,0.63189,0.172151,0.260947,0.120986,0.0156722,0.0213592,0.511255,0.520094)
taskWEIGHTS = createWeightsTask(diag)
taskGAZE = createGazeTask('camera_joint')
taskGAZE.goto3D((100,0.0,1.48),10)

basicStack()
gotoNd(taskRW,(0.2,-0.4,1.1),'111111',5)
gotoNd(taskLW,(0.2,0.4,1.1),'111111',5)
