import pygame
import random

pygame.init()
Screen_Width, Screen_Height = 800, 600
Screen = pygame.display.set_mode((Screen_Width, Screen_Height))
pygame.display.set_caption("Solar Particle Collector")
White_Color = (255, 255, 255)
Black_Color = (0, 0, 0)
Player_Image = pygame.image.load("player.webp").convert_alpha()
player_width = Player_Image.get_rect().width // 2 #make player half its size
player_height = Player_Image.get_rect().height // 2
Player_Image = pygame.transform.scale(Player_Image, (player_width, player_height)) #resize image
Player_Rect = Player_Image.get_rect()
Player_X = Screen_Width // 2 - Player_Rect.width // 2
Player_Y = Screen_Height - 100
Player_Base_Speed = 5
Player_Speed = Player_Base_Speed
Particles = []
Particle_Size = 40
Particle_Speed = 1
Energy = 10
Time_Limit = 60
Start_Time = pygame.time.get_ticks()
Base_Spawn_Rate = 0.01
Max_Spawn_Rate = 0.03
Score_Multiplier = 1
Multiplier_Timer = 0
Font = pygame.font.Font(None, 36)
try:
    Collect_Sound = pygame.mixer.Sound("collect-ring.mp3")
except pygame.error:
    print("Error: Could not load sound file 'collect-ring.mp3'")
    Collect_Sound = None

shapes = ["circle", "square", "triangle"]
renewable_energies = {
    "circle": 1,
    "square": 2,
    "triangle": 4,
}
non_renewable_energies = {
    "circle": -1,
    "square": -2,
    "triangle": -4,
}

Power_Usage = 50
Max_Power_Usage = 100
Power_Drain = 1.5
Power_Regen = 3
Critical_Power = 10
renewable_collected = 0
non_renewable_collected = 0
game_time = 0
collected_text = None
collected_text_timer = 0

