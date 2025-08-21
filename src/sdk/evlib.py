import sys

if sys.platform in ("win32", "cygwin", "cli"):
    import winloop as _evlib
elif sys.platform in ("linux", "linux2", "darwin"):
    import uvloop as _evlib
else:
    raise ValueError(f"Unsupported platform: {sys.platform}")

new_event_loop = _evlib.new_event_loop
Loop = _evlib.Loop
install = _evlib.install
run = _evlib.run
EventLoopPolicy = _evlib.EventLoopPolicy
cancel_all_tasks = _evlib._cancel_all_tasks

# Alias for external use
_evlib_name = sys.modules[__name__]


__all__ = ("new_event_loop", "Loop", "install", "run", "EventLoopPolicy", "cancel_all_tasks")