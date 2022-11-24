"""
A package for working with laboratory equipment
"""
from .scanner import Scanner, BaseAxes, Position, Velocity, Deceleration, Acceleration
from .scanner import ScannerConnectionError, ScannerInternalError, ScannerMotionError
