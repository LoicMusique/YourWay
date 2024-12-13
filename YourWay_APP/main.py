import pygame
import sys
import os
import platform
import shutil

try:
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
except:
    pass

pygame.init()
pygame.mixer.init()
pygame.mixer_music.load("./appData/pop.mp3")
pygame.mixer_music.set_volume(0.5)
# Dimensions et couleurs
SCREEN_WIDTH, SCREEN_HEIGHT = 1360, 765
BACKGROUND_COLOR = (24, 0, 60)
TEXT_COLOR = (25, 20, 15)
LIGHT_TEXT_COLOR = (164, 159, 154)
BLUE = (71, 120, 215)
LIGHT_BLUE = (173, 216, 230)
RED = (220, 10, 42)
LIGHT_RED = (255, 99, 71)
WHITE = (250, 250, 250)
GREEN = (10, 150, 10)
LIGHT_GREEN = (60, 200, 60)
BUTTON_RADIUS= 20  # Rayon des bords arrondis des boutons

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("YourWay")
icon = pygame.image.load("./appData/Icon.png")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

font_text = pygame.font.Font(None, 36)
font_choices = pygame.font.Font(None, 28)

# Chargement des histoires
relative_path = "./storiesData"
StoriesNames = os.listdir(relative_path)
StoriesNames.sort()

def get_android_storage_root():
    if platform.system() == "Linux" and "ANDROID_STORAGE" in os.environ:
        # Retourne le chemin Android standard si on est sur un système Android
        return os.environ.get("EXTERNAL_STORAGE", "/storage/emulated/0")
    else:
        # Si ce n'est pas Android, on peut retourner None ou lever une exception
        return None

def create_app_folder(app_name):
    storage_root = get_android_storage_root()
    
    if not storage_root:
        # raise EnvironmentError("Cette fonction est prévue pour un système Android uniquement.")
        return None
    
    app_folder_path = os.path.join(storage_root, app_name)
    
    try:
        os.makedirs(app_folder_path, exist_ok=True)
        print(f"Dossier créé ou déjà existant : {app_folder_path}")
        return app_folder_path
    except Exception as e:
        print(f"Erreur lors de la création du dossier : {e}")
        return None

# Fonction pour dessiner un bouton avec bords arrondis
def draw_button(text, rect, font, color, hover_color):
    mouse_pos = pygame.mouse.get_pos()
    clicked = False
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, rect, border_radius=BUTTON_RADIUS)
        if pygame.mouse.get_pressed()[0]:
            clicked = True
            pygame.mixer_music.play()
    else:
        pygame.draw.rect(screen, color, rect, border_radius=BUTTON_RADIUS)
    
    text_surf = font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    
    return clicked

# Fonction pour dessiner le texte dans une boîte ajustable
def draw_text_box(text, rect, font, color=TEXT_COLOR, bgcolor=None):
    if bgcolor:
        pygame.draw.rect(screen, bgcolor, rect, border_radius=10)
    words = text.split(' ')
    lines, line = [], ""
    for word in words:
        test_line = f"{line} {word}".strip()
        if font.size(test_line)[0] < rect.width:
            line = test_line
        else:
            lines.append(line)
            line = word
    lines.append(line)
    
    y_offset = rect.y
    for line in lines:
        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (rect.x, y_offset))
        y_offset += text_surface.get_height()

# Fonction pour afficher une boîte de confirmation
def confirm_action(message):
    while True:
        screen.fill(BACKGROUND_COLOR)
        confirm_rect = pygame.Rect((SCREEN_WIDTH/2)-300, (SCREEN_HEIGHT)/5, 600, 200)
        draw_text_box(message, confirm_rect, font_text, bgcolor=LIGHT_BLUE)
        
        yes_button = pygame.Rect((SCREEN_WIDTH/3)-50, (SCREEN_HEIGHT)/4*3, 100, 50)
        no_button = pygame.Rect((SCREEN_WIDTH/3)*2-50, (SCREEN_HEIGHT)/4*3, 100, 50)
        
        if draw_button("Oui", yes_button, font_text, BLUE, LIGHT_BLUE):
            wait_for_mouse_release()
            return True
        if draw_button("Non", no_button, font_text, RED, LIGHT_RED):
            wait_for_mouse_release()
            return False
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# Fonction pour attendre le relâchement de la souris
def wait_for_mouse_release(max_wait: int=10):
    waiting = True
    step = 0
    while waiting and step < max_wait:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                waiting = False
        pygame.time.Clock().tick(30)
        step += 1

