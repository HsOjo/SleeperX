# SleeperX

Native macOS menubar power/sleep manager for Hackintosh users.

* Auto sleep on low battery capacity.
* Auto disable sleep while on AC power.
* Disable idle sleep or lid sleep on demand (with timed auto-cancel).
* Lock the screen when the lid closes.

Event-driven (IOKit / NSWorkspace notifications), PyObjC-native, no polling.

> Requires **macOS 10.12 (Sierra) or later**.

* Multiple language support:
  * English
  * Simplified Chinese
  * Traditional Chinese
  * Japanese
  * Korean

## Privileged helper

Disabling lid sleep and changing the sleep (hibernate) mode require root, because
`pmset -a disablesleep` / `hibernatemode` have no public IOKit equivalent. SleeperX
installs a classic LaunchDaemon helper the first time you use these features. You
authorize it **once** with an admin password (nothing is stored). The helper only
runs a fixed, whitelisted set of `pmset` commands, gated by socket permissions and a
peer-uid check. Everything else (whole-machine sleep, display sleep, idle-sleep
prevention) runs without root.

## Downloads

Please see the [Releases Page](../../releases).

## First open (unsigned app)

SleeperX is distributed unsigned. On first launch Gatekeeper will refuse to open it.
Either **right-click the app → Open**, or clear the quarantine flag:

```bash
xattr -dr com.apple.quarantine /Applications/SleeperX.app
```

## How to build

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra build
uv run python build.py                   # produces dist/SleeperX.app and dist/SleeperX-<version>.zip
```

## Report a bug

Export the log (Preferences → Advanced Options), then attach it to a GitHub issue.
Private data is masked in the exported log.
