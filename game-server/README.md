Simple multi-threaded and -player'd cookie-throwing game implemented over a custom protocol.

Win the game by hitting other players with your stash of cookies.

Running the server:
1. Have Python 3+ on your path
2. Modify the server.config as needed
3. python bootstrap.py

Some protocol definitions:

- `WSP` : whitespace
- `EOL` : WSP* CRLF`
- `TILE` : [-]DIGIT+
- `DIR` : (UP | DOWN | LEFT | RIGHT) | (U | D | L | R)

Requests the player can make:

- `LOGIN WSP player EOL` : log in as player
- `MOVE WSP DIR EOL` : move in a direction
- `THROW WSP DIR EOL` : throw in a direction
- `MSG WSP (player | all) WSP message EOL` : message another player (or all of them)

Responses you'll get from the server:

- `200 WSP map_x, map_y EOL` : the column and row count, respectively, of the game map
- `100 WSP [player] message EOL` : a message from the server
- `101 WSP player, winning message EOL` : player won the game
- `102 WSP map_x1, map_y1, map_x2, map_y2, TILE, TILE, ..., EOL` : one of several messages describing the tile layout of the map
- `103 WSP cookie, map_x, map_y, DIR EOL` : a cookie's coordinates as it is flying
- `104 WSP player, map_x, map_y, cookie_count EOL` : a player's coordinates with their cookie count
- `400 message EOL` : user error