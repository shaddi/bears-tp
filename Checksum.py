import binascii

# Assumes last field is the checksum!
def validate_checksum(message):
    try:
        msg,reported_checksum = message.rsplit('|',1)
        msg += '|'
        return generate_checksum(msg) == reported_checksum
    except:
        return False

# Assumes message does NOT contain final checksum field. Message MUST end
# with a trailing '|' character.
def generate_checksum(message):
    return str(binascii.crc32(message) & 0xffffffff)
