from werkzeug.local import Local, LocalManager

fc = Local()
global_manager = LocalManager([fc])