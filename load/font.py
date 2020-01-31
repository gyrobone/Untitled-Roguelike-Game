import tcod as libtcod


def load_customfont():
    #The index of the first custom tile in the file
    a = 256
 
    #The "y" is the row index, here we load the sixth row in the font file. Increase the "6" to load any new rows from the file
    for y in range(5,6):
        libtcod.console_map_ascii_codes_to_font(a, 32, 0, y)
        a += 32