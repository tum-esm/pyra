import os
import psutil

processes = [p.name() for p in psutil.process_iter()]
print(sorted(processes))

for e in ["opus.exe", "OpusCore.exe"]:
    if e in processes:
        exit_code = os.system(f"taskkill /f /im {e}")
        assert exit_code == 0, f"taskkill  of '{e}' ended with an exit_code of {exit_code}"
