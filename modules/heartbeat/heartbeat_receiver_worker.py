"""
Heartbeat worker that sends heartbeats periodically.
"""

import os
import pathlib
import time  ### ADDED THIS MYSELF

from pymavlink import mavutil

from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import heartbeat_receiver
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================


def heartbeat_receiver_worker(
    connection: mavutil.mavfile,
    controller: worker_controller.WorkerController,
    output_queue: queue_proxy_wrapper.queue,  # Place your own arguments here
    # Add other necessary worker arguments here
) -> None:
    """
    Worker process.

    args... describe what the arguments are
    """
    # =============================================================================================
    #                          ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
    # =============================================================================================

    # Instantiate logger
    worker_name = pathlib.Path(__file__).stem
    process_id = os.getpid()
    result, local_logger = logger.Logger.create(f"{worker_name}_{process_id}", True)
    if not result:
        print("ERROR: Worker failed to create logger")
        return

    # Get Pylance to stop complaining
    assert local_logger is not None

    local_logger.info("Logger initialized", True)

    # =============================================================================================
    #                          ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
    # =============================================================================================
    # Instantiate class object (heartbeat_receiver.HeartbeatReceiver)
    hb_receiver = heartbeat_receiver.HeartbeatReceiver.create(connection)
    # Main loop: do work.
    num_missed = 0
    while not controller.is_exit_requested():
        message = hb_receiver.run()
        if message is not None:
            num_missed = 0
        elif message is None:
            num_missed += 1
            local_logger.error(f"Heartbeat from Drone Missed!!!{num_missed}")

        if num_missed >= 5:
            output_queue.put("Disconnected")
            break
        output_queue.put("Connected")
        time.sleep(1)


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
