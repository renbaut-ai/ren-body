#!/usr/bin/env python3
"""
Smooth Motion Planning for SO-101 Robot Arms
Provides interpolated trajectories and velocity profiling.
"""

import os
import time
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import scservo_sdk as sdk

# Servo control table addresses
ADDR_TORQUE_ENABLE = 40
ADDR_GOAL_POSITION = 42
ADDR_PRESENT_POSITION = 56
ADDR_MOVING_SPEED = 46
ADDR_PRESENT_SPEED = 58
ADDR_PRESENT_LOAD = 60

# Joint configuration
JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
JOINT_IDS = {name: i+1 for i, name in enumerate(JOINTS)}

# Default limits (in servo units 0-4095, ~0-360°)
DEFAULT_LIMITS = {
    "shoulder_pan": (500, 3500),
    "shoulder_lift": (500, 3500),
    "elbow_flex": (500, 3500),
    "wrist_flex": (500, 3500),
    "wrist_roll": (500, 3500),
    "gripper": (1000, 3000),
}

# Default movement speed (0-1023, 0=max). 250 is smooth but purposeful.
DEFAULT_SPEED = 250

@dataclass
class ArmState:
    """Current state of all joints"""
    positions: Dict[str, int]  # Raw servo positions (0-4095)
    velocities: Optional[Dict[str, int]] = None
    loads: Optional[Dict[str, int]] = None
    timestamp: float = 0.0

