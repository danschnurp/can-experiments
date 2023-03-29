
import asyncio
from typing import List

import can
from can.notifier import MessageRecipient


def process_msg(msg: can.Message, allowed_ids=[0xC0FFEE, 0xCACA0], writer=can.ASCWriter("./drinks.asc"), message_counter=0) -> None:
    if msg is not None:
        if msg.arbitration_id == int(0xFF):
            # bus.send(can.Message(arbitration_id=msg.arbitration_id,
            #                      data=[message_counter], is_extended_id=True))
            print(message_counter)
            return

        if msg.arbitration_id in allowed_ids:
            writer.on_message_received(msg)
            message_counter += 1


def process_msg2(msg: can.Message, allowed_ids=[0xBEEF], writer=can.ASCWriter("./beefs.asc"), message_counter=0) -> None:
    if msg is not None:
        if msg.arbitration_id == int(0xFF):
            # bus.send(can.Message(arbitration_id=msg.arbitration_id,
            #                      data=[message_counter], is_extended_id=True))
            print(message_counter)
            return

        if msg.arbitration_id in allowed_ids:
            writer.on_message_received(msg)
            message_counter += 1


async def main() -> None:
    """The main function that runs in the loop."""

    with can.Bus(  # type: ignore
            interface="virtual", channel="my_channel_0", receive_own_messages=True
    ) as bus:
        reader = can.AsyncBufferedReader()
        listeners: List[MessageRecipient] = [
            process_msg,  # Callback function
            process_msg2,
            reader,

        ]
        # Create Notifier with an explicit loop to use for scheduling of callbacks
        loop = asyncio.get_running_loop()
        notifier = can.Notifier(bus, listeners, loop=loop)

        for i in can.BLFReader("./input.blf"):
            print(i)
            # Delay response 0.1
            bus.send(i)
            await asyncio.sleep(0.01)
            # Wait for next message from AsyncBufferedReader
            msg = await reader.get_message()
            # process_msg(msg)
            process_msg2(msg)
            # process_msg(bus, msg, [0xBEEF], can.ASCWriter("./beefs.asc"))

        print("Done!")

        # Clean-up
        notifier.stop()


if __name__ == "__main__":
    #     for i in can.BLFReader("./input.blf"):
    #         print(i)
    asyncio.run(main())
