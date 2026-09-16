# Browser & Chrome Interaction Rule

1. **NEVER attempt to launch a new Chrome process or open new Chrome browser instances** (e.g. via `browser_subagent` or direct CLI calls like `open -a "Google Chrome"`). Doing so causes Google Chrome to open the multi-profile selector popup ("Quem está usando o Chrome?"), which interrupts the user.
2. **Always reuse the already open Google Chrome window** belonging to the user's active profile (`ghcastellano@gmail.com`).
3. **To reload or activate the dossier page in Chrome**, use AppleScript to find the existing tab matching `processocamilacaruso` or `localhost:3000` and reload that tab in the existing window:
   ```bash
   osascript -e '
   tell application "Google Chrome"
       repeat with w in windows
           repeat with t in tabs of w
               set u to URL of t
               if u contains "processocamilacaruso" or u contains "localhost:3000" then
                   reload t
               end if
           end repeat
       end repeat
   end tell
   '
   ```
4. **Never create redundant tabs or windows.** Keep interactions strictly confined to existing open tabs.
