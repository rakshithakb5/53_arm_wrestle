import math
import random
import pygame


class GameEngine:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.arm_position = 0.0
        self.target_limit = 100.0
        self.last_key = None
        
        self.stamina = 100.0
        self.max_stamina = 100.0

        # Task 3: exhaustion lockout (locks below 10, unlocks once stamina reaches 30)
        self.exhausted = False
        self.exhaust_threshold = 10.0
        self.recover_threshold = 30.0
        
        self.winner = None
        self.game_state = "PLAYING"
        self.ai_strength = 0.35

#timer: 
        self.match_start = pygame.time.get_ticks()
        self.match_time_ms = 0


        # Task 2: AI surge cycle  BUILDING -> SURGING -> EXHAUSTED -> BUILDING
        self.ai_state = "BUILDING"
        self.ai_state_start = pygame.time.get_ticks()
        self.ai_build_ms = 4000
        self.ai_surge_ms = 1500
        self.ai_exhaust_ms = 2000
        self.ai_multipliers = {"BUILDING": 1.0, "SURGING": 2.0, "EXHAUSTED": 0.3}
        
        self.font_big = pygame.font.SysFont(None, 44)
        self.font_med = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type == pygame.KEYDOWN:
            if self.exhausted:
                return
                
            if event.key == pygame.K_LEFT:
                if self.last_key != pygame.K_LEFT: 
                    self.arm_position -= 4.2
                    self.stamina = max(0.0, self.stamina - 6.0)
                    self.last_key = pygame.K_LEFT
            elif event.key == pygame.K_RIGHT:
                if self.last_key != pygame.K_RIGHT: 
                    self.arm_position -= 4.2
                    self.stamina = max(0.0, self.stamina - 6.0)
                    self.last_key = pygame.K_RIGHT

    def update(self):
        if self.game_state != "PLAYING":
            return

        # Task 2: advance the AI surge state machine using real elapsed time
        now = pygame.time.get_ticks()

        #timer:
        self.match_time_ms = now - self.match_start


        elapsed = now - self.ai_state_start
        if self.ai_state == "BUILDING" and elapsed >= self.ai_build_ms:
            self.ai_state, self.ai_state_start = "SURGING", now
        elif self.ai_state == "SURGING" and elapsed >= self.ai_surge_ms:
            self.ai_state, self.ai_state_start = "EXHAUSTED", now
        elif self.ai_state == "EXHAUSTED" and elapsed >= self.ai_exhaust_ms:
            self.ai_state, self.ai_state_start = "BUILDING", now

        ai_variance = random.uniform(0.3, 1.0)
        multiplier = self.ai_multipliers[self.ai_state]
        self.arm_position += self.ai_strength * ai_variance * multiplier

        if self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + 0.45)

        # Task 3: lock input below 10, unlock once stamina recovers to 30
        if self.stamina < self.exhaust_threshold:
            self.exhausted = True
        elif self.exhausted and self.stamina >= self.recover_threshold:
            self.exhausted = False

        if self.arm_position <= -self.target_limit:
            self.winner = "PLAYER"
            self.game_state = "GAME_OVER"
        elif self.arm_position >= self.target_limit:
            self.winner = "COMPUTER"
            self.game_state = "GAME_OVER"

    def reset(self):
        self.arm_position = 0.0
        self.stamina = 100.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"
        self.exhausted = False
        self.ai_state = "BUILDING"
        self.ai_state_start = pygame.time.get_ticks()
        #timer:
        self.match_start = pygame.time.get_ticks()
        self.match_time_ms = 0

    def render(self, screen):
        screen.fill((25, 28, 35))

#timer:
        timer_surf = self.font_med.render(
            f"TIME: {self.match_time_ms / 1000:.1f}s", True, (240, 240, 240)
        )
        screen.blit(timer_surf, (self.width // 2 - timer_surf.get_width() // 2, 58))



        title_surf = self.font_big.render("ARM WRESTLE SHOWDOWN", True, (240, 240, 240))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 12))

        player_header = self.font_med.render("PLAYER", True, (80, 160, 255))
        computer_header = self.font_med.render("COMPUTER", True, (255, 100, 80))
        screen.blit(player_header, (60, 55))
        screen.blit(computer_header, (self.width - 150, 55))


