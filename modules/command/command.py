"""
Decision-making logic.
"""

import math

from pymavlink import mavutil

from ..common.modules.logger import logger
from ..telemetry import telemetry


class Position:
    """
    3D vector struct.
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Command:  # pylint: disable=too-many-instance-attributes
    """
    Command class to make a decision based on recieved telemetry,
    and send out commands based upon the data.
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        target: Position,  # Put your own arguments here
        local_logger: logger.Logger,
    ):
        """
        Falliable create (instantiation) method to create a Command object.
        """
        return cls(cls.__private_key, 
                connection = connection, 
                target = target, 
                local_logger = local_logger)
        pass  #  Create a Command object

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        target: Position,

        # Put your own arguments here
        local_logger: logger.Logger,
    ) -> None:
        assert key is Command.__private_key, "Use create() method"

        # Do any intializiation here
        self.connection = connection
        self.target = target
        self.local_logger = local_logger
        self.numOfRuns = 0
        self.totalVelocity = 0

    def run(
        self,
        telemetry_data: telemetry.TelemetryData  # Put your own arguments here
    ):
        """
        Make a decision based on received telemetry data.
        """
        self.numOfRuns += 1
        self.totalVelocity += telemetry_data.z_velocity+telemetry_data.x_velocity+telemetry_data.y_velocity

        self.local_logger.info(f"current velocity: {self.totalVelocity/self.numOfRuns}")

        # Use COMMAND_LONG (76) message, assume the target_system=1 and target_componenet=0
        # The appropriate commands to use are instructed below

        # Adjust height using the comand MAV_CMD_CONDITION_CHANGE_ALT (113)
        # String to return to main: "CHANGE_ALTITUDE: {amount you changed it by, delta height in meters}"

        # Adjust direction (yaw) using MAV_CMD_CONDITION_YAW (115). Must use relative angle to current state
        # String to return to main: "CHANGING_YAW: {degree you changed it by in range [-180, 180]}"
        # Positive angle is counter-clockwise as in a right handed system

        if telemetry_data.z - self.target.z >= 0.5:
            self.local_logger.info("TARGET IS LOWER, GOING DOWN")
            self.connection.mav.command_long_send(1, 0, mavutil.mavlink.MAV_CMD_CONDITION_CHANGE_ALT, 0, 1.0, 0, 0, 0, 0, 0, self.target.z)
            return f"CHANGE ALTITUDE: {self.target.z-telemetry_data.z}"
        elif telemetry_data.z - self.target.z <= -0.5:
            self.local_logger.info("TARGET IS HIGHER, GOING UP")

            self.connection.mav.command_long_send(1, 0, mavutil.mavlink.MAV_CMD_CONDITION_CHANGE_ALT, 0, 1.0, 0, 0, 0, 0, 0, self.target.z)
            return f"CHANGE ALTITUDE: {self.target.z-telemetry_data.z}"
        
        
        #Calculate bearing to target
        dx = self.target.x - telemetry_data.x
        dy = self.target.y - telemetry_data.y  
        bearing_rad = math.atan2(dy, dx)  
        bearing_deg = math.degrees(bearing_rad)
        
        #Current yaw in degrees
        current_yaw_deg = math.degrees(telemetry_data.yaw)
        
        #Calculate yaw difference
        delta_yaw_deg = bearing_deg - current_yaw_deg
        
        #Normalize 
        delta_yaw_deg = (delta_yaw_deg + 180) % 360 - 180
        
        if abs(delta_yaw_deg) > 5:
            self.local_logger.info("TARGET NOT IN SIGHT, TURNING")
            self.connection.mav.command_long_send(1, 0, mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0,0, 5.0, 1, 1, 0, 0, 0  )
            return f"CHANGE YAW: {delta_yaw_deg}"
        
        


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
