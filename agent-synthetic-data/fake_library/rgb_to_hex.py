def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to a HEX color code."""
    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        raise ValueError("RGB values must be in the range 0-255.")
    return f"#{r:02x}{g:02x}{b:02x}"
