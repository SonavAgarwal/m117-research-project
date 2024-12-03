def is_palindrome(s: str) -> bool:
    """Check if a given string is a palindrome."""
    s = ''.join(filter(str.isalnum, s)).lower(
    )  # Remove non-alphanumeric characters and lowercase
    return s == s[::-1]
