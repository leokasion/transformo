#!/bin/bash
set -e

# Gran the UID/GID of the folder we are mounting
# This 'borrows' the identity of whoever owns the folder on the host
USER_ID=${PUID:-$(stat -c %u /app/uploads)}
GROUP_ID=${PGID:-$(stat -c %g /app/uploads)}

# Check if we are trying to map to root (UID 0)
if [ "$USER_ID" -eq 0 ]; then
    echo "Warning: Attempting to map to root. Skipping adjustment for security."
    exec gosu transformo "$@"
else
    echo "Adjusting transformo user to UID $USER_ID and GID $GROUP_ID..."
    # Modify the internal user to match
    usermod -u "$USER_ID" transformo
    groupmod -g "$GROUP_ID" transformo
    # Run the app as 'transformo' using gosu
    # This replaces the root proc (PID 1) with the Flask app

    # Ensure the user can write to the upload folder
    chown -R transformo:transformo /app/uploads
    # Ensure the user can read the output folder
    mkdir -p /app/outputs
    chown -R transformo:transformo /app/outputs
    exec gosu transformo "$@"
fi