def copy_android_folders_to_relative(source_folder, relative_destination):
    # Définir le chemin absolu du répertoire relatif
    destination_folder = os.path.abspath(relative_destination)
    
    # Créer le dossier de destination s'il n'existe pas
    os.makedirs(destination_folder, exist_ok=True)
    
    # Lister les dossiers dans le dossier source
    for item in os.listdir(source_folder):
        source_item_path = os.path.join(source_folder, item)
        
        if os.path.isdir(source_item_path):  # Vérifie que c'est un dossier
            # Chemin complet du dossier de destination
            destination_item_path = os.path.join(destination_folder, item)
            
            try:
                # Copier le dossier
                shutil.copytree(source_item_path, destination_item_path, dirs_exist_ok=True)
                print(f"Copié : {source_item_path} -> {destination_item_path}")
            except Exception as e:
                print(f"Erreur lors de la copie de {source_item_path} : {e}")

# Fonction principale pour choisir et lancer une histoire
def main_menu(path_extern_data):
    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        title_rect = pygame.Rect(SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.1, SCREEN_WIDTH * 0.8, 50)
        draw_text_box("Histoires disponibles :", title_rect, font_text, WHITE)
        import_rect = pygame.Rect(SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.7, SCREEN_WIDTH * 0.8, 50)
        if draw_button("Recharger les histoire", import_rect, font_choices, GREEN, LIGHT_GREEN):
            wait_for_mouse_release()
            if path_extern_data:
                copy_android_folders_to_relative(path_extern_data, relative_path)
                global StoriesNames
                StoriesNames = os.listdir(relative_path)
                StoriesNames.sort()
            else:
                pass
        
        # Dynamiser la position des boutons pour les histoires
        for i, story in enumerate(StoriesNames):
            story_rect = pygame.Rect(SCREEN_WIDTH * 0.1, 150 + i * 60, SCREEN_WIDTH * 0.8, 40)
            if draw_button(story, story_rect, font_choices, BLUE, LIGHT_BLUE):
                wait_for_mouse_release()
                play_story(story)
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# Fonction pour jouer une histoire
def play_story(Story, StepName="START"):
    end_text = None  # Texte à afficher à la fin de l'histoire
    while True:
        text = ""
        choices, cPath = [], []
        
        with open(f"./storiesData/{Story}/{StepName}.sd") as StoryStep:
            for line in StoryStep.readlines():
                if line.startswith("T"):
                    text = line[2:]
                elif line[0] in "ABCDEFG":
                    choices.append(line[2:].strip())
                elif line[0].islower():
                    cPath.append(line[2:].strip())
        
        # Vérifier si l'étape est une fin
        if "END" in StepName:
            end_text = text
            break
        
        choice_made = False
        while not choice_made:
            screen.fill(BACKGROUND_COLOR)
            
            quit_button = pygame.Rect((SCREEN_WIDTH/2)-50, SCREEN_HEIGHT-80, 100, 40)
            if draw_button("Quitter", quit_button, font_text, RED, LIGHT_RED):
                if confirm_action("Voulez-vous retourner au menu principal ?"):
                    wait_for_mouse_release(5)
                    return
            
            text_rect = pygame.Rect(SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.1, SCREEN_WIDTH * 0.8, 200)
            draw_text_box(text, text_rect, font_text, bgcolor=LIGHT_BLUE)
            
            for i, choice in enumerate(choices):
                choice_rect = pygame.Rect(SCREEN_WIDTH * 0.1, 300 + i * 50, SCREEN_WIDTH * 0.8, 40)
                if draw_button(f"{choice}", choice_rect, font_choices, BLUE, LIGHT_BLUE):
                    wait_for_mouse_release()
                    StepName = cPath[i]
                    choice_made = True
                    break
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.unicode.isdigit():
                    selected = int(event.unicode) - 1
                    if 0 <= selected < len(choices):
                        StepName = cPath[selected]
                        choice_made = True
                        break
            clock.tick(30)
    
    # Affichage de la fin
    while True:
        screen.fill(BACKGROUND_COLOR)
        end_rect = pygame.Rect(SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.1, SCREEN_WIDTH * 0.8, 300)
        draw_text_box(end_text if end_text else "FIN !", end_rect, font_text, bgcolor=LIGHT_BLUE)
        
        restart_button = pygame.Rect(SCREEN_WIDTH * 0.1, 400, SCREEN_WIDTH * 0.8, 50)
        menu_button = pygame.Rect(SCREEN_WIDTH * 0.1, 470, SCREEN_WIDTH * 0.8, 50)
        
        if draw_button("Relancer l'histoire", restart_button, font_text, BLUE, LIGHT_BLUE):
            wait_for_mouse_release()
            play_story(Story, StepName="START")  # Recommence l'histoire depuis le début
            return
        
        if draw_button("Retourner au menu principal", menu_button, font_text, BLUE, LIGHT_BLUE):
            wait_for_mouse_release()
            return
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.unicode == '1':  # Relancer l'histoire
                    play_story(Story, StepName="START")
                    return
                elif event.unicode == '2':  # Retourner au menu principal
                    return
        clock.tick(30)

# Créer le dossier pour importer des histoires
storiesData_extern = create_app_folder("storiesData")
# Démarrer le programme
main_menu(storiesData_extern)
