'''
 copyright 2014
 author: Spiridoula O'Regan
 email: roula.oregan@gmail.com
 github user: roulaoregan
'''
import logging
import math
import os
import random
import re
import sys

from collections import Counter
from optparse import OptionParser

'''
Handles file input errors
'''
class FileInputError(Exception):
        def __init__(self, value):
                self.value = value
        def __str__(self):
                return repr(self.value)
