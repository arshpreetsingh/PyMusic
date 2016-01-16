import glob
import os
import sys

import pygame

DEFAULT_VOLUME = 0.5


# Supported  Formats

FILE_TYPES = [
    '*.mid',
    '*.midi',
    '*.ogg',
    '*.mp3',
    '*.wav',
]


def init(frequency=22050, size=-16, channels=2, buffersize=4096):
    """ initialization of pygame """
    
    pygame.init()
    pygame.mixer.pre_init(frequency, size, channels, buffersize)


def read_dirs(dirs=['.'], file_types=FILE_TYPES):
    """ Retrun list of directories in list"""
    
    if not dirs:
        dirs.append('.')
    song_files = []
    for dir in dirs:
        for file_type in file_types:
            pattern = os.path.join(dir, file_type)
            names = glob.glob(pattern)
            #print 'names',names
            song_files.extend(names)
    return song_files


def play_window(args=[]):
    
    """Interface of Music Player. """
    
    init()
   
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((500,100))
    screen_rect = screen.get_rect()
    font = pygame.font.SysFont('Verdana', 11)
    bright = pygame.Color('gold')
    dim = pygame.Color('gold4')
    bgcolor = pygame.Color('black')
    caption = '(+/-) Volume | (Up/Down) Song | (Right/Left) Skip'
    pygame.display.set_caption(caption)
    
    names = []
   
    for arg in args:
        if os.path.isdir(arg):
            names.extend(read_dirs([arg]))
        else:
            names.append(arg)
    for name in names:
        if not os.access(name, os.R_OK):
            print 'cannot read', name
            quit()
    
    volume_bar = screen.get_rect()
    volume_bar.height = 8
    volume_bar.width -= 4
    volume_bar.topleft = 2,2
    volume_level = pygame.Rect(volume_bar)
    volume_level.inflate_ip(-2, -2)
    volume_color1 = pygame.Color('gold1')
    volume_color2 = pygame.Color('gold3')
    
    namei = -1
    name = names[namei]
    next_song = +1
    delay = 0
    song_queue = ['']*3
    volume = int(DEFAULT_VOLUME * 1000)
    pygame.mixer.music.set_volume(volume/1000.0)
    song_rect = pygame.Rect(0,0,1,1)
    
    while True:
        
        # song logic
        
        if delay > 0:
            # ticks between songs
            delay -= 1
        elif next_song:
            # switch song
            namei += next_song
            if namei >= len(names):
                quit()
            try:
                name = names[namei]
                pygame.mixer.music.load(name)
                pygame.mixer.music.play()
                next_song = 0
            
            except:
				print "Music file  "+ str(name) + " is not Supported"
				
                #print "Supported types are" 
                #print FILE_TYPES            
            
            # make the display
            for i in xrange(3):
                txti = namei + i - 1
                if txti < 0 or txti >= len(names):
                    txt = '---'
                else:
                    txt = names[txti]
                song_queue[i] = font.render(txt, 1, [dim,bright,dim][i])
        elif not pygame.mixer.music.get_busy():
            # trigger auto switch
            next_song = +1
            delay = 40
        
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN: # any keyboard key pressed by user
				
                # will work both on + as well as for =
                
                if e.key == pygame.K_PLUS or e.key == pygame.K_EQUALS:
                    if volume < 1000:
                        volume += 25
                        pygame.mixer.music.set_volume(volume/1000.0)
                
                elif e.key == pygame.K_MINUS:
                    if volume > 0:
                        volume -= 25
                        pygame.mixer.music.set_volume(volume/1000.0)
                
                elif e.key == pygame.K_UP:
                    if namei > 0:
                        next_song = -1
                
                elif e.key == pygame.K_DOWN:
                    if namei < len(names) - 1:
                        next_song = +1
                
                # Forward Song
                
                elif e.key == pygame.K_RIGHT:
                    try:
                        pos = pygame.mixer.music.get_pos() # get Current position of song
                        pygame.mixer.music.set_pos(pos + 10000) # Add 10000
                    except:
                        pass
                
                # Reverse song
                
                elif e.key == pygame.K_LEFT:
                    try:
                        pos = pygame.mixer.music.get_pos()
                        pygame.mixer.music.set_pos(pos - 10000)
                    except:
                        pass
                elif e.key == pygame.K_ESCAPE:
                    quit()
            elif e.type == pygame.QUIT:
                quit()
        
        # draw screen
        
        screen.fill(bgcolor)
        
        # volume bar
        volume_level.w = volume_bar.w * (volume/1000.0) - 1
        pygame.draw.rect(screen, volume_color2, volume_bar, 1)
        screen.fill(volume_color1, volume_level)
        
        # songs
        font_height = font.get_height()
        x = 2
        y = 2 + volume_bar.h + 2
        
        # elapsed time
        if pygame.mixer.music.get_busy():
            sec = pygame.mixer.music.get_pos() / 1000
            h = sec / 60 / 60
            m = (sec - h*60*60) / 60
            s = sec - h*60*60 - m*60
            txt = '{0}:{1:02d}:{2:02d}'.format(h, m, s)
            img = font.render(txt, 1, bright)
            screen.blit(img, (x,y))
        y += font_height + 2
        
        # song queue
        for img in song_queue:
            song_rect.topleft = x,y
            song_rect.size = img.get_size()
            if song_rect.right > screen_rect.right:
                song_rect.right = screen_rect.right
            screen.blit(img, song_rect)
            y += font_height + 2
        
        pygame.display.flip()
        clock.tick(10)


if __name__ == '__main__':

    """

For single Music file: 

$ python music.py

To play all files from Directory:  

$ python music.py "/home/metal-machine/Videos/kirtan/files"

    """
    if len(sys.argv) > 1:
        args = sys.argv[1:]
    else:
        args = [s.rstrip() for s in sys.stdin]
    play_window(args)
