# Encoding headers
POSITION_DATA = 0b10000
HEADING_DATA = 0b10001
VOLTAGE_DATA = 0b10010
TEMP_DATA = 0b10011
MOVEMENT_STAT_DATA = 0b10100
MISSION_STAT_DATA = 0b10101
FLOODED_DATA = 0b10110
DEPTH_DATA = 0b10111


def decode_command(self_obj, header_str, line):
    if header_str == POSITION_DATA:
        # reads in remaining byte
        remain = self_obj.radio.read(2)
        remain = int.from_bytes(remain, "big")

        # contains x and y data
        data = remain | ((line & 0b00000111) << 16)

        x = (data >> 9)
        y = (data & 0b111111111)

        # TODO, call function and update positioning in gui

    elif header_str == HEADING_DATA:
        x
    elif header_str == VOLTAGE_DATA:
        x
    elif header_str == TEMP_DATA:
        x
    elif header_str == MOVEMENT_STAT_DATA:
        x
    elif header_str == MISSION_STAT_DATA:
        x
    elif header_str == FLOODED_DATA:
        x
    elif header_str == DEPTH_DATA:
        print("Depth Case")

        # reads in remaining bytes
        remain = self_obj.radio.read(1)
        remain = int.from_bytes(remain, "big")

        # contains x and y data
        data = remain | ((line & 0b00000111) << 8)
        x = data >> 4            # first 7 bits
        y = float(data & 0xF)    # last 5 bits
        depth = x + y/10
        print("Depth: ", depth)

        self_obj.out_q.put("set_depth(" + str(depth) + ")")

        #         self.in_q.put(message)
