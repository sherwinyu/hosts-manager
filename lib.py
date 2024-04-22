import logging
import sys
import datetime
import re
import subprocess

def parse_time_format(time_string):
    pattern = r"^(\d+)(m|s)?$"  # Optional unit group
    match = re.match(pattern, time_string)
    if match:
        number = int(match.group(1))
        unit = match.group(2) if match.group(2) else 'm'  # Default to 'm' if no unit is specified
        return (number, unit)
    return None


def setup_logging(log_filename, log_level=logging.INFO):
    """
    Sets up logging with both file and console handlers.

    Args:
        log_filename (str): The path to the log file.
        log_level (int): The logging level, e.g., logging.INFO, logging.DEBUG.
    """
    # Create a formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(filename)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Stream (console) handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)

    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger



def quit_application_with_confirmation(app_name):
    script = f'''
    tell application "System Events"
        display dialog "Are you sure you want to quit {app_name}?" buttons ["Yes", "No"] default button "No"
        if the button returned of the result is "Yes" then
            tell application "{app_name}" to quit
        end if
    end tell
    '''
    subprocess.run(["osascript", "-e", script])