class SmoothMotion:
    """
    Smooth motion controller for robot arms.
    Implements trajectory interpolation and velocity profiling.
    """
    
    def __init__(self, port: str, baudrate: int = 1000000):
        self.port = port
        self.baudrate = baudrate
        self.port_handler = None
        self.packet_handler = None
        self.connected = False
        self.joint_limits = DEFAULT_LIMITS.copy()
        
    def connect(self) -> bool:
        """Connect to the arm"""
        self.port_handler = sdk.PortHandler(self.port)
        self.packet_handler = sdk.PacketHandler(0)
        
        if not self.port_handler.openPort():
            print(f"Failed to open port {self.port}")
            return False
        
        self.port_handler.setBaudRate(self.baudrate)
        self.connected = True
        return True
    
    def disconnect(self):
        """Disconnect from the arm"""
        if self.port_handler:
            self.port_handler.closePort()
        self.connected = False
    
    def read_state(self) -> ArmState:
        """Read current state of all joints"""
        positions = {}
        for name, servo_id in JOINT_IDS.items():
            pos, result, _ = self.packet_handler.read2ByteTxRx(
                self.port_handler, servo_id, ADDR_PRESENT_POSITION
            )
            if result == sdk.COMM_SUCCESS:
                positions[name] = pos
        
        return ArmState(positions=positions, timestamp=time.time())
    
    def set_torque(self, enable: bool, joints: List[str] = None):
        """Enable/disable torque on joints"""
        joints = joints or JOINTS
        value = 1 if enable else 0
        for name in joints:
            self.packet_handler.write1ByteTxRx(
                self.port_handler, JOINT_IDS[name], ADDR_TORQUE_ENABLE, value
            )
    
    def set_speed(self, speed: int, joints: List[str] = None):
        """Set movement speed for joints (0-1023, 0=max)"""
        joints = joints or JOINTS
        for name in joints:
            self.packet_handler.write2ByteTxRx(
                self.port_handler, JOINT_IDS[name], ADDR_MOVING_SPEED, speed
            )
    
    def _clamp_position(self, joint: str, position: int) -> int:
        """Clamp position to joint limits"""
        min_pos, max_pos = self.joint_limits.get(joint, (0, 4095))
        return max(min_pos, min(max_pos, position))
    
    def move_joint(self, joint: str, position: int, speed: int = 300):
        """Move a single joint to position"""
        position = self._clamp_position(joint, position)
        servo_id = JOINT_IDS[joint]
        
        self.packet_handler.write2ByteTxRx(
            self.port_handler, servo_id, ADDR_MOVING_SPEED, speed
        )
        self.packet_handler.write2ByteTxRx(
            self.port_handler, servo_id, ADDR_GOAL_POSITION, position
        )
    
    def move_joints(self, positions: Dict[str, int], speed: int = 300):
        """Move multiple joints simultaneously"""
        for joint, position in positions.items():
            self.move_joint(joint, position, speed)
    
    # ==================== RECOMMENDED API ====================
    
    def move_to(self, positions: Dict[str, int], speed: int = None, wait: float = None):
        """
        Move to target positions using servo's native motion control.
        This is the recommended way to move - smooth and efficient.
        
        Args:
            positions: Target positions for joints (servo units 0-4095)
            speed: Movement speed (0-1023, 0=max). Default: DEFAULT_SPEED (250)
            wait: Optional seconds to wait after sending command.
                  If None, estimates based on distance and speed.
        """
        speed = speed if speed is not None else DEFAULT_SPEED
        self.move_joints(positions, speed=speed)
        
        if wait is not None:
            time.sleep(wait)
        else:
            # Estimate wait time based on max distance and speed
            current = self.read_state().positions
            max_dist = 0
            for joint, target in positions.items():
                if joint in current:
                    dist = abs(target - current[joint])
                    max_dist = max(max_dist, dist)
            # Rough estimate: speed 250 moves ~500 units/sec
            estimated_time = (max_dist / 500) * (250 / max(speed, 1)) + 0.1
            time.sleep(min(estimated_time, 3.0))  # Cap at 3 seconds
    
    def go_home(self, speed: int = None):
        """Move all joints to center position (2048)"""
        home = {joint: 2048 for joint in JOINTS}
        self.move_to(home, speed=speed)
    
    # ==================== SMOOTH MOTION (LEGACY) ====================
    
    def linear_interpolate(
        self, 
        start: Dict[str, int], 
        end: Dict[str, int], 
        steps: int
    ) -> List[Dict[str, int]]:
        """
        Generate linear interpolation between two positions.
        Returns list of intermediate positions.
        """
        trajectory = []
        for i in range(steps + 1):
            t = i / steps
            point = {}
            for joint in JOINTS:
                if joint in start and joint in end:
                    point[joint] = int(start[joint] + t * (end[joint] - start[joint]))
            trajectory.append(point)
        return trajectory
    
    def cubic_interpolate(
        self,
        start: Dict[str, int],
        end: Dict[str, int],
        steps: int
    ) -> List[Dict[str, int]]:
        """
        Generate cubic (ease-in-out) interpolation.
        Smoother acceleration/deceleration at endpoints.
        """
        trajectory = []
        for i in range(steps + 1):
            # Cubic ease-in-out: t' = 3t² - 2t³
            t = i / steps
            t_smooth = 3 * t * t - 2 * t * t * t
            
            point = {}
            for joint in JOINTS:
                if joint in start and joint in end:
                    point[joint] = int(start[joint] + t_smooth * (end[joint] - start[joint]))
            trajectory.append(point)
        return trajectory
    
    def trapezoidal_velocity(
        self,
        start: Dict[str, int],
        end: Dict[str, int],
        steps: int,
        accel_fraction: float = 0.25
    ) -> List[Dict[str, int]]:
        """
        Generate trapezoidal velocity profile.
        - Accelerates for first accel_fraction of motion
        - Constant velocity in middle
        - Decelerates for last accel_fraction of motion
        """
        trajectory = []
        accel_steps = int(steps * accel_fraction)
        
        for i in range(steps + 1):
            if i < accel_steps:
                # Acceleration phase: quadratic ramp
                t = 0.5 * (i / accel_steps) ** 2 * accel_fraction
            elif i > steps - accel_steps:
                # Deceleration phase
                remaining = (steps - i) / accel_steps
                t = 1.0 - 0.5 * remaining ** 2 * accel_fraction
            else:
                # Constant velocity phase
                t = accel_fraction / 2 + (i - accel_steps) / (steps - 2 * accel_steps) * (1 - accel_fraction)
            
            point = {}
            for joint in JOINTS:
                if joint in start and joint in end:
                    point[joint] = int(start[joint] + t * (end[joint] - start[joint]))
            trajectory.append(point)
        
        return trajectory
    
    def execute_trajectory(
        self,
        trajectory: List[Dict[str, int]],
        dt: float = 0.02,
        speed: int = 0  # 0 = max speed (servo handles timing)
    ):
        """
        Execute a trajectory by sending waypoints at regular intervals.
        
        Args:
            trajectory: List of position dictionaries
            dt: Time between waypoints (seconds)
            speed: Servo speed setting (0=max, let dt control timing)
        """
        self.set_torque(True)
        self.set_speed(speed)
        
        for waypoint in trajectory:
            for joint, position in waypoint.items():
                position = self._clamp_position(joint, position)
                self.packet_handler.write2ByteTxRx(
                    self.port_handler, 
                    JOINT_IDS[joint], 
                    ADDR_GOAL_POSITION, 
                    position
                )
            time.sleep(dt)
    
    def smooth_move(
        self,
        target: Dict[str, int],
        duration: float = 1.0,
        profile: str = "cubic"
    ):
        """
        High-level smooth move to target position.
        
        Args:
            target: Target positions for joints
            duration: Total movement time (seconds)
            profile: Interpolation profile ("linear", "cubic", "trapezoidal")
        """
        current = self.read_state()
        
        # Calculate steps based on duration (50Hz update rate)
        steps = max(int(duration * 50), 10)
        dt = duration / steps
        
        # Generate trajectory
        if profile == "linear":
            trajectory = self.linear_interpolate(current.positions, target, steps)
        elif profile == "cubic":
            trajectory = self.cubic_interpolate(current.positions, target, steps)
        elif profile == "trapezoidal":
            trajectory = self.trapezoidal_velocity(current.positions, target, steps)
        else:
            raise ValueError(f"Unknown profile: {profile}")
        
        # Execute
        self.execute_trajectory(trajectory, dt=dt, speed=0)
    
    def wave(self, joint: str = "wrist_roll", amplitude: int = 400, cycles: int = 3, period: float = 0.5):
        """Do a wave motion on a joint"""
        current = self.read_state()
        center = current.positions.get(joint, 2048)
        
        self.set_torque(True, [joint])
        self.set_speed(400, [joint])
        
        steps_per_cycle = int(period * 50)
        
        for cycle in range(cycles):
            for i in range(steps_per_cycle):
                t = i / steps_per_cycle
                offset = int(amplitude * math.sin(2 * math.pi * t))
                self.move_joint(joint, center + offset)
                time.sleep(period / steps_per_cycle)
        
        # Return to center
        self.move_joint(joint, center)
        time.sleep(0.3)
        self.set_torque(False, [joint])

