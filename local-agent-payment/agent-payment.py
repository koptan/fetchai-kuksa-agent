'''
MIT License

Copyright (c) 2024 Mohammad Zubair, Abdulrahman AlKoptan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from pydantic import Field
import asyncio
from kuksa_client.grpc.aio import VSSClient
from kuksa_client.grpc import Any, Datapoint
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
from web3.middleware import geth_poa_middleware
from sdvlink_companion import Set

from web3 import Web3, AsyncWeb3, EthereumTesterProvider
import json

init(autoreset=True)

DATABROKER_ADDRESS = "40.114.167.144"
DATABROKER_PORT = 55555
PAYMENT_PATH = "Vehicle.VehicleIdentification.VehicleSpecialUsage"  # VSS Path co-opted for payment
# BLOCKCHAIN_ADDRESS = "ws://158.177.1.17:8546"
# CONTRACT_ADDRESS = "0x9B8397f1B0FEcD3a1a40CdD5E8221Fa461898517"
BLOCKCHAIN_ADDRESS = "wss://ethereum-sepolia-rpc.publicnode.com"
CONTRACT_ADDRESS = "0x06825EB4c30081568A16249F57E60319F0E99a86"
TOKEN_ID = 1;

vssClient = VSSClient(DATABROKER_ADDRESS, DATABROKER_PORT)
w3 = Web3(Web3.WebsocketProvider(BLOCKCHAIN_ADDRESS))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

test_private_key_1 = "3497ac60bf7691caa9e8faeca06422521f4272f82bcfe4f5673900524e660592"  # "0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63";
test_private_key_2 = "40160557dc9d2674e2d7f32f7e3c869af9cdd779f052d733227233a3e2cd4745"  # "0xc87509a1c067bbde78beb793e6fa76530b6382a4c0241e5e4a9ec0a0f44dc0d3";
test_private_key_3 = "0xae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f";

account_car = w3.eth.account.from_key(test_private_key_1)
account_station = w3.eth.account.from_key(test_private_key_2)
account_3 = w3.eth.account.from_key(test_private_key_3)

"""
What code does:
- Vehicle.VehicleIdentification.OptionalExtras will be used for both incoming and outgoing messsages
- Subscribes to Vehicle.VehicleIdentification.OptionalExtras
- Format of value is a string with pipe delimited values
- handlePayment will be called 


Data is expected to come in from Vehicle.VehicleIdentification.VehicleSpecialUsage 
Format:
Inbound >>>|TS|ID<str>|Tx-Type<str>|Value<str>
for example:
>>>|2024-02-21-09:23:45|DriverABC|Fuel|223.56 (Fuel is the goods, 223.56 is the payment amount)
>>>|2024-02-21-09:23:45|DriverABC|Parking|60  (Parking is the goods, 60 is the parking duration in minutes)

Outbound <<<|TS|transactionid|message
example: <<<|2024-02-21-09:23:45|TX123456|Transaction Complete. Payment has been made
"""  #


def logError(msg):
    log(f"{Fore.RED} {msg}")


def log(msg):
    current_GMT = time.gmtime()
    ts = calendar.timegm(current_GMT)
    dt = datetime.fromtimestamp(ts)
    print(f"{Fore.GREEN} {dt} {msg}")


def do_the_payment(price):
    f = open("Token.json", "r")
    token = json.load(f)

    init_bytecode = token['bytecode']
    init_abi = token['abi']
    nonce = w3.eth.get_transaction_count(account_car.address)
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=init_abi)
    chain_id = w3.eth.chain_id
    transfer_tx = contract.functions.safeTransferFrom(account_car.address, account_station.address, TOKEN_ID, price,
                                                      bytes('0x0', 'utf-8')).build_transaction(
        {
            'from': account_car.address,
            'nonce': nonce,
            'gas': 1000000,
        })

    signed_txn = w3.eth.account.sign_transaction(transfer_tx, private_key=account_car.key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_hash = w3.to_hex(tx_hash)
    print(f"Transction hash is {tx_hash}")


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
PATH_NOTIFICATION = "Vehicle.VehicleIdentification.VehicleSpecialUsage"

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
    await asyncio.sleep(0.85 / FACTOR)

    # Left turn
    await Set(PATH_STEERING_ANGLE, LEFT_TURN_VALUE * 1.9, DataType.FLOAT)
    await asyncio.sleep(LEFT_TURN_DUR / 1.9)
    await Set(PATH_STEERING_ANGLE, 0, DataType.FLOAT)

    await asyncio.sleep(0.2 / FACTOR)

    # Stop
    await Set(PATH_VEHICLE_SPEED, 0, DataType.FLOAT)
    await asyncio.sleep(1)


async def show_notification(header, text):
    await Set(PATH_NOTIFICATION, f"<<<|notification|{header}|{text}", DataType.STRING)


async def hide_notification():
    await Set(PATH_NOTIFICATION, "<<<|hide", DataType.STRING)


async def subscribe():
    """ Subscribe to values used by app and sync changes """
    print(f"   {Fore.YELLOW}>>> {Fore.RED}Subscribing required values..{Fore.YELLOW}<<<")

    do_the_payment(100)

    async with vssClient:
        entries = []
        entries.append(SubscribeEntry(PAYMENT_PATH, View.FIELDS, (VssField.VALUE, VssField.ACTUATOR_TARGET)))

        async for updates in vssClient.subscribe(entries=entries):
            for update in updates:
                # print("Incoming message: " + update.entry.value.value.values[0])
                if update.entry.value is not None:
                    frags = parseInbound(update.entry.value.value.values[0])

                    if isinstance(frags, str):
                        print(f"Unexpected or invalid content returned. Ignoring content: {frags}")
                        continue

                    ts = frags[1]
                    identity = frags[2]
                    goods = frags[3]
                    paymentAmount = frags[4]
                    await handlePayment(ts, identity, goods, paymentAmount)


def parseInbound(val):
    frags = val.split("|")

    if frags[0] == "<<<":
        return "Ignoring outbound message"

    if len(frags) != 6:
        return "Unexpected parameters encountered. Expected 6"

    if frags[0] != ">>>":
        return "Unexpected marker encountered. Expecting '>>>'"

    try:
        float(frags[4])
    except ValueError:
        return "Unable to parse Price. Price is not float data."

    return frags


async def handlePayment(ts, identity, goods, paymentAmount):
    print(f"handlePayment {ts} {identity} {goods} {paymentAmount}")
    """ Handle SmartContract Payments and then write to databroker the results """

    print(f"Connected to blockchain: {w3.is_connected()}")

    returnValue = f"<<<|payment|True|x893794872u234234sdfsd|30|Eth|Payment Complete"

    try:
        async with vssClient:
            entry = EntryUpdate(DataEntry(PAYMENT_PATH, value=Datapoint(value=returnValue),
                                          metadata=Metadata(data_type=DataType.STRING_ARRAY)), (VssField.VALUE,))
            await vssClient.set(updates=(entry,))
    except Exception as err:
        logError(
            f"ERROR: Sending data to Kuksa Databroker {err}. Connection Details: {DATABROKER_ADDRESS} port {DATABROKER_PORT}")


async def main():
    await asyncio.gather(subscribe(), demo_move())


if __name__ == "__main__":
    asyncio.run(main())
