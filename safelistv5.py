import tkinter as tk
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
import keyboard
import json
import re
import aiohttp
import asyncio


def replace_message(widget: tk.Text, message: str):
    """
    Deletes a widget's current text and replaces it with message.
    """
    widget.config(state="normal")
    widget.delete("1.0", "end")
    widget.insert("end", message)
    widget.config(state="disabled")

def add_line(widget: tk.Text, message: str):
    """
    Adds message content as a new line to a widget.
    """
    widget.config(state="normal")
    widget.insert("end", f"\n{message}")
    widget.config(state="disabled")

def clean_string(input_string: str):
    pattern = r'[^a-zA-Z0-9_]'
    parts = re.split(pattern, input_string, maxsplit=1)
    cleaned_string = parts[0]
    return cleaned_string


class Overlay():
    """
    A class to represent the overlay.
    """
    def __init__(self):
        self.root = tk.Tk()

        self.bg_color = "#000000"
        self.txt_color = "#00ffff"

        self.title = tk.Label(self.root, text="Safelist V5", font=("TkDefaultFont", 16, "bold"), bg=self.bg_color, fg=self.txt_color)
        self.title.grid(row=1, sticky="W")

        self.text = tk.Text(self.root, font=("TkDefaultFont", 12), bg=self.bg_color, fg=self.txt_color, bd=0, state="disabled")
        self.text.grid(row=4, sticky="W")

        self.queueDisplay = tk.Text(self.root, font=("TkDefaultFont", 12), bg=self.bg_color, fg=self.txt_color, bd=0, state="disabled", padx=5, pady=5)

        self.root.overrideredirect(True)  # Hide the window border and close button
        self.root.config(bg=self.bg_color)
        self.root.wm_attributes("-topmost", True)  # Keep the window always on top
        self.root.wm_attributes("-transparentcolor", self.bg_color)  # Set the transparent color

        self.root.after(0, self._initialize_logs)
        self.root.after(100, self._check_key_press)

    def run(self):
        """
        Runs the overlay.
        """
        self.root.mainloop()

    def test(self):
        """
        A method to test random crap.
        """
        pass

    def _initialize_logs(self):
        """
        Initializes the logs object.
        """
        self.logs = Log_File(self)
        if not self.logs.error:
            self.userDisplay = tk.Label(self.root, text=f"Playing as: {self.logs.user}", font=("TkDefaultFont", 16, "bold"), bg=self.bg_color, fg=self.txt_color)
            self.userDisplay.grid(row=2, sticky="W")
            self.root.after(250, self.logs.read_log_file)

    def _close_overlay(self):
        """
        Closes the overlay.
        """
        self.logs.event_loop.close()
        self.root.destroy()  # Close the window

    def _check_key_press(self):
        """
        Watches for keybind presses.
        """
        if keyboard.is_pressed('End'):
            self._close_overlay()
        else:
            self.root.after(100, self._check_key_press)


