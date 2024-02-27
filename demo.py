from pydantic import Field
import asyncio
from kuksa_client.grpc.aio import VSSClient
from kuksa_client.grpc import Datapoint
from kuksa_client.grpc import DataEntry
from kuksa_client.grpc import DataType
from kuksa_client.grpc import EntryUpdate
from kuksa_client.grpc import Field as VssField
from kuksa_client.grpc import Metadata
from kuksa_client.grpc import EntryRequest
from kuksa_client.grpc import View
from kuksa_client.grpc import SubscribeEntry
from colorama import init
from colorama import Fore
import calendar
import time
from datetime import datetime
from sdvlink_companion import Set, logSetMessage, logError

from web3 import Web3, AsyncWeb3

init(autoreset=True)

DATABROKER_ADDRESS = "localhost"
DATABROKER_PORT = 55555
PAYMENT_PATH = "Vehicle.VehicleIdentification.VehicleSpecialUsage"  # VSS Path co-opted for payment
NOTIFICATION_PATH = "Vehicle.VehicleIdentification.VehicleSpecialUsage"
BLOCKCHAIN_ADDRESS = "ws://158.177.1.17:8546"

PATH_VEHICLE_SPEED = "Vehicle.Speed"
PATH_LEFTINDICATOR_SIGNALING = "Vehicle.Body.Lights.DirectionIndicator.Left.IsSignaling"
PATH_RIGHTINDICATOR_SIGNALING = "Vehicle.Body.Lights.DirectionIndicator.Right.IsSignaling"
PATH_ENGINE_RUNNING = "Vehicle.Powertrain.CombustionEngine.IsRunning"
PATH_STEERING_ANGLE = "Vehicle.Chassis.Axle.Row1.SteeringAngle"
PATH_BEAM_LOW_ISON = "Vehicle.Body.Lights.Beam.Low.IsOn"
PATH_BEAM_HIGH_ISON = "Vehicle.Body.Lights.Beam.High.IsOn"
PATH_CURRENTGEAR = "Vehicle.Powertrain.Transmission.CurrentGear"
PATH_BRAKEPEDAL_POSITION = "Vehicle.Chassis.Brake.PedalPosition"
PATH_ISMOVING = "Vehicle.IsMoving"
PATH_START_TIME = "Vehicle.StartTime"
PATH_TRIP_DURATION = "Vehicle.TripDuration"
PATH_EMERGENCY_BRAKE_DETECTED = "Vehicle.Chassis.Brake.IsDriverEmergencyBrakingDetected"
PATH_BRAKEPEDAL_ISACTIVE = "Vehicle.Body.Lights.Brake.IsActive"
PATH_PARKING_BRAKE_ENGAGED = "Vehicle.Chassis.ParkingBrake.IsEngaged"

vssClient = VSSClient(DATABROKER_ADDRESS, DATABROKER_PORT)


async def main():
    await demo_move()

    return

    # await notify_ui("BLANK")

    # return
    # await notify_ui("Dialog", "Choose a Charging Station", "Station One,Station Two,Station Three")

    # return
    for speed in range(10, 20):
        try:
            async with vssClient:
                entry = EntryUpdate(DataEntry(PATH_VEHICLE_SPEED, value=Datapoint(value=str(speed)),
                                              metadata=Metadata(data_type=DataType.FLOAT)), (VssField.VALUE,))
                await vssClient.set(updates=(entry,))
                print(speed)
        except Exception as err:
            print(
                f"ERROR: Sending data to Kuksa Databroker {err}. Connection Details: {DATABROKER_ADDRESS} port {DATABROKER_PORT}")
        time.sleep(1)


FACTOR = 1
SPEED = 8 * FACTOR
LEFT_TURN_VALUE = 10
RIGHT_TURN_VALUE = -LEFT_TURN_VALUE

LEFT_TURN_DUR = 1.775


async def demo_move():
    await Set(PATH_ENGINE_RUNNING, True, DataType.BOOLEAN)
    await Set(PATH_PARKING_BRAKE_ENGAGED, False, DataType.BOOLEAN)
    await Set(PATH_VEHICLE_SPEED, SPEED, DataType.FLOAT)

    # First straight
    await asyncio.sleep(6.8 / FACTOR)

    # Left turn
    await Set(PATH_STEERING_ANGLE, LEFT_TURN_VALUE, DataType.FLOAT)
    await asyncio.sleep(LEFT_TURN_DUR)
    await Set(PATH_STEERING_ANGLE, 0, DataType.FLOAT)

    # 2nd straight
    await asyncio.sleep(9.7 / FACTOR)

    # Left turn
    await Set(PATH_STEERING_ANGLE, LEFT_TURN_VALUE, DataType.FLOAT)
    await asyncio.sleep(LEFT_TURN_DUR)
    await Set(PATH_STEERING_ANGLE, 0, DataType.FLOAT)

    # 3rd straight
    await asyncio.sleep(1.3 / FACTOR)

    # Left turn
    await Set(PATH_STEERING_ANGLE, LEFT_TURN_VALUE, DataType.FLOAT)
    await asyncio.sleep(LEFT_TURN_DUR)
    await Set(PATH_STEERING_ANGLE, 0, DataType.FLOAT)

    # 4th straight
    await asyncio.sleep(0.9 / FACTOR)

    # Left turn
    await Set(PATH_STEERING_ANGLE, LEFT_TURN_VALUE * 1.9, DataType.FLOAT)
    await asyncio.sleep(LEFT_TURN_DUR / 1.8)
    await Set(PATH_STEERING_ANGLE, 0, DataType.FLOAT)

    await asyncio.sleep(0.2 / FACTOR)

    # Stop
    await Set(PATH_VEHICLE_SPEED, 0, DataType.FLOAT)
    await asyncio.sleep(1)


async def notify_ui(req_type, text1=None, text2=None):
    try:
        # Append text1 and text2 using pipe delimiter if not none
        payload = f"@UIRequest|{req_type}"
        if text1 is not None:
            payload += f"|{text1}"
        if text2 is not None:
            payload += f"|{text2}"

        async with vssClient:
            entry = EntryUpdate(DataEntry(NOTIFICATION_PATH, value=Datapoint(value=payload),
                                          metadata=Metadata(data_type=DataType.STRING)), (VssField.VALUE,))
            await vssClient.set(updates=(entry,))

            # Wait for response
            # response = await vssClient.get(requests=(EntryRequest(NOTIFICATION_PATH, (VssField.VALUE), 1)))
    except Exception as err:
        print(
            f"ERROR: Sending data to Kuksa Databroker {err}. Connection Details: {DATABROKER_ADDRESS} port {DATABROKER_PORT}")


if __name__ == "__main__":
    asyncio.run(main())
