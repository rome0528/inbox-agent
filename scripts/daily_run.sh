#!/bin/zsh
# Daily unattended agent run, started by launchd (see scripts/com.inboxagent.daily.plist).
# Output goes to logs/agent.log; a macOS notification appears if the run fails.
cd "${0:A:h}/.." || exit 1
echo "=== $(date '+%Y-%m-%d %H:%M:%S %z')"
.venv/bin/python -W ignore src/agent.py --max 200 < /dev/null
code=$?
if [[ $code -ne 0 ]]; then
  osascript -e "display notification \"Daily run failed (exit $code). See logs/agent.log\" with title \"Inbox agent\""
fi
exit $code
