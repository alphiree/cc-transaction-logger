import os


def update_env_file(key: str, value: str):
    """
    Update a value in the .env file

    Args:
        key (str): The environment variable name
        value (str): The new value to set
    """
    # Read the current .env file
    with open(".env", "r") as file:
        lines = file.readlines()

    # Update or add the key-value pair
    key_found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            key_found = True
            break

    # If key wasn't found, add it to the end
    if not key_found:
        lines.append(f"{key}={value}\n")

    # Write back to the .env file
    with open(".env", "w") as file:
        file.writelines(lines)

    # Also update the current environment
    os.environ[key] = value
