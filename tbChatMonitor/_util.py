import sys
from datetime import datetime, timedelta


def convert_unix_to_utc(timestamp_ms):
    # Convert milliseconds since epoch to seconds since epoch
    timestamp_s = timestamp_ms / 1000.0
    # Convert to datetime object
    dt_object = datetime.utcfromtimestamp(timestamp_s)
    return dt_object


def compute_difference(unix_timestamp: int):
    # Convert the Unix timestamp to a datetime object
    timestamp_date = datetime.utcfromtimestamp(unix_timestamp)

    # Get the current time
    now = datetime.utcnow()

    # Compute the difference
    difference = now - timestamp_date
    if now < timestamp_date:
        difference = timestamp_date - now

    # Extract days, hours, and minutes
    days = difference.days
    hours, remainder = divmod(difference.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    return days, hours, minutes


def main():
    if len(sys.argv) != 2:
        print("Usage: python program_name.py <unix_timestamp>")
        sys.exit(1)

    try:
        unix_timestamp = int(sys.argv[1])
    except ValueError:
        print("Please provide a valid Unix timestamp.")
        sys.exit(1)

    days, hours, minutes = compute_difference(unix_timestamp)

    # Determine if the timestamp is in the past or future
    if datetime.utcnow() > datetime.utcfromtimestamp(unix_timestamp):
        print(f"{days} days, {hours} hours, and {minutes} minutes since the timestamp.")
    else:
        print(f"{days} days, {hours} hours, and {minutes} minutes until the timestamp.")


if __name__ == "__main__":
    main()
