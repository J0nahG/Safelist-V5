# Safelist V5 by J0nahG
A semi-automated safelisting program for the Celestia safelist.

Requires a Celestia API key.
Please visit https://api.duel.dev for more information about Celestia!

## Installation Instructions:
Create a virtual environment
```shell
python -m venv venv
```

Activate the environment
```shell
venv\Scripts\activate
```

Install the dependencies
```shell
pip install -r requirements.txt
```

## To Use:
* Run the program
* Select your log file
* Input your Celestia API key
* Play bedwars!
* Players will automatically be queued on final kill, but you can use the commands below to control exactly who gets safelisted

### Available Commands:
* /j add "player"     - Adds "player" to the safelist queue
* /j remove "player"  - Removes "player" from the safelist queue
* /j clear            - Clears the safelist queue
* /j show             - Shows the safelist queue on-screen
* /j hide             - Hides the safelist queue on-screen
* /j confirm          - Adds all players in the queue to the Celestia safelist
* /j user "player"    - Sets the current user to "player" (used for win detection)
* /j key "key"        - Sets Celestia API key to "key"
* /j auto             - Enables automatically safelisting players in the queue on game win
* /j manual           - Disables automatically safelisting players in the queue on game win