def create_particle():
    x = random.randint(0, Screen_Width - Particle_Size)
    shape = random.choice(shapes)
    non_renewable_prob = min(0.4, 0.1 + (game_time / 10000))
    if random.random() < non_renewable_prob and game_time > 5000:
        value = non_renewable_energies[shape]
        y = 0
        color = (255, 0, 0)
    else:
        value = renewable_energies[shape]
        y = random.randint(0, Screen_Height // 3)
        color = (0, 255, 0)

    Particles.append([x, y, shape, value, color, []])

def draw_particles():
    for Particle in Particles:
        for pos in Particle[5]:
            draw_shape(Particle[2], pos, Particle[4])
        draw_shape(Particle[2], (Particle[0], Particle[1]), Particle[4])

def draw_shape(shape, pos, color):
    x, y = pos
    if shape == "circle":
        pygame.draw.circle(Screen, color, (x, y), Particle_Size // 2)
    elif shape == "square":
        pygame.draw.rect(Screen, color, (x - Particle_Size // 2, y - Particle_Size // 2, Particle_Size, Particle_Size))
    elif shape == "triangle":
        pygame.draw.polygon(Screen, color, [(x, y - Particle_Size // 2), (x - Particle_Size // 2, y + Particle_Size // 2), (x + Particle_Size // 2, y + Particle_Size // 2)])

def draw_player():
    Screen.blit(Player_Image, (Player_X, Player_Y))

def draw_info():
    Energy_Text = Font.render(f"Energy: {Energy}", True, White_Color)
    Time_Remaining = Time_Limit - (pygame.time.get_ticks() - Start_Time) // 1000
    Time_Text = Font.render(f"Time: {Time_Remaining}", True, White_Color)
    Multiplier_Text = Font.render(f"Multiplier: {Score_Multiplier}x", True, White_Color)
    Power_Text = Font.render(f"Power: {int(Power_Usage)} / {Max_Power_Usage}", True, White_Color)
    Screen.blit(Energy_Text, (10, 10))
    Screen.blit(Time_Text, (Screen_Width - 100, 10))
    Screen.blit(Multiplier_Text, (Screen_Width // 2 - 70, 10))
    Screen.blit(Power_Text, (10, 50))
    if collected_text and pygame.time.get_ticks() - collected_text_timer < 250:
        Screen.blit(collected_text, (Player_X, Player_Y - 30))

def draw_background():
    for y in range(Screen_Height):
        color = (int(20 * y / Screen_Height), int(40 * y / Screen_Height), int(80 * y / Screen_Height))
        pygame.draw.line(Screen, color, (0, y), (Screen_Width, y))

Running = True
energy_timer = pygame.time.get_ticks()
energy_usage_interval = 1000
energy_usage = 1
clock = pygame.time.Clock()

while Running:
    moving = False
    game_time += clock.get_time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False

    Keys = pygame.key.get_pressed()
    if Keys[pygame.K_LEFT] and Player_X > 0:
        Player_X -= Player_Speed
        moving = True
    if Keys[pygame.K_RIGHT] and Player_X < Screen_Width - Player_Rect.width:
        Player_X += Player_Speed
        moving = True

    if moving:
        Power_Usage = max(0, Power_Usage - Power_Drain)
    else:
        if Power_Usage < Critical_Power:
            Power_Usage = min(Max_Power_Usage, Power_Usage + Power_Regen * 2)
        else:
            Power_Usage = min(Max_Power_Usage, Power_Usage + Power_Regen)

    Player_Speed = Player_Base_Speed * (1 + (Power_Usage / Max_Power_Usage * 1.5))
    Particle_Speed = min(3, 1 + game_time / 30000)

    draw_background()
    Elapsed_Time = (pygame.time.get_ticks() - Start_Time) / 1000
    Spawn_Rate = min(Base_Spawn_Rate + Elapsed_Time * 0.0005, Max_Spawn_Rate)
    if random.random() < Spawn_Rate:
        create_particle()
    draw_player()
    draw_particles()
    draw_info()

    Player_Rect.topleft = (Player_X, Player_Y)
    particles_to_remove = []
    for Particle in Particles:
        Particle[1] += Particle_Speed
        Particle[5].insert(0, (Particle[0], Particle[1]))
        if len(Particle[5]) > 5:
            Particle[5].pop()
        Particle_Rect_Particle = pygame.Rect(Particle[0], Particle[1], Particle_Size, Particle_Size)
        if Player_Rect.colliderect(Particle_Rect_Particle):
            if Particle[3] == 2:
                Score_Multiplier = min(Score_Multiplier + 1, 5)
                Multiplier_Timer = pygame.time.get_ticks()
            else:
                Energy += Particle[3] * Score_Multiplier
                if Collect_Sound:
                    pygame.mixer.Sound.play(Collect_Sound)
                if Particle[3] > 0:
                    collected_text = Font.render(f"+{Particle[3]*Score_Multiplier} (Renewable)", True, White_Color)
                else:
                    collected_text = Font.render(f"{Particle[3]*Score_Multiplier} (Non-Renewable)", True, White_Color)
                collected_text_timer = pygame.time.get_ticks()
            if Particle[3] > 0:
                renewable_collected += 1
            else:
                non_renewable_collected += 1
            particles_to_remove.append(Particle)
        elif Particle[1] > Screen_Height:
            particles_to_remove.append(Particle)
            Score_Multiplier = 1
    for particle in particles_to_remove:
        Particles.remove(particle)

    if pygame.time.get_ticks() - Multiplier_Timer > 2000:
        Score_Multiplier = 1
    if (pygame.time.get_ticks() - Start_Time) // 1000 > Time_Limit:
        Running = False
    if pygame.time.get_ticks() - energy_timer > energy_usage_interval:
        energy_timer = pygame.time.get_ticks()
        Energy -= energy_usage
        if Energy < 0:
            Energy = 0
    if Energy == 0:
        Running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

print(f"Final Energy: {Energy}")