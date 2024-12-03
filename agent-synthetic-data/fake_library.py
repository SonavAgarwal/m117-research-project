"""
Helper Library
==============

A collection of simple, commonly used utility functions to make everyday tasks easier.
"""


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to a HEX color code."""
    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        raise ValueError("RGB values must be in the range 0-255.")
    return f"#{r:02x}{g:02x}{b:02x}"


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5.0 / 9.0


def inches_to_centimeters(inches: float) -> float:
    """Convert inches to centimeters."""
    return inches * 2.54


def is_palindrome(s: str) -> bool:
    """Check if a given string is a palindrome."""
    s = ''.join(filter(str.isalnum, s)).lower(
    )  # Remove non-alphanumeric characters and lowercase
    return s == s[::-1]
