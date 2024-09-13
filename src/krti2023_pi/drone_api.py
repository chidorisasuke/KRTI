from math import *
import rospy
from std_msgs.msg import Float64
from geometry_msgs.msg import PoseStamped, Point, Quaternion, Twist, TwistStamped, Vector3
from nav_msgs.msg import Odometry
from geographic_msgs.msg import GeoPointStamped, GeoPoseStamped, GeoPoint
from mavros_msgs.msg import State, Thrust, OverrideRCIn, GlobalPositionTarget, WaypointReached, WaypointList
from mavros_msgs.srv import SetMode, SetModeRequest
from mavros_msgs.srv import CommandLong, CommandLongRequest
from mavros_msgs.srv import ParamSet, ParamSetRequest
from mavros_msgs.srv import ParamGet, ParamGetRequest
from mavros_msgs.srv import CommandBool, CommandBoolRequest
from mavros_msgs.srv import CommandTOL, CommandTOLRequest
from mavros_msgs.srv import StreamRate, StreamRateRequest
from sensor_msgs.msg import LaserScan, Imu, NavSatFix, Range
from serial import Serial

from pygeodesy.geoids import GeoidPGM
import numpy as np

_egm96 = GeoidPGM('/usr/share/GeographicLib/geoids/egm96-5.pgm', kind=-3)

def geoid_height(lat, lon):
    """Calculates AMSL to ellipsoid conversion offset.
    Uses EGM96 data with 5' grid and cubic interpolation.
    The value returned can help you convert from meters 
    above mean sea level (AMSL) to meters above
    the WGS84 ellipsoid.
    If you want to go from AMSL to ellipsoid height, add the value.
    To go from ellipsoid height to AMSL, subtract this value.
    """
    return _egm96.height(lat, lon)
# IF USING RASPI
# import board
# import busio
# import adafruit_vl53l0x as vl53l0x

# IF USING KHADAS
# https://github.com/pimoroni/vl53l1x-python
# import VL53L1X as VL53
# import VL53L0X as VL53

DEBUG_PERIODE = 1
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

# WIP
class PID:
    def __init__(self, kp, ki=0, kd=0, dt=0, max_error=2, name=""):
        self.name = name
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.error = 0
        self.error_sum = 0
        self.error_diff = 0
        self.last_error = 0
        self.max_error = max_error

    
    def update(self, error)->float:
        self.error = error
        self.error_sum += error
        self.error_diff = error - self.last_error
        self.last_error = error
        if(self.max_error != 0):
            self.error_sum = clamp(self.error_sum, -self.max_error, self.max_error)
        pid_val = self.kp * self.error + self.ki * self.error_sum + self.kd * self.error_diff
        pid_val = clamp(pid_val, -2, 2)
        # rospy.logdebug("PID {}: error: {}, error_sum: {}, pid_val: {}".format(self.name, self.error, self.error_sum, pid_val))
        return pid_val
    
    def reset(self):
        self.error = 0
        self.error_sum = 0
        self.error_diff = 0
        self.last_error = 0