class Log_File():
    """
    A class to represent the log file.
    """
    def __init__(self, overlay: Overlay):
        self.overlay = overlay
        self.prefix = "j"
        self.command_pattern = f"Unknown command. Type \"/help\" for help. ('{self.prefix} "
        self.command_pattern2 = f"Unknown command. Type \"help\" for help. ('{self.prefix} "
        self.GameEndPatterns = ["Red -", "Blue -", "Green -", "Yellow -", "White -", "Pink -", "Aqua -", "Gray -"]
        self.settings = {}
        self.error = False
        self.auto = False
        self.event_loop = asyncio.new_event_loop()

        try:
            with open("safelist_settings.json", "r") as settingsFile:
                self.settings = json.load(settingsFile)

        except FileNotFoundError:
            self.settings = {}
            self.ask_for_log_file()
            self.ask_for_celestia_key()
            self.update_settings()

        except:
            print("An unknown error has occurred. (0001)")
            self.error = True
            self.overlay._close_overlay()

        if not self.error:
            try:
                self.logFilePath = self.settings['log_file']

            except KeyError:
                self.ask_for_log_file()
                self.update_settings()

            except:
                print("An unknown error has occurred. (0002)")
                self.error = True
                self.overlay._close_overlay()

        if not self.error:
            try:
                self.celestia_key = self.settings['celestia_key']

            except KeyError:
                self.ask_for_celestia_key()
                self.update_settings()

            except Exception as e:
                print("An unknown error has occurred. (0003)")
                self.error = True
                self.overlay._close_overlay()

        if not self.error:
            try:
                with open(self.logFilePath, "r") as logFile:
                    content = logFile.read()
                    userPattern = "Setting user: "
                    index = content.find(userPattern)

                    if index != -1:
                        next_space = content.find("\n", index + len(userPattern))
                        if next_space != -1:
                            self.user = clean_string(content[index + len(userPattern):next_space])
                        else:
                            self.user = "error"
                    else:
                        self.user = "error"

                    logFile.seek(0, 2)
                    self.logLocation = logFile.tell()

            except FileNotFoundError:
                print("Log file not found.")
                self.overlay._close_overlay()

            except:
                print("An unknown error has occurred. (0004)")
                self.error = True

            self.queue = Safelist_Queue(self)

    def ask_for_log_file(self):
        """
        Prompts the user to select a log file.
        """
        filetypes = (('Log files', '*.log'), ('All files', '*.*'))
        logFilePath = fd.askopenfile(title='Please select log file.', initialdir='/', filetypes=filetypes)
        if logFilePath:
            self.logFilePath = logFilePath.name
            self.settings['log_file'] = self.logFilePath
        else:
            print("No log file selected.")
            self.overlay._close_overlay()

    def ask_for_celestia_key(self):
        """
        Prompts the user to input their Celestia API key.
        """
        user_input = sd.askstring("Safelist V5", "Please input Celestia API key:")
        if user_input:
            self.celestia_key = user_input.strip()
            self.settings['celestia_key'] = self.celestia_key
        else:
            print("No Celestia API key provided.")
            self.overlay._close_overlay()

    def update_settings(self):
        """
        Updates the settings file.
        """
        with open("safelist_settings.json", 'w') as settingsFile:
            json.dump(self.settings, settingsFile)

    def read_log_file(self):
        """
        Reads any new lines in the log file and sets self.lines to the list of new lines.
        """
        try:
            with open(self.logFilePath, "r") as logFile:
                logFile.seek(self.logLocation)
                newLines = []
                timeStampPattern = r'^\[\d{2}:\d{2}:\d{2}\]'
                while True:
                    newLine = logFile.readline()
                    if newLine == "":
                        self.logLocation = logFile.tell()
                        formatted_lines = []
                        for line in newLines:
                            formatted_line = self.format_line(line)
                            if formatted_line:
                                formatted_lines.append(formatted_line)
                        self.lines = formatted_lines
                        break

                    elif bool(re.match(timeStampPattern, newLine)):
                        if "[CHAT] " in newLine:
                            newLines.append(newLine)

                    else:
                        try:
                            newLines[-1] = f"{newLines[-1].rstrip()} {newLine.lstrip()}"
                        except:
                            pass

        except FileNotFoundError:
            print("Invalid log file.")
            self.overlay._close_overlay()

        except:
            print("An unknown error has occured. (0005)")
            self.overlay._close_overlay()

        for line in self.lines:
            self._check_events(line)

        self.overlay.root.after(250, self.read_log_file)

    def format_line(self, line: str):
        """
        Returns a formatted line.
        """
        lines = line.split("[CHAT] ", 1)
        if len(lines) >= 1:
            formatted_line = lines[1].strip()
            formatted_line = re.sub(r"(?i)§[0-9A-FK-OR]", "", formatted_line)
            return formatted_line
        else:
            return False

    def _check_events(self, line: str):
        """
        Checks for events in line.
        """
        command = False # Allows checking multiple invalid command patterns since hypixel can't make up their mind.

        if line.endswith("FINAL KILL!"):
            # Final Kill
            player = clean_string(line.split(" ")[0])
            self.event_loop.run_until_complete(self.addPlayer(player))

        elif line == "Protect your bed and destroy the enemy beds.":
            # Game start
            self.queue.clear()

        elif line.startswith("You are now nicked as "):
            ign = clean_string(line.replace("You are now nicked as ", "", 1).rstrip("!"))
            self.setuser(ign)

        elif line.strip() == "Your nick has been reset!":
            try:
                with open(self.logFilePath, "r") as logFile:
                    content = logFile.read()
                    userPattern = "Setting user: "
                    index = content.find(userPattern)

                    if index != -1:
                        next_space = content.find("\n", index + len(userPattern))
                        if next_space != -1:
                            ign = clean_string(content[index + len(userPattern):next_space])

            except:
                ign = "error"

            self.setuser(ign)

        elif line.startswith(self.command_pattern):
            command = line[len(self.command_pattern):-2]

        elif line.startswith(self.command_pattern2):
            command = line[len(self.command_pattern2):-2]

        else:
            for pattern in self.GameEndPatterns:
                if line.startswith(pattern):
                    line = line.replace(pattern, "", 1)
                    winners = [clean_string(i.split()[-1]) for i in line.split(',')]

                    if self.user in winners:
                        for winner in winners:
                            self.queue.remove(winner)
                        if self.auto:
                            self.queue.confirm()

                    else:
                        self.queue.clear()
                    break

        if command:
            if command.startswith("clear"):
                self.queue.clear()

            elif command.startswith("add"):
                ign = clean_string(command.replace("add ", "", 1).strip())
                self.event_loop.run_until_complete(self.addPlayer(ign))

            elif command.startswith("remove"):
                ign = clean_string(command.replace("remove ", "", 1).strip())
                self.queue.remove(ign)

            elif command.startswith("show"):
                self.queue.show()

            elif command.startswith("hide"):
                self.queue.hide()

            elif command.startswith("confirm"):
                self.queue.confirm()

            elif command.startswith("user"):
                ign = clean_string(command.replace("user ", "", 1).strip())
                self.setuser(ign)

            elif command.startswith("key"):
                key = command.replace("key", "", 1).strip()
                print(key)
                self.celestia_key = key
                self.settings["celestia_key"] = key
                self.update_settings()

            elif command.startswith("auto"):
                self.auto = True

            elif command.startswith("manual"):
                self.auto = False

            elif command.startswith("kill"):
                self.overlay._close_overlay()

    def setuser(self, ign):
        """
        Sets the user.
        """
        self.user = ign
        self.overlay.userDisplay.config(text=f"Playing as: {self.user}")

    async def addPlayer(self, ign):
        """
        Gets a player's UUID from minecraftservices API.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.minecraftservices.com/minecraft/profile/lookup/name/" + ign) as response:
                    data = await response.json()
                    if response.status == 200:
                        self.queue.add(data)
                    else:
                        print(f"No UUID found for {ign}.")
        except:
            print(f"An error occured while fetching UUID for {ign}")


class Safelist_Queue():
    """
    A class to represent the safelist queue.
    """
    def __init__(self, Log_File: Log_File):
        self.log_file = Log_File
        self.overlay = self.log_file.overlay
        self.key = self.log_file.celestia_key
        self.queue = {}
        self.clear()

    def add(self, playerData: dict):
        """
        Adds a player to the safelist queue.
        """
        player = {playerData["name"].lower():playerData}
        self.queue.update(player)
        self.refresh()

    def remove(self, ign):
        """
        Removes a player from the safelist queue.
        """
        if ign.lower() in self.queue.keys():
            del self.queue[ign.lower()]
            self.refresh()

    def clear(self):
        """
        Clears the safelist queue.
        """
        self.queue.clear()
        replace_message(self.overlay.queueDisplay, "Queued players:")

    def show(self):
        """
        Shows the players currently in the safelist queue.
        """
        self.overlay.queueDisplay.grid(row=3, sticky="W")

    def hide(self):
        """
        Hides the players currently in the safelist queue.
        """
        self.overlay.queueDisplay.grid_forget()

    def refresh(self):
        """
        Refreshes the on-screen display of the safelist queue.
        """
        replace_message(self.overlay.queueDisplay, "Queued players:")
        for player in self.queue.keys():
            add_line(self.overlay.queueDisplay, self.queue[player]['name'])

    def confirm(self):
        """
        Adds players in the safelist queue to the Celestia safelist.
        """
        data = []
        for player in self.queue.keys():
            data.append({'uuid': self.queue[player]['id'], 'type': 'safe'})
        self.log_file.event_loop.run_until_complete(self.safelistWorker(data))
        self.clear()

    async def safelistWorker(self, payload: list):
        """
        Worker for adding players to the Celestia safelist.
        """
        headers = {'Api-Key': self.key}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(f'https://api.duel.dev/lists/add', json=payload) as response:
                data = await response.json()
                if response.status != 200:
                    print("An error occured while trying to add players to the Celestia safelist.")



overlay = Overlay()
overlay.run()
