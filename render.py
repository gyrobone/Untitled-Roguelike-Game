import tcod as libtcod
from enum import Enum

from states.game_states import GameStates

from menu import inventory_menu, level_up_menu, character_screen

wall_tile = 256 
floor_tile = 257
player_tile = 258
orc_tile = 259
troll_tile = 260
scroll_tile = 261
healingpotion_tile = 262
sword_tile = 263
shield_tile = 264
stairsdown_tile = 265
dagger_tile = 266
blood_tile = 267


class RenderOrder(Enum):
    STAIRS = 1
    CORPSE = 2
    ITEM = 3
    ACTOR = 4


def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    names = [entity.name for entity in entities
             if entity.x == x and entity.y == y and libtcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)

    return names.capitalize()


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER,
                             '{0}: {1}/{2}'.format(name, value, maximum))


def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log,
                screen_width, screen_height, bar_width, panel_height, panel_y, mouse, colors,
                game_state):
    if fov_recompute:
        # Draw All Tiles in GameMap
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                # Render floor and wall tiles based on visibility
                if not visible:
                    #if it's not visible right now, the player can only see it if it's explored
                    if game_map.tiles[x][y].explored:
                        if wall:
                            # Wall Not Visible
                            libtcod.console_put_char_ex(con, x, y, wall_tile, libtcod.gray, libtcod.black)
                        else:
                            # Floor Not Visible
                            libtcod.console_put_char_ex(con, x, y, floor_tile, libtcod.gray, libtcod.black)
                else:
                    #it's visible
                    if wall:
                        # Wall Visible
                        libtcod.console_put_char_ex(con, x, y, wall_tile, libtcod.white, libtcod.dark_gray)
                    else:
                        # Floor Visible
                        libtcod.console_put_char_ex(con, x, y, floor_tile, libtcod.white, libtcod.dark_gray)
                        #since it's visible, explore it
                    game_map.tiles[x][y].explored = True


    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # Draw All Entities in List
    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map, game_map)

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Press the key next to an item to use it, or Esc to cancel.\n'
        else:
            inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'

        inventory_menu(con, inventory_title, player, 50, screen_width, screen_height)
    
    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(con, 'Level up! Choose a stat to raise:', player, 40, screen_width, screen_height)

    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, screen_width, screen_height)

    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    # Print the game messages, one line at a time
    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp,
               libtcod.light_red, libtcod.darker_red)

    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT,
                            'Dungeon Level: {0}'.format(game_map.dungeon_level))

    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                             get_names_under_mouse(mouse, entities, fov_map))

    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)

    
def draw_entity(con, entity, fov_map, game_map):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.tiles[entity.x][entity.y].explored):
        libtcod.console_set_default_foreground(con, libtcod.white)
        libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)
    elif entity.render_order == RenderOrder.CORPSE:
        clear_entity(con, entity)
        libtcod.console_put_char_ex(con, entity.x, entity.y, blood_tile, libtcod.gray, libtcod.black)
    elif game_map.tiles[entity.x][entity.y].explored and entity.item:
        libtcod.console_set_default_foreground(con, libtcod.white)
        libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_entity(con, entity):
    # Erase from Console
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)


'''
                if not visible:
                    #if it's not visible right now, the player can only see it if it's explored
                    if game_map.tiles[x][y].explored:
                        if wall:
                            # Wall Not Visible
                            libtcod.console_put_char_ex(con, x, y, wall_tile, libtcod.gray, libtcod.black)
                        else:
                            # Floor Not Visible
                            libtcod.console_put_char_ex(con, x, y, floor_tile, libtcod.gray, libtcod.black)
                else:
                    #it's visible
                    if wall:
                        # Wall Visible
                        libtcod.console_put_char_ex(con, x, y, wall_tile, libtcod.white, libtcod.dark_gray)
                    else:
                        # Floor Visible
                        libtcod.console_put_char_ex(con, x, y, floor_tile, libtcod.white, libtcod.dark_gray)
                        #since it's visible, explore it
                    game_map.tiles[x][y].explored = True
'''