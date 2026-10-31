#!/usr/bin/env bash
# Install Seconwind Help on a customer's Linux Mint machine.
#   sudo ./install.sh [customer-username]
# Puts the app in /opt/seconwind-help, adds "Seconwind Help" to the menu, and a desktop icon
# for the customer if a username is given. Works offline. Remove with uninstall.sh.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Please run with sudo." >&2; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/../dist/index.html"
[[ -f "$SRC" ]] || { echo "dist/index.html missing: run tools/build.py first." >&2; exit 1; }
DEST=/opt/seconwind-help
USER_NAME="${1:-${SUDO_USER:-}}"

install -d -m 755 "$DEST"
install -m 644 "$SRC" "$DEST/index.html"
install -m 644 "$HERE/seconwind-help.svg" "$DEST/seconwind-help.svg"

# Details shown on the help page and added to emails. Read-only facts, no personal data.
json_str() { python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1"; }
vendor="$(cat /sys/class/dmi/id/sys_vendor 2>/dev/null || true)"
product="$(cat /sys/class/dmi/id/product_name 2>/dev/null || true)"
version="$(cat /sys/class/dmi/id/product_version 2>/dev/null || true)"
[[ "${vendor,,}" == lenovo* && -n "$version" ]] && product="$version"
. /etc/os-release
cat > "$DEST/machine-info.js" <<JS
window.SECONWIND_MACHINE = {
  model: $(json_str "$(echo "$vendor $product" | xargs)"),
  os: $(json_str "${PRETTY_NAME:-Linux}"),
  hostname: $(json_str "$(hostname)"),
  installed: $(json_str "$(date +'%d %B %Y')")
};
JS
chmod 644 "$DEST/machine-info.js"

cat > /usr/share/applications/seconwind-help.desktop <<DESK
[Desktop Entry]
Type=Application
Name=Seconwind Help
Comment=Quick answers for your computer, and how to reach Michael
Exec=xdg-open $DEST/index.html
Icon=$DEST/seconwind-help.svg
Categories=Utility;Documentation;
Keywords=help;support;seconwind;question;
Terminal=false
DESK
chmod 644 /usr/share/applications/seconwind-help.desktop

if [[ -n "$USER_NAME" ]] && id "$USER_NAME" >/dev/null 2>&1; then
  desk="$(sudo -u "$USER_NAME" xdg-user-dir DESKTOP 2>/dev/null || echo "/home/$USER_NAME/Desktop")"
  if [[ -d "$desk" ]]; then
    install -m 755 -o "$USER_NAME" -g "$(id -gn "$USER_NAME")" /usr/share/applications/seconwind-help.desktop "$desk/seconwind-help.desktop"
    sudo -u "$USER_NAME" gio set "$desk/seconwind-help.desktop" metadata::trusted true 2>/dev/null || true
    echo "Desktop icon added for $USER_NAME."
  fi
fi
echo "Installed. Open it from the menu: Seconwind Help."
