# author: Daniel Schnurpfeil
# date: 29.3. 2023

import time
import can

import threading

from can import BufferedReader


# A function that receives messages from the bus and writes them to a file.
def receiving(output_file_path: str, acceptable_ids: list):

    # It converts the list of strings to a list of integers.
    acceptable_ids = [int(i) for i in acceptable_ids]
    # Creating a writer object that writes the received messages to a file.
    writer = can.ASCWriter(output_file_path)
    message_counter = 0
    # A buffer for the received messages.
    reader = BufferedReader()
    while not stop_event.is_set():
        msg = bus.recv(0.01)
        reader.on_message_received(msg)
        rx_msg = reader.get_message(0.01)
        if rx_msg is not None:
            # A way to stop the threads.
            if rx_msg.arbitration_id == int(0xFF):
                print(message_counter)
                # Sending the number of messages received back to the sender.
                bus.send(can.Message(arbitration_id=rx_msg.arbitration_id,
                                     data=[message_counter], is_extended_id=True))
                return

            # It checks if the arbitration id of the received message is in the list of acceptable ids.
            if rx_msg.arbitration_id in acceptable_ids:
                print(output_file_path, message_counter)
                # It writes the received message to the file.
                writer.on_message_received(rx_msg)
                message_counter += 1


# Creating a virtual bus and a reader for the input file.
with can.Bus(interface="virtual", channel="virtual_channel",
                       receive_own_messages=True) as bus:
    # It creates a reader object that reads the messages from the input file.
    iterator_blf = can.BLFReader("./input.blf")

    # A way to stop the threads.
    stop_event = threading.Event()

    # It creates a thread that calls the receiving function with the arguments "./drinks.asc" and [0xC0FFEE, 0xCACA0].
    drink_consumer = threading.Thread(target=receiving, args=("./drinks.asc", [0xC0FFEE, 0xCACA0]))

    # It creates a thread that calls the receiving function with the arguments "./beefs.asc" and [0xBEEF].
    beef_consumer = threading.Thread(target=receiving, args=("./beefs.asc", [0xBEEF]))
    drink_consumer.start()
    beef_consumer.start()

    main_reader = BufferedReader()

    # Sending the messages from the input file to the bus.
    for i in iterator_blf:
        print(i)
        bus.send(i)
        time.sleep(0.1)

    # Receiving the number of messages received by the beef_consumer thread.
    main_reader.on_message_received(bus.recv(0.01))
    m = main_reader.get_message(0.1)
    m = [x for x in m.data]
    print(m)

    stop_event.set()
