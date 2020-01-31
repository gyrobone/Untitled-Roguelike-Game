import shelve
import os
import simpleaudio as sa

from map_objects.game_map import GameMap

save_path = 'saves\\'
isdir = os.path.isdir(save_path)
if not isdir:
    try:
        os.mkdir(save_path)
    except OSError:
        print('Creation of the directort %s failed.' % save_path)
    else:
        print('Successfully created the directory %s.' % save_path)


def save_game(player, entities, game_map, message_log, game_state):
    with shelve.open('saves\\savegame', 'n') as data_file:
        data_file['player_index'] = entities.index(player)
        data_file['entities'] = entities
        data_file['game_map'] = game_map
        data_file['message_log'] = message_log
        data_file['game_state'] = game_state


def load_game():
    if not os.path.isfile('saves\\savegame.dat'):
        raise FileNotFoundError

    with shelve.open('saves\\savegame', 'r') as data_file:
        player_index = data_file['player_index']
        entities = data_file['entities']
        game_map = data_file['game_map']
        message_log = data_file['message_log']
        game_state = data_file['game_state']

    player = entities[player_index]

    return player, entities, game_map, message_log, game_state