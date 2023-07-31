from stem import Signal
from stem.control import Controller

import subprocess
import time

class TorController:
    def __init__(self, tor_exe_path: str, control_port: str="9051") -> None:
        print("Starting Tor...")
        self.tor_exe_path = tor_exe_path
        self.tor_process = subprocess.Popen([self.tor_exe_path, "--controlport", control_port])
        time.sleep(5)
        print("Tor started.\n")

    def renew_tor_connection(self) -> None:
        print("Renewing Tor connection...")
        try:
            # Connect to the Tor control port
            with Controller.from_port(port=9051) as controller: # type: ignore
                controller.authenticate()
                controller.set_options({
                    "ExitNodes": "{US}",
                })
                controller.signal(Signal.NEWNYM) # type: ignore
            
            time.sleep(5)
            print("Tor connection renewed.\n")
        except Exception as e:
            print(f"Error renewing Tor connection: {e}\n\n")
            exit()

    def close(self) -> None:
        print("Closing Tor...")
        try:
            self.tor_process.kill()
            print("Tor closed.\n")
        except Exception as e:
            print(f"Error closing Tor: {e}\n\n")
            exit()