class DroneAPI:
    """
    Control Functions
    This module is designed to make high level control programming simple.
    """

    """
        TODO:
            1. Emergency cancel (stop all movement) if LIDAR detects an obstacle
               within 1 meter (http://wiki.ros.org/mavros#mavros.2FPlugins.local_position)

    """
    
    def __init__(
        self,
        waypoints: list = [],
        global_position: dict = {
            "latitude": -7.265572783693384,
            "longitude": 112.78452265474213,
            "altitude": 1,
        },
        parameters: dict = {},
        sim:bool = True,

    ) -> None:
        """
        Initialize the drone API

        Args:
            waypoints (list): list of waypoints
            global_position (dict): global position
            parameters (dict): parameters to set
        """
        self.sim = sim
        # Set waypoints
        self.current_waypoint = 0
        self.follow_waypoint = True
        self.waypoints = waypoints
        self.gps = NavSatFix()
        global_pos = rospy.Subscriber("/mavros/global_position/global", NavSatFix, self.gps_cb)
        rospy.sleep(3)
        
        # Set state
        state_sub = rospy.Subscriber("/mavros/state", State, self.state_cb)
        self.current_state = State()

        # mission in auto mode related
        wp_reached_sub = rospy.Subscriber("/mavros/mission/reached", WaypointReached, self.mission_wp_reached_cb)
        self.wp_reached = WaypointReached()
            
        # Wait for connection
        self.wait4connect()

        # Set origin
        # we need to sleep for a while otherwise
        # '0' will be stored in 'now'
        # so the loop will stop immediately
        rospy.sleep(0.2)
        if self.gps.status != -1:
            rospy.loginfo(f"current global position lat: {self.gps.latitude}, lon: {self.gps.longitude}")
        else:
            now = rospy.Time.now()
            while rospy.Time.now() - now < rospy.Duration(1.0):
                rospy.logdebug_throttle(0.2,"set origin")
                self.set_origin(global_position)

        # Set parameters
        for name, value in parameters.items():
            self.set_parameter(name, value)
        
        # Set current pose
        self.imu_heading = -1
        self.current_pose = Odometry()
        self.current_heading = 0.0
        self.local_desired_heading = 0.0
        self.home_heading = -1.0
        self.home_compass = -1.0
        pose_sub = rospy.Subscriber(
            "/mavros/local_position/odom",
            Odometry,
            self.pose_cb,
        )

        self.compass = Float64().data
        compass_sub = rospy.Subscriber(
            "/mavros/global_position/compass_hdg",
            Float64,
            self.compass_cb,
        )

        # set Velocity
        self.current_velocity = TwistStamped()
        velocity_sub = rospy.Subscriber("/mavros/local_position/velocity", TwistStamped, self.velocity_cb)

        # set IMU
        imu_sub = rospy.Subscriber('/mavros/imu/data/', Imu, self.imu_cb)
        self.imu = Imu()

        # LIDAR data
        self.lidar_queue = []
        self.lidar_data = LaserScan()
        # if self.sim:
        #     lidar_sub = rospy.Subscriber("/sensors/lidar/sim", LaserScan, self.lidar_cb)
        # else:
        #     self.setup_lidar()


        rospy.Timer(rospy.Duration(0.05), self.lidar_pub)
        
        # ultrasonic 
        # self.ultrasonic = float()
        # self.ser = Serial('/dev/ttyS0', baudrate=115200) 
        # rospy.Timer(rospy.Duration(0.1), self.ultrasonic_cb)

        self.previous_pose = Odometry()

        self.yaw_pid = PID(0.1,0,0.01,0, max_error=0.5)

        # rangefinder reading from pixhawk
        self.rangefinder = Range()
        rangefinder_sub = rospy.Subscriber("/mavros/rangefinder/rangefinder", Range, self.rangefinder_cb)
        
        # Print success
        rospy.loginfo("Initialization completed.")
        
    def set_home(self):
        self.home_gps = self.gps
        self.home_compass = self.compass
        self.home_heading = self.current_heading

    def gps_cb(self, data: NavSatFix):
        self.gps = data
        
    
    def ultrasonic_cb(self, msg: float):
        try:
            self.ultrasonic = self.ser.readline().decode('utf-8').split('\n')[0]
            rospy.loginfo(self.ultrasonic)
        except:
            self.ultrasonic = -1

    def move_vel(self, velx = 0, vely = 0, velz = 0, heading :float = None):
        
        cur_pose = self.current_pose
        # Get client
        client = rospy.Publisher(
            "/mavros/setpoint_velocity/cmd_vel_unstamped",
            Twist,
            queue_size=10,
        )
        # rospy.loginfo_throttle(0.3,f"position : {self.current_pose}")
        # rospy.loginfo_throttle(0.3,f"heading : {self.current_heading}")
        
        # If have heading then we set the heading
        if heading is None:
            heading = self.home_heading

        # Set position
        request = Twist()
        request.linear = Vector3(velx,vely,velz)    
        self.local_desired_heading = heading
        rospy.loginfo(f"Move with velocity:\n{request.linear}")
        print(heading)
        print(self.current_heading)
        err_head = heading - self.current_heading

        # if err_head > 180:
        #     err_head -= 360
        # elif err_head < -180:
        #     err_head += 360
        
        # val = self.yaw_pid.update(-err_head)
        val = 0
        request.angular.z = val

        # Send request
        # rospy.logdebug("publishing setpoint_velocity/cmd_vel_unstamped", logger_name="move_vel")
        client.publish(request)
        # rospy.loginfo_throttle_identical(0.1,
        #     f"cmd_vel to x: {velx}; y: {vely}; z: {velz}, yaw: {val}"
        # )
    
    def imu_cb(self, msg:Imu):
        """
        A function for IMU's subscriber callback
        Will set self.imu to the message received
        used in detecting stable motion
        """
        self.imu = msg

    def rangefinder_cb(self, msg: Range):
        self.rangefinder = msg.range
        # rospy.loginfo_throttle(0.3, f"rangefinder : {self.rangefinder}")

    def compass_cb(self, msg: Float64):
        """
        A function for Compass's subscriber callback
        Will set self.ompass to the message received
        used in detecting stable motion
        """
        self.compass = msg.data   
    def lidar_cb(self, data: LaserScan):
        """
        A function for receiving Lidar data from sensors node
        [ 1 2 3 4] consist of 4 range [front, left, back, right] sequentially
        needed for obstacle avoidance
        """
        self.lidar_data = data.ranges
    
    def lidar_pub(self, data):
        """
        A function for publishing Lidar data
        """
        data = LaserScan()
        
        if not self.sim:
            range = self.tof.get_distance()
            self.lidar_queue.append(range)
            
            if len(self.lidar_queue) > 1:
                self.lidar_queue.pop(0)
            
            data.ranges.append(sum(self.lidar_queue) / len(self.lidar_queue))
            self.lidar_data = data

        else:
            data.ranges = self.lidar_data
    
    def state_cb(self, msg):
        """
        A function for state's subscriber callback
        Will set self.current_state to the message received
        """
        self.current_state = msg
    
    def velocity_cb(self, msg:TwistStamped):
        """
        A function for velocity's subscriber callback
        
        """
        self.current_velocity = msg

    def pose_cb(self, msg: Odometry):
        """
        Gets the raw pose of the drone and processes it for use in control.

        Args:
                msg (nav_msgs/Odometry): Raw pose of the drone.
        """
        # Set current pose
        self.current_pose = msg

        # Calculate heading from quarternion to degrees
        q0, q1, q2, q3 = (
            msg.pose.pose.orientation.w,
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
        )

        psi = atan2((2 * (q0 * q3 + q1 * q2)), (1 - 2 * (pow(q2, 2) + pow(q3, 2))))
        # rospy.logdebug_throttle(0.3, "hdg = " + str(degrees(psi)))
        # rospy.logdebug_throttle(0.3, f"hdg = {self.imu_heading}")

        # Set current heading
        self.imu_heading = degrees(psi)
        self.current_heading = self.imu_heading

        # Set home heading
        if self.home_heading == -1.0:
            self.home_compass = self.compass
            self.home_heading = self.current_heading
            self.local_desired_heading = self.home_heading
            # print("home heading : ", self.home_heading)

    def set_origin(self, origin: dict):
        """
        A function to set origin to custom coordinates
        We need to set this if we're flying without GPS

        Args:
            origin (dict): origin coordinates
                - latitude
                - longitude
                - altitude

        Refer to https://discuss.ardupilot.org/t/guided-mode-with-optical-flow-without-gps-in-simulation/53494/6
        """

        # Get client
        setter = rospy.Publisher(
            "/mavros/global_position/set_gp_origin", GeoPointStamped, queue_size=10
        )

        # Set position
        position = GeoPointStamped()
        position.header.frame_id = "global"
        position.header.stamp = rospy.Time.now()
        position.position.latitude = origin["latitude"]
        position.position.longitude = origin["longitude"]
        position.position.altitude = origin["altitude"]

        setter.publish(position)
    
    def set_rc_override(self, values: dict = {}):
        client = rospy.Publisher("mavros/rc/override", OverrideRCIn, queue_size=10)
        ch = OverrideRCIn()
        if len(values) != 0:
            for i in values:
                ch.channels[i-1] = values[i]
        rospy.logdebug_throttle(0.2, f"ch override {ch}")
        client.publish(ch)
        


    def get_home_heading(self):
        return self.home_compass

    def get_parameter(self, name: str):
        """
        A function to get parameters

        Args:
            name (str): name of parameter
            value (float): value of parameter
        """

        # Get client
        client = rospy.ServiceProxy("/mavros/param/get", ParamGet)

        # get parameter
        request = ParamGetRequest()
        request.param_id = name

        # Send request
        response = ParamGet()
        response = client(request)
        return response.value

    def stable_motion(self):
        z = self.imu.linear_acceleration.z
        if(z > 9.68 and z < 9.9):
            return True
        return False
    
    def set_parameter(self, name: str, value: float):
        """
        A function to set parameters

        Args:
            name (str): name of parameter
            value (float): value of parameter
        """

        # Get client
        client = rospy.ServiceProxy("/mavros/param/set", ParamSet)

        # Set parameter
        request = ParamSetRequest()
        request.param_id = name
        request.value.real = value

        # Send request
        client(request)
    
    def use_gps(self,use:bool = True):
        self.set_parameter("AHRS_GPS_USE",1 if use else 0)
    
    def set_stream_rate(self, rate: int = 10):
        client = rospy.ServiceProxy("/mavros/set_stream_rate", StreamRate)
        request = StreamRateRequest(0, 100, 1)
        # request.message_rate = rate
        # request.on_off = 1
        # request.stream_id = 0
        
        client(request)

    def set_mode(self, mode: str = "GUIDED"):
        """
        A function to set mode

        Args:
            mode (str): mode to set. Default to GUIDED
        """

        # Get client
        rospy.wait_for_service("/mavros/set_mode")
        client = rospy.ServiceProxy("/mavros/set_mode", SetMode)

        # Set mode
        client(SetModeRequest(0, mode))

        # Check if mode is set
        if self.current_state.mode == mode:
            # Print success message
            rospy.loginfo(f"Mode is set to {mode}")
        else:
            # Print failed message
            rospy.loginfo(f"Failed to set mode to {mode}")
            rospy.loginfo(f"Current mode is {self.current_state.mode}")

    def set_thrust(self, thrust: float):
        """
        A function to set thrust

        Args:
            thrust (float): thrust to set. Value should be between 0 and 1
        """

        # Check if thrust is not in range
        if thrust < 0 or thrust > 1:
            print("Illegal thrust value. It should be between 0 and 1 (inclusive).")
            return

        # Get client
        client = rospy.Publisher(
            "/mavros/setpoint_attitude/thrust", Thrust, queue_size=10
        )

        # Create thrust message
        request = Thrust()
        request.header.stamp = rospy.Time.now()
        request.thrust = thrust

        # Set thrust
        client.publish(request)

    def arm(self, status: bool = True):
        """
        A function to arm or disarm the drone

        Args:
            status (bool): True to arm, False to disarm
        """

        # Get client
        rospy.wait_for_service("/mavros/cmd/arming")
        arming_client = rospy.ServiceProxy("/mavros/cmd/arming", CommandBool)
        
        # Arm
        while not rospy.is_shutdown() and not self.current_state.armed:
            arming_client(CommandBoolRequest(status))
        else:
            if status == True:
                rospy.loginfo("Drone is armed and ready to fly")
            else:
                rospy.loginfo("Drone is disarmed")

    def  takeoff(self, altitude: float = 3.0):
        """
        A function to give drone a takeoff command

        Args:
            altitude (float): altitude to takeoff to
        """

        rospy.loginfo("drone current altitude = " + str(self.current_pose.pose.pose.position.z))
        # Arm drone
        self.arm()
        print(f"current altitude = {self.current_pose.pose.pose.position.z}")

        if self.current_pose.pose.pose.position.z > altitude * 0.95 - 0.2:
            rospy.loginfo("altitude already reached")
            return 1
        
        if self.current_pose.pose.pose.position.z > 0.45:
            rospy.loginfo("drone already in air")
            return 1
        
        # Get client
        rospy.wait_for_service("/mavros/cmd/takeoff")
        takeoff_client = rospy.ServiceProxy("/mavros/cmd/takeoff", CommandTOL)

        # Takeoff
        rospy.loginfo("Taking off ...")
        response = takeoff_client(CommandTOLRequest(0, 0, 0, 0, altitude))
        rospy.sleep(3)

        if response.success:
            rospy.loginfo("Taking off ...")

            # We will return if we are 95% of the way to the target altitude
            while self.current_pose.pose.pose.position.z < altitude * 0.95 - 0.2:
                rospy.loginfo_throttle(0.1,f"current altitude = {self.current_pose.pose.pose.position.z}")

                rospy.sleep(0.1)

            return 1
        
        rospy.logerr("Takeoff failed")
        return 0
        

    def land(self):
        """
        A function to give drone a land command
        """

        # Get client
        rospy.wait_for_service("/mavros/cmd/land")
        client = rospy.ServiceProxy("/mavros/cmd/land", CommandTOL)

        # Landing
        client(CommandTOLRequest(0, 0, 0, 0, 0))

        # Print success message
        rospy.loginfo(
            "Landing command sent. Drone should be disarming itself in 10-15 seconds after it touches the ground. ..."
        )

    def stop(self):
        rospy.loginfo("Stopping")
        home_heading = radians(self.get_home_heading())

        x,y,z = self.body2local(0, 0, 0, home_heading)
        dist = {"x": x, "y": y, "z": z, "heading": home_heading}

        # Move command        
        for _ in range(30):
            self.move(dist)
            rospy.sleep(0.1)

        rospy.loginfo("Stop command sent, aircraft should be stopped in a moment")

    def body2local(self, x, y, heading):
        return x * cos(heading) - y * sin(heading), x * sin(heading) + y * cos(heading)
    
    def move(self, destination: dict = None):
        """
            IMPORTANT NOTES:
        - in simulation we need to send the msg  multiple times to make it work
        - in real drone we shouldn't send the msg multiple times
        - ONLY USE MAV_FRAME "LOCAL_NED".

        A function to move the drone to certain position

        Args:
            destination (dict | None): destination coordinates
                - x
                - y
                - z
                - heading (optional, if not passed then it will use the current heading)
            wait_reached: wait until the drone reached the setpoint
                If no destination passed then drone will go to
                current destination in the waypoint list
        """
        rospy.loginfo(f"testing home heading on move method : {self.home_heading}")
        self.previous_pose = self.current_pose
        ref_pose = self.current_pose.pose.pose.position
        # Get client
        client = rospy.Publisher(
            "/mavros/setpoint_position/local",
            PoseStamped,
            queue_size=10,
        )
        rospy.loginfo_throttle(0.2,f"position : {self.current_pose} ")
        rospy.loginfo_throttle(0.2,f"heading : {self.current_heading} ")
        # If no destination is given, use current destination
        # indicated by current waypoint index
        if destination == None:
            destination = self.waypoints[self.current_waypoint]

        # If have heading then we set the heading
        if "heading" in destination:
            heading = destination["heading"]
        else:
            heading = self.home_heading

        # Set position
        request = PoseStamped()
        request.header.stamp = rospy.Time.now()
        request.pose.position = Point(
            x=destination["x"], y=destination["y"], z=destination["z"]
        )

        request.pose.orientation = self.calculate_heading(heading)
        # self.local_desired_heading = heading

        # # === khusus BODY_NED ===
        # cur_waypoint = destination
        # cur_waypoint['x'] += ref_pose.x
        # cur_waypoint['y'] += ref_pose.y
        # cur_waypoint['z'] += ref_pose.z
        # cur_waypoint['heading'] = self.home_heading
        # # === end of khusus BODY_NED ===


        # Send request
        rospy.logdebug("publishing setpoint_position/local", logger_name="move")
        client.publish(request)
        rospy.loginfo(
            f"Moving to x: {destination['x']}; y: {destination['y']}; z: {destination['z']}"
        )

    def move_global_raw(self, coordinate: GeoPoint, heading = None):
        """
            IMPORTANT NOTES:
        - in simulation we need to send the msg  multiple times to make it work
        - in real drone we shouldn't send the msg multiple times but sometimes we need to

        A function to move the drone to certain position in global frame

        """

        # Get client
        client = rospy.Publisher(
            "/mavros/setpoint_raw/global",
            GlobalPositionTarget,
            queue_size=10,
        )

        # http://docs.ros.org/en/api/mavros_msgs/html/msg/GlobalPositionTarget.html
        request = GlobalPositionTarget()
        request.header.stamp = rospy.Time.now()

        request.coordinate_frame = 3
        request.latitude = coordinate.latitude
        request.longitude = coordinate.longitude
        request.altitude = coordinate.altitude
        
        rospy.loginfo_throttle(0.2,f"latitude : {self.gps.latitude} ")
        rospy.loginfo_throttle(0.2,f"longitude : {self.gps.longitude} ")
        rospy.loginfo_throttle(0.2,f"altitude : {self.gps.altitude} ")
        rospy.loginfo_throttle(0.2,f"position : {self.current_pose} ")
        rospy.loginfo_throttle(0.2,f"heading : {self.compass} ")

        if heading is not None:
            request.yaw = radians(heading)
            self.local_desired_heading = heading
        else:
            request.yaw = radians(self.home_compass)
        
        request.type_mask = 1024 # ignore yaw
        
        # Send request
        rospy.logdebug("publishing setpoint_raw/global", logger_name="move_global")
            
        for i in range(30):
            client.publish(request)
            rospy.sleep(0.01)
            
    def move_global(self, coordinate: GeoPoseStamped = None, heading = None,lat:float=None,lon:float=None, alt:float=None):
        """
            IMPORTANT NOTES:
        - in simulation we need to send the msg  multiple times to make it work
        - in real drone we shouldn't send the msg multiple times but sometimes we need to
        A function to move the drone to certain position in global frame
        """

        # Get client
        client = rospy.Publisher(
            "/mavros/setpoint_position/global",
            GeoPoseStamped,
            queue_size=10,
        )
        # coordinate.altitude = gps.altitude-geoid_height(gps.latitude,gps.longitude)+alt
        request = GeoPoseStamped()
        if coordinate is not None:
            request = coordinate
            # request.pose.position.altitude = self.home_gps.altitude - geoid_height(self.gps.latitude,self.gps.longitude) + request.pose.position.altitude
            # request.pose.position.altitude = request.pose.position.altitude
        elif lat is not None and lon is not None and alt is not None:
            request.pose.position.latitude = lat
            request.pose.position.longitude = lon
            request.pose.position.altitude = self.home_gps.altitude - geoid_height(self.gps.latitude,self.gps.longitude) + alt
        request.header.stamp = rospy.Time.now()
        if heading is not None:
            request.pose.orientation = self.calculate_heading(heading)
        else:
            request.pose.orientation = self.calculate_heading(self.home_compass)

        rospy.logdebug("publishing setpoint_position/global", logger_name="move_global")
        for i in range(30):
            client.publish(request)
            rospy.sleep(0.01)

    def send_mavlink_command(self, request: CommandLongRequest):
        """
        A function to send custom MAVLink command.

        Args:
            - request (CommandLongRequest): command and its param
        """
        # Get client
        client = rospy.ServiceProxy("/mavros/cmd/command", CommandLong)

        # Send request
        response = client(request)

        return response

    def switch_relay(self, relay: int = 0, status: bool = True):
        """
        A function to switch the relay on/off connected to the autopilot
        this function send a commandLong msg to the autopilot

        Args:
            - relay (int): relay number "index started from 0" default 0
            - status (bool): True to turn on, False to turn off default True
        """

        # get parameter
        request = CommandLongRequest()
        request.command = 181 # MAV_CMD_DO_SET_RELAY
        request.param1 = relay
        request.param2 = 1 if status else 0

        return self.send_mavlink_command(request)
    
    def set_servo(self, servo: int = 9, pwm: int = 1100):
        """
        A function to set the servo pwm value connected to the autopilot
        this function send a commandLong msg to the autopilot

        Args:
            - servo (int):  servo number "index started from 9 to 13", default 9 
                            servo 9-13 means aux out 1-4
            - pwm (int): pwm value to set,  default 1100
        """
        # Get client
        client = rospy.ServiceProxy("/mavros/cmd/command", CommandLong)

        # get parameter
        request = CommandLongRequest()
        request.command = 183 # MAV_CMD_DO_SET_SERVO
        request.param1 = servo
        request.param2 = pwm 
        client(request)

        #return self.send_mavlink_command(request)
    
    def set_ekf_source(self, ekf: int = 1):
        """
        A function to switch the relay on/off connected to the autopilot
        this function send a commandLong msg to the autopilot

        Args:
            - ekf (int): EKF source to be used, min value = 0, max value = 3
        """
        valid_ekf = [1,2,3]
        if ekf not in valid_ekf:
            rospy.logerr(f"Invalid EKF source {ekf}. Valid EKF source value is {valid_ekf}")
            return

        # get parameter
        request = CommandLongRequest()
        request.command = 42007 # MAV_CMD_SET_EKF_SOURCE_SET
        request.param1 = ekf

        return self.send_mavlink_command(request)

    def set_speed(self, type:int = 1, speed:int=-2, throttle:int = -1):
        """
        A function to change/set the speed of vehicle
        this function send a commandLong msg to the autopilot

        Args:
            - type (int) : Speed type (0=Airspeed, 1=Ground Speed, 2=Climb Speed, 3=Descent Speed)
            - speed(int) (m/s): (-1 indicates no change, -2 indicates return to default vehicle speed)
            - throttle :  (-1 indicates no change, -2 indicates return to default vehicle throttle value)
        """

        
        # Get client
        client = rospy.ServiceProxy("/mavros/cmd/command", CommandLong)

        # get parameter
        request = CommandLongRequest()
        request.command = 178 # MAV_CMD_DO_CHANGE_SPEED
        request.param1 = type
        request.param2 = speed
        request.param3 = throttle
        client(request) 

        return self.send_mavlink_command(request)

    def next(self):
        """
        A function to move to next waypoint
        """
        self.current_waypoint += 1
        if self.current_waypoint >= len(self.waypoints) or len(self.waypoints) == 0 or self.current_waypoint > len(self.waypoints)-1:
            return False
        return True

    def mission_wp_reached_cb(self, msg):
        self.wp_reached = msg
        
    def get_wp_reached(self):
        return self.wp_reached.wp_seq
    
    def check_waypoint_reached(self,destination: dict = None, pos_tol = 0.1, head_tol = 0.4):
        """This function checks if the waypoint is reached within given tolerance and returns an int of 1 or 0. This function can be used to check when to request the next waypoint in the mission.
        Args:
                pos_tol (float, optional): Position tolerance under which the drone must be with respect to its position in space. Defaults to 0.03.
                head_tol (float, optional): Heading or angle tolerance under which the drone must be with respect to its orientation in space. Defaults to 0.01.
        Returns:
                1 (int): Waypoint reached successfully.
                0 (int): Failed to reach Waypoint.
        """
        if destination == None:
            destination = self.waypoints[self.current_waypoint]

        dx = abs(self.previous_pose.pose.pose.position.x + destination["x"] - self.current_pose.pose.pose.position.x)
        dy = abs(self.previous_pose.pose.pose.position.y + destination["y"] - self.current_pose.pose.pose.position.y)
        dz = abs(self.previous_pose.pose.pose.position.z + destination["z"] - self.current_pose.pose.pose.position.z)

        dMag = sqrt(pow(dx, 2) + pow(dy, 2)) # so the altitude tolerance is just 0.3 in default

        cosErr = cos(radians(self.current_heading)) - cos(
            radians(self.local_desired_heading)
        )

        sinErr = sin(radians(self.current_heading)) - sin(
            radians(self.local_desired_heading)
        )

        dHead = sqrt(pow(cosErr, 2) + pow(sinErr, 2))
        rospy.logdebug_throttle(0.1,f"dx:{dx}, dy:{dy}, dz:{dz}")
        
        # with heading check
        if dMag < pos_tol and dHead < head_tol:
            return 1
        else:
            return 0

    def check_waypoint_reached_global(self,coordinate:GeoPoint ,pos_tol = 2.5, head_tol = 0.4):
        """This function checks if the waypoint is reached within given tolerance and returns an int of 1 or 0. This function can be used to check when to request the next waypoint in the mission.
        Args:
                pos_tol (float, optional): Position tolerance under which the drone must be with respect to its position in space. Defaults to 0.03.
                head_tol (float, optional): Heading or angle tolerance under which the drone must be with respect to its orientation in space. Defaults to 0.01.
        Returns:
                1 (int): Waypoint reached successfully.
                0 (int): Failed to reach Waypoint.
        """
        lat2 = self.gps.latitude
        lon2 = self.gps.longitude
        lat1 = coordinate.latitude
        lon1 = coordinate.longitude
        dist = acos(sin(radians(lat1))*sin(radians(lat2))+cos(radians(lat1))*cos(radians(lat2))*cos(radians(lon2-lon1)))*6400000

        cosErr = cos(radians(self.current_heading)) - cos(
            radians(self.local_desired_heading)
        )

        sinErr = sin(radians(self.current_heading)) - sin(
            radians(self.local_desired_heading)
        )

        dHead = sqrt(pow(cosErr, 2) + pow(sinErr, 2))
        rospy.logdebug_throttle(0.2,f"dist from wp :{dist}")
        
        # with heading check
        if dist < pos_tol :
            return 1
        else:
            return 0
        
    def wait4connect(self):
        """
        Wait for connect is a function that will hold the program until communication with the FCU is established.
        Returns:
                0 (int): Connected to FCU.
                -1 (int): Failed to connect to FCU.
        """
        rospy.loginfo("Waiting for FCU connection")
        while not rospy.is_shutdown() and not self.current_state.connected:
            print("connecting")
            rospy.sleep(0.01)
        else:
            if self.current_state.connected:
                rospy.loginfo("FCU connected")
                return 0
            else:
                rospy.logerr("Error connecting to drone's FCU")
                return -1

    def wait4start(self):
        """
        This function will hold the program until the user signals the FCU to mode enter GUIDED mode. This is typically done from a switch on the safety pilot's remote or from the Ground Control Station.
        Returns:
                0 (int): Mission started successfully.
                -1 (int): Failed to start mission.
        """
        rospy.loginfo("Waiting for user to set mode to GUIDED")

        while not rospy.is_shutdown() and self.current_state.mode != "GUIDED":
            rospy.sleep(0.01)
        else:
            # We will not start if mode is not GUIDED and home heading is not set
            if self.current_state.mode == "GUIDED" and self.home_heading != -1.0:
                rospy.loginfo("Mode set to GUIDED. Starting Mission...")
                return 0
            else:
                rospy.logerr("Error starting mission")
                return -1

    def calculate_heading(self, heading) -> Quaternion:
        """
        This function is used to specify the drone's heading in the local reference frame. Psi is a counter clockwise rotation following the drone's reference frame defined by the x axis through the right side of the drone with the y axis through the front of the drone.
        Args:
                heading (Float): θ(degree) Heading angle of the drone.
        """
        yaw = radians(heading)
        pitch = 0.0
        roll = 0.0

        # cy = cos(yaw * 0.5)
        # sy = sin(yaw * 0.5)

        # cr = cos(roll * 0.5)
        # sr = sin(roll * 0.5)

        # cp = cos(pitch * 0.5)
        # sp = sin(pitch * 0.5)

        qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
        qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
        qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)
        qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)

        q = Quaternion()
        q.x, q.y, q.z, q.w = qx, qy, qz, qw
        
        return q

    def set_heading(self, heading:float):
        self.local_desired_heading = heading
