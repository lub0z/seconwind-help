#!/usr/bin/env bash
# Remove Seconwind Help.   sudo ./uninstall.sh [customer-username]
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Please run with sudo." >&2; exit 1; }
rm -f /usr/share/applications/seconwind-help.desktop
rm -rf /opt/seconwind-help
USER_NAME="${1:-${SUDO_USER:-}}"
if [[ -n "$USER_NAME" ]]; then
  desk="$(sudo -u "$USER_NAME" xdg-user-dir DESKTOP 2>/dev/null || echo "/home/$USER_NAME/Desktop")"
  rm -f "$desk/seconwind-help.desktop"
fi
echo "Removed."
