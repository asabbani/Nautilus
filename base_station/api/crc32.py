crc_divisor = 0x104c11db7


class Crc32():

    # create the crc 32 bytes
    def generate(message, lengthMessage):
        message = message << (31 - lengthMessage)
        remainder = message % crc_divisor
        message = message + remainder
        message = message & 0xFFFF
        return message

    # check is the crc32 bit

    def confirm(message):
        if message % crc_divisor == 0:
            return True
        else:
            return False
