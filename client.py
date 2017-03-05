#!/usr/bin/python

import base64
import hashlib
import sys
import time

from Crypto import Random
from Crypto.Cipher import AES

# The following command read stdin as a bytestream:
inBytes = sys.stdin.buffer.read()
# print(inBytes)
# outFile = open("pic.jpg","wb")
# outFile.write(inBytes)
# outFile.close()