class DualArmController:
    """Controller for synchronized dual-arm movements"""
    
    def __init__(self, leader_port: str, follower_port: str):
        self.leader = SmoothMotion(leader_port)
        self.follower = SmoothMotion(follower_port)
    
    def connect(self) -> bool:
        return self.leader.connect() and self.follower.connect()
    
    def disconnect(self):
        self.leader.disconnect()
        self.follower.disconnect()
    
    def mirror_move(self, target: Dict[str, int], duration: float = 1.0):
        """Move both arms to same position (mirrored)"""
        import threading
        
        def move_arm(arm, target):
            arm.smooth_move(target, duration=duration)
        
        t1 = threading.Thread(target=move_arm, args=(self.leader, target))
        t2 = threading.Thread(target=move_arm, args=(self.follower, target))
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    
    def synchronized_wave(self, cycles: int = 3):
        """Both arms wave together"""
        import threading
        
        t1 = threading.Thread(target=self.leader.wave, kwargs={"cycles": cycles})
        t2 = threading.Thread(target=self.follower.wave, kwargs={"cycles": cycles})
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()

# Example usage and testing
if __name__ == "__main__":
    import json
    
    # Load config
    config_path = os.path.expanduser("~/.openclaw/skills/lerobot/config.json")
    with open(config_path) as f:
        config = json.load(f)
    
    leader_port = config["leader"]["port"].replace("tty.", "cu.")
    follower_port = config["follower"]["port"].replace("tty.", "cu.")
    
    print("Testing Motion Controller")
    print(f"Leader: {leader_port}")
    print(f"Follower: {follower_port}")
    print(f"Default speed: {DEFAULT_SPEED}")
    
    # Test single arm
    arm = SmoothMotion(follower_port)
    if arm.connect():
        print("\nConnected to follower arm")
        
        state = arm.read_state()
        home = state.positions.copy()
        print(f"Home positions: {home}")
        
        arm.set_torque(True)
        
        # Test move_to (recommended API)
        print("\nTesting move_to (native servo motion)...")
        target = home.copy()
        target["shoulder_pan"] = min(home.get("shoulder_pan", 2048) + 400, 3000)
        arm.move_to(target)
        
        target["shoulder_pan"] = max(home.get("shoulder_pan", 2048) - 400, 1000)
        arm.move_to(target)
        
        # Return home
        print("Returning home...")
        arm.move_to(home)
        
        arm.set_torque(False)
        arm.disconnect()
        print("Done!")
    else:
        print("Failed to connect")
