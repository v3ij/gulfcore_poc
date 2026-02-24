import mujoco
import mujoco.viewer
import time

factory_xml = """
<mujoco model="GulfCore_Conveyor_Validation">
  <compiler angle="degree" coordinate="local"/>
  <option timestep="0.005" gravity="0 0 -9.81"/>
  <asset>
    <material name="steel_mat" rgba="0.3 0.3 0.3 1"/>
    <material name="glass_mat" rgba="0.2 0.8 1.0 0.7"/>
    <material name="belt_mat" rgba="0.05 0.05 0.05 1"/>
    <material name="arm_mat" rgba="0.1 0.4 0.9 1"/>
  </asset>
  <worldbody>
    <light pos="0 0 3" dir="0 0 -1" directional="true"/>
    <geom type="plane" size="2 2 0.1" rgba="0.9 0.9 0.9 1"/>
    <body name="conveyor_belt" pos="0.45 0 0.05">
      <geom type="box" size="0.1 2.0 0.05" material="belt_mat"/>
    </body>
    <body name="steel_part" pos="0.45 1.5 0.11">
      <joint name="steel_track" type="slide" axis="0 -1 0"/>
      <geom type="box" size="0.05 0.05 0.05" material="steel_mat" mass="5.0"/>
    </body>
    <body name="glass_part" pos="0.45 3.0 0.11">
      <joint name="glass_track" type="slide" axis="0 -1 0"/>
      <geom type="box" size="0.05 0.05 0.05" material="glass_mat" mass="0.2"/>
    </body>
    <body name="base" pos="0 0 0.1">
      <geom type="cylinder" size="0.15 0.1" rgba="0.5 0.5 0.5 1"/>
      <body name="shoulder" pos="0 0 0.1">
        <joint name="shoulder_yaw" type="hinge" axis="0 0 1" range="-180 180" damping="20"/>
        <geom type="cylinder" size="0.05 0.3" pos="0 0 0.3" material="arm_mat"/>
        <body name="arm_reach" pos="0 0 0.6">
          <geom type="cylinder" size="0.04 0.25" pos="0.25 0 0" euler="0 90 0" material="arm_mat"/>
          <body name="gripper" pos="0.5 0 0">
            <joint name="gripper_close" type="slide" axis="1 0 0" range="-0.1 0.1" damping="5"/>
            <geom type="box" size="0.08 0.08 0.08" rgba="0.8 0.1 0.1 1" mass="0.5"/>
          </body>
        </body>
      </body>
    </body>
  </worldbody>
  <actuator>
    <position name="belt_motor_1" joint="steel_track" kp="1000"/>
    <position name="belt_motor_2" joint="glass_track" kp="1000"/>
    <position name="shoulder_motor" joint="shoulder_yaw" kp="300"/>
    <position name="gripper_motor" joint="gripper_close" kp="500"/>
  </actuator>
</mujoco>
"""

GULFCORE_MEMORY = {
    "IDLE": [45.0, 0.0],
    "STEEL_IN_ZONE": [0.0, 0.06],
    "GLASS_IN_ZONE": [0.0, 0.02],
}

model = mujoco.MjModel.from_xml_string(factory_xml)
data = mujoco.MjData(model)

print("[INFO] Initializing GulfCore Conveyor Validation Sequence...")

with mujoco.viewer.launch_passive(model, data) as viewer:
    viewer.cam.distance = 3.5
    viewer.cam.elevation = -30
    viewer.cam.lookat[0] = 0.3
    viewer.cam.lookat[1] = 0.3
    start_time = time.time()
    
    while viewer.is_running():
        current_time = time.time() - start_time
        conveyor_distance = current_time * 0.5
        data.ctrl[0] = conveyor_distance 
        data.ctrl[1] = conveyor_distance 

        steel_y = 1.5 - conveyor_distance
        glass_y = 3.0 - conveyor_distance

        weight_context = "IDLE"
        if -0.2 < steel_y < 0.2:
            weight_context = "STEEL_IN_ZONE"
        elif -0.2 < glass_y < 0.2:
            weight_context = "GLASS_IN_ZONE"

        derived_action = GULFCORE_MEMORY[weight_context]
        data.ctrl[2] = derived_action[0]
        data.ctrl[3] = derived_action[1]

        mujoco.mj_step(model, data)
        viewer.sync()
        time.sleep(0.005)
