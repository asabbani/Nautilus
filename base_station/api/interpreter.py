

def decode_command(header_str, self_obj):
    if header == POSITION_DATA:
        # reads in remaining byte
        remain = self_obj.radio.read(2)
        remain = int.from_bytes(remain, "big")

        # contains x and y data
        data = remain | ((line & 0b00000111) << 16)

        x = (data >> 9)
        y = (data & 0b111111111)

        # TODO, call function and update positioning in gui

    elif header == HEADING_DATA:
        x
    elif header == VOLTAGE_DATA:
        x
    elif header == TEMP_DATA:
        x
    elif header == MOVEMENT_STAT_DATA:
        x
    elif header == MISSION_STAT_DATA:
        x
    elif header == FLOODED_DATA:
        x
    elif header == DEPTH_DATA:
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
