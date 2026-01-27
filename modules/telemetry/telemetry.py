"""
Telemetry gathering logic.
"""

import time

from pymavlink import mavutil

from ..common.modules.logger import logger


class TelemetryData:  # pylint: disable=too-many-instance-attributes
    """
    Python struct to represent Telemtry Data. Contains the most recent attitude and position reading.
    """

    def __init__(
        self,
        time_since_boot: int | None = None,  # ms
        x: float | None = None,  # m
        y: float | None = None,  # m
        z: float | None = None,  # m
        x_velocity: float | None = None,  # m/s
        y_velocity: float | None = None,  # m/s
        z_velocity: float | None = None,  # m/s
        roll: float | None = None,  # rad
        pitch: float | None = None,  # rad
        yaw: float | None = None,  # rad
        roll_speed: float | None = None,  # rad/s
        pitch_speed: float | None = None,  # rad/s
        yaw_speed: float | None = None,  # rad/s
    ) -> None:
        self.time_since_boot = time_since_boot
        self.x = x
        self.y = y
        self.z = z
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity
        self.z_velocity = z_velocity
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.roll_speed = roll_speed
        self.pitch_speed = pitch_speed
        self.yaw_speed = yaw_speed

    def __str__(self) -> str:
        return f"""{{
            time_since_boot: {self.time_since_boot},
            x: {self.x},
            y: {self.y},
            z: {self.z},
            x_velocity: {self.x_velocity},
            y_velocity: {self.y_velocity},
            z_velocity: {self.z_velocity},
            roll: {self.roll},
            pitch: {self.pitch},
            yaw: {self.yaw},
            roll_speed: {self.roll_speed},
            pitch_speed: {self.pitch_speed},
            yaw_speed: {self.yaw_speed}
        }}"""


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Telemetry:
    """
    Telemetry class to read position and attitude (orientation).
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,  # Put your own arguments here
        local_logger: logger.Logger,
    ):
        """
        Falliable create (instantiation) method to create a Telemetry object.
        """
        if connection is not None:
            return cls(cls.__private_key, connection, local_logger=local_logger)
        else:
            local_logger.error("Failed to create a Telemetry object due to missing connection")
            return None

        pass  # Create a Telemetry object

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,  # Put your own arguments here
        local_logger: logger.Logger,
    ) -> None:
        assert key is Telemetry.__private_key, "Use create() method"

        # Do any intializiation here
        self.connection = connection
        self.local_logger = local_logger
        
    def run(
        self,  # Put your own arguments here
    ):
        """
        Receive LOCAL_POSITION_NED and ATTITUDE messages from the drone,
        combining them together to form a single TelemetryData object.
        """
        # Read MAVLink message LOCAL_POSITION_NED (32)
        # Read MAVLink message ATTITUDE (30)
        # Return the most recent of both, and use the most recent message's timestamp

        start_time = time.time()
        return_Telemetry = TelemetryData()

        run = True
        #Bool tuple to check if both attitude and local position data is received
        data_received = [False, False]
        while run:
            #Check to see if time is greater than one
            if time.time()-start_time >=1:
                return None

            #Attempt to take in attitude data
            attitude = self.connection.recv_match(type = 'ATTITUDE', timeout=0.0)

            #Set telemetry data to corresponding incoming data
            if attitude is not None:
                data_received[0] = True

                return_Telemetry.time_since_boot = attitude.time_boot_ms
                return_Telemetry.roll = attitude.roll
                return_Telemetry.pitch = attitude.pitch
                return_Telemetry.yaw = attitude.yaw
                return_Telemetry.roll_speed = attitude.rollspeed
                return_Telemetry.pitch_speed = attitude.pitchspeed
                return_Telemetry.yaw_speed = attitude.yawspeed
            
            #Take in position data
            local_Position = self.connection.recv_match(type = 'LOCAL_POSITION_NED', timeout=0.0)
            #Same thing as attitude data intake
            if local_Position is not None:
                data_received[1] = True

                return_Telemetry.time_since_boot = local_Position.time_boot_ms
                return_Telemetry.x = local_Position.x
                return_Telemetry.y = local_Position.y
                return_Telemetry.z = local_Position.z
                return_Telemetry.x_velocity = local_Position.vx
                return_Telemetry.y_velocity = local_Position.vy
                return_Telemetry.z_velocity = local_Position.vz
            
            
            #If both data types have been received, return the data to worker
            if all(data_received):
                return return_Telemetry

# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
