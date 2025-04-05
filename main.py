# -*- coding: utf-8 -*-
"""
Main script for the project.
Prints a welcome message including the current version.
"""

# --- Global Variables ---
# Using uppercase convention for global constants
PROGRAM_VERSION = "0.1.0"


# --- Functions ---
def display_welcome_message(version):
    """
    Prints the welcome message to the console.
    Args:
      version (str): The program version to display.
    """
    # Using an f-string for easy formatting
    message = f"Welcome! You are running version: {version}"
    print("-" * len(message))  # Optional: Print a line for visual separation
    print(message)
    print("-" * len(message))  # Optional: Print a line for visual separation


# --- Main Execution Block ---
if __name__ == "__main__":
    """
    This block runs only when the script is executed directly
    (not when imported as a module).
    """
    display_welcome_message(PROGRAM_VERSION)

    # You can add more code here later to start your program's logic
    # print("\nStarting main application logic...")
