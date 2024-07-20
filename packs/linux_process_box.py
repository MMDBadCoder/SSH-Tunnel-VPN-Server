import os
import signal
import psutil


def kill_processes(pids):
    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
            print(f"Successfully killed process with PID {pid}")
        except ProcessLookupError:
            print(f"No such process with PID {pid}")
        except PermissionError:
            print(f"Permission denied to kill process with PID {pid}")
        except Exception as e:
            print(f"Failed to kill process with PID {pid}: {e}")


def get_child_pids_recursive(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        child_pids = [child.pid for child in children]
        return child_pids
    except psutil.NoSuchProcess:
        return []


def kill_all_os_process_of_pack(pack):
    pid_list = get_child_pids_recursive(pack.session_pid)
    pid_list.append(pack.session_pid)
    kill_processes(pid_list)
