from uagents import Agent, Bureau, Context, Model
 
RECIPIENT_ADDRESS = "agent1qfwn5w4dute0k905ckdhlfn8vs6kapv7xntgv3rwj2ygxxpvu9l7y7ms870"


class Message(Model):
    message: str
 
carvis = Agent(name="carvis", seed="42")
charging_station_finder = Agent(name="charging_station_finder", seed="42")
 

@carvis.on_interval(period=3.0)
async def send_message(ctx: Context):
    await ctx.send(charging_station_finder.address, Message(message="hello there charging_station_finder"))

 
# @carvis.on_message(model=Message)
# async def carvis_message_handler(ctx: Context, sender: str, msg: Message):
#     ctx.logger.info(f"Received message from {sender}: {msg.message}")


# @charging_station_finder.on_message(model=Message)
# async def send_message(ctx: Context):
#    await ctx.send(ctx, carvis.address, Message(message="Here are the charging stations"))


@charging_station_finder.on_message(model=Message)
async def charging_station_finder_message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")
    await ctx.send(carvis.address, Message(message="Here are the charging stations"))

 
bureau = Bureau()
bureau.add(carvis)
bureau.add(charging_station_finder)
if __name__ == "__main__":
    bureau.run()