#timer:
        final_surf = self.font_med.render(
         f"Match time: {self.match_time_ms / 1000:.1f}s", True, (200, 200, 200)
        )
        screen.blit(
            final_surf,
            (self.width // 2 - final_surf.get_width() // 2, self.height // 2 + 45)
        )
        # Task 2: show the AI's current state under its header
        if self.ai_state == "SURGING":
            tag = self.font_med.render("SURGE!", True, (255, 200, 60))
            screen.blit(tag, (self.width - 150, 80))
        elif self.ai_state == "EXHAUSTED":
            tag = self.font_med.render("tired...", True, (150, 150, 170))
            screen.blit(tag, (self.width - 150, 80))

        table_rect = pygame.Rect(40, 100, self.width - 80, 310)
        pygame.draw.rect(screen, (110, 50, 15), table_rect, border_radius=14)
        pygame.draw.rect(screen, (70, 30, 8), table_rect, width=5, border_radius=14)

        pygame.draw.line(screen, (45, 18, 4), (self.width // 2, 100), (self.width // 2, 410), 4)

        offset_x = (self.arm_position / self.target_limit) * 95
        hand_x = (self.width // 2) + int(offset_x)
        hand_y = 235

        # Task 3: arm trembles while exhausted
        if self.exhausted:
            hand_x += random.randint(-4, 4)
            hand_y += random.randint(-4, 4)

        p_shoulder = (70, 330)
        p_elbow = (140, 215)
        c_shoulder = (self.width - 70, 330)
        c_elbow = (self.width - 140, 215)

        pygame.draw.line(screen, (200, 145, 110), p_shoulder, p_elbow, 32)
        pygame.draw.line(screen, (215, 160, 125), p_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (185, 130, 95), p_elbow, 18)

        pygame.draw.line(screen, (170, 110, 85), c_shoulder, c_elbow, 32)
        pygame.draw.line(screen, (185, 125, 95), c_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (150, 95, 70), c_elbow, 18)

        pygame.draw.circle(screen, (225, 175, 140), (hand_x, hand_y), 24)
        pygame.draw.circle(screen, (160, 115, 85), (hand_x, hand_y), 24, width=3)

        stamina_label = self.font_med.render("STAMINA", True, (220, 220, 220))
        screen.blit(stamina_label, (40, 445))

        stamina_bg = pygame.Rect(140, 448, 240, 22)
        stamina_fill = pygame.Rect(140, 448, int(240 * (self.stamina / self.max_stamina)), 22)
        pygame.draw.rect(screen, (45, 50, 60), stamina_bg, border_radius=6)
        bar_color = (60, 210, 100) if self.stamina > 25 else (220, 60, 60)
        pygame.draw.rect(screen, bar_color, stamina_fill, border_radius=6)

        # Task 3: flashing red bar + EXHAUSTED! label while locked out
        if self.exhausted:
            flash_on = (pygame.time.get_ticks() // 150) % 2 == 0
            if flash_on:
                pygame.draw.rect(screen, (255, 40, 40), stamina_bg, width=3, border_radius=6)
                pygame.draw.rect(screen, (255, 40, 40), stamina_fill, border_radius=6)
            warn = self.font_med.render("EXHAUSTED!", True, (255, 70, 70))
            screen.blit(warn, (400, 447))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            win_text = "PLAYER WINS THE MATCH!" if self.winner == "PLAYER" else "COMPUTER WINS!"
            color = (80, 240, 100) if self.winner == "PLAYER" else (240, 80, 80)
            text_surf = self.font_big.render(win_text, True, color)
            screen.blit(
                text_surf,
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 45)
            )

            restart_surf = self.font_med.render(
                "Press [R] to Rematch", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 10)
            )