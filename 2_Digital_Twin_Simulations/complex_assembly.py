import mujoco
import mujoco.viewer
import time

factory_xml = """
<mujoco model="GulfCore_Precision_Assembly">
  <compiler angle="degree" coordinate="local"/>
  <option timestep="0.002" gravity="0 0 -9.81"/>
  <worldbody>
    <light pos="0 0 3" dir="0 0 -1" directional="true"/>
    <geom type="plane" size="2 2 0.1" rgba="0.9 0.9 0.9 1"/>
    <body name="car_chassis" pos="0 0 0.1">
      <geom type="box" size="0.2 0.2 0.05" rgba="0.3 0.3 0.3 1"/>
      <geom type="box" size="0.2 0.02 0.1" pos="0 0.22 0.05" rgba="0.3 0.3 0.3 1"/>
      <geom type="box" size="0.2 0.02 0.1" pos="0 -0.22 0.05" rgba="0.3 0.3 0.3 1"/>
      <geom type="box" size="0.02 0.2 0.1" pos="0.22 0 0.05" rgba="0.3 0.3 0.3 1"/>
      <geom type="box" size="0.02 0.2 0.1" pos="-0.22 0 0.05" rgba="0.3 0.3 0.3 1" name="left_wall"/>
    </body>
    <body name="assembly_robot" pos="-0.05 0 0.8">
      <joint name="robot_x" type="slide" axis="1 0 0" damping="50"/>
      <joint name="robot_z" type="slide" axis="0 0 1" damping="50"/>
      <geom type="cylinder" size="0.05 0.2" rgba="0.5 0.5 0.5 1"/>
      <body name="battery_pack" pos="0 0 -0.25">
        <geom type="box" size="0.18 0.18 0.1" rgba="0.2 0.8 0.2 1" mass="10.0"/>
        <site name="tactile_sensor_left" pos="-0.18 0 0" size="0.01" rgba="1 0 0 1"/>
      </body>
    </body>
  </worldbody>
  <sensor>
    <touch name="left_collision" site="tactile_sensor_left"/>
  </sensor>
  <actuator>
    <motor name="motor_x" joint="robot_x" gear="500"/>
    <motor name="motor_z" joint="robot_z" gear="500"/>
  </actuator>
</mujoco>
"""

GULFCORE_MEMORY = {
    "ROOT:INSERT | WEIGHT:CLEAR": [0.0, -100.0], 
    "ROOT:INSERT | WEIGHT:LEFT_WALL_HIT": [150.0, -50.0], 
}

model = mujoco.MjModel.from_xml_string(factory_xml)
data = mujoco.MjData(model)

print("[INFO] Initializing GulfCore Tactile Assembly Validation...")

with mujoco.viewer.launch_passive(model, data) as viewer:
    viewer.cam.distance = 2.0
    viewer.cam.elevation = -15
    viewer.cam.lookat[2] = 0.2
    
    while viewer.is_running():
        left_force = data.sensordata[0]
        weight_context = "WEIGHT:CLEAR"
        if left_force > 5.0:
            weight_context = "WEIGHT:LEFT_WALL_HIT"
            
        atom_key = f"ROOT:INSERT | {weight_context}"
        derived_action = GULFCORE_MEMORY[atom_key]

        data.ctrl[0] = derived_action[0]
        data.ctrl[1] = derived_action[1]

        mujoco.mj_step(model, data)
        viewer.sync()
        time.sleep(0.002)

        if data.qpos[1] < -0.6: 
            data.qpos[0] = -0.05
            data.qpos[1] = 0.0
            data.qvel[0] = 0.0
            data.qvel[1] = 0.0
