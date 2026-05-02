import pygame
import random
import math
from enum import Enum


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3


class CardState(Enum):
    BACK = 0
    FLIPPING_TO_FRONT = 1
    FRONT = 2
    FLIPPING_TO_BACK = 3
    MATCHED = 4


class ShapeType:
    CIRCLE = 0
    SQUARE = 1
    TRIANGLE = 2
    DIAMOND = 3
    STAR = 4
    HEART = 5
    CROSS = 6
    RING = 7


SHAPE_COLORS = [
    (220, 20, 60),
    (255, 140, 0),
    (255, 215, 0),
    (34, 139, 34),
    (30, 144, 255),
    (75, 0, 130),
    (255, 105, 180),
    (0, 128, 128),
]

SHAPE_NAMES = [
    "红色圆形",
    "橙色方形",
    "黄色星形",
    "绿色三角",
    "蓝色菱形",
    "紫色心形",
    "粉色十字",
    "青色圆环",
]

FLIP_DURATION = 0.4


def draw_shape(surface, shape_type, color, center_x, center_y, size):
    if shape_type == ShapeType.CIRCLE:
        pygame.draw.circle(surface, color, (center_x, center_y), size // 2)
        pygame.draw.circle(surface, (50, 50, 50), (center_x, center_y), size // 2, 2)
    
    elif shape_type == ShapeType.SQUARE:
        half = size // 2
        rect = pygame.Rect(center_x - half, center_y - half, size, size)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (50, 50, 50), rect, 2)
    
    elif shape_type == ShapeType.TRIANGLE:
        half = size // 2
        points = [
            (center_x, center_y - half),
            (center_x - half, center_y + half),
            (center_x + half, center_y + half),
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (50, 50, 50), points, 2)
    
    elif shape_type == ShapeType.DIAMOND:
        half = size // 2
        points = [
            (center_x, center_y - half),
            (center_x + half, center_y),
            (center_x, center_y + half),
            (center_x - half, center_y),
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (50, 50, 50), points, 2)
    
    elif shape_type == ShapeType.STAR:
        points = []
        for i in range(10):
            angle = i * 36 - 90
            rad = math.radians(angle)
            radius = size // 2 if i % 2 == 0 else size // 4
            x = center_x + math.cos(rad) * radius
            y = center_y + math.sin(rad) * radius
            points.append((int(x), int(y)))
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (50, 50, 50), points, 2)
    
    elif shape_type == ShapeType.HEART:
        points = []
        for angle in range(360):
            rad = math.radians(angle)
            x = 16 * (math.sin(rad) ** 3)
            y = -(13 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad))
            scale = size / 35
            x = int(center_x + x * scale)
            y = int(center_y + y * scale)
            points.append((x, y))
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (50, 50, 50), points, 2)
    
    elif shape_type == ShapeType.CROSS:
        half = size // 2
        thickness = size // 5
        pygame.draw.rect(surface, color, (center_x - thickness // 2, center_y - half, thickness, size))
        pygame.draw.rect(surface, color, (center_x - half, center_y - thickness // 2, size, thickness))
        pygame.draw.rect(surface, (50, 50, 50), (center_x - thickness // 2, center_y - half, thickness, size), 2)
        pygame.draw.rect(surface, (50, 50, 50), (center_x - half, center_y - thickness // 2, size, thickness), 2)
    
    elif shape_type == ShapeType.RING:
        pygame.draw.circle(surface, color, (center_x, center_y), size // 2, size // 4)
        pygame.draw.circle(surface, (50, 50, 50), (center_x, center_y), size // 2, 2)
        pygame.draw.circle(surface, (50, 50, 50), (center_x, center_y), size // 4, 2)


def create_chinese_font(size, bold=False):
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/Library/Fonts/SimHei.ttf",
        "/Library/Fonts/Microsoft YaHei.ttf",
    ]
    
    for font_path in font_paths:
        try:
            font = pygame.font.Font(font_path, size)
            test_text = font.render("测试中文", True, (0, 0, 0))
            if test_text.get_width() > 0 and test_text.get_width() < 500:
                return font
        except:
            continue
    
    try:
        font_names = [
            "PingFang SC", "Hiragino Sans GB", "Heiti SC", "STHeiti",
            "Microsoft YaHei", "SimHei", "WenQuanYi Micro Hei", "Noto Sans CJK SC"
        ]
        for font_name in font_names:
            try:
                font = pygame.font.SysFont(font_name, size, bold=bold)
                test_text = font.render("测试", True, (0, 0, 0))
                if test_text.get_width() > 10:
                    return font
            except:
                continue
    except:
        pass
    
    return pygame.font.Font(None, size)


class Card:
    def __init__(self, x, y, width, height, shape_type, pattern_index):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.shape_type = shape_type
        self.pattern_index = pattern_index
        self.state = CardState.BACK
        self.flip_start_time = 0
        self.is_matched = False
        self.rect = pygame.Rect(x, y, width, height)
    
    def start_flip_to_front(self, current_time):
        if self.state == CardState.BACK:
            self.state = CardState.FLIPPING_TO_FRONT
            self.flip_start_time = current_time
            return True
        return False
    
    def start_flip_to_back(self, current_time):
        if self.state == CardState.FRONT:
            self.state = CardState.FLIPPING_TO_BACK
            self.flip_start_time = current_time
            return True
        return False
    
    def set_matched(self):
        self.state = CardState.MATCHED
        self.is_matched = True
    
    def update(self, current_time):
        if self.state == CardState.FLIPPING_TO_FRONT:
            elapsed = (current_time - self.flip_start_time) / 1000.0
            if elapsed >= FLIP_DURATION:
                self.state = CardState.FRONT
        
        elif self.state == CardState.FLIPPING_TO_BACK:
            elapsed = (current_time - self.flip_start_time) / 1000.0
            if elapsed >= FLIP_DURATION:
                self.state = CardState.BACK
    
    def get_flip_progress(self, current_time):
        if self.state in [CardState.FLIPPING_TO_FRONT, CardState.FLIPPING_TO_BACK]:
            elapsed = (current_time - self.flip_start_time) / 1000.0
            return min(elapsed / FLIP_DURATION, 1.0)
        return 0.0
    
    def is_showing_front(self, current_time):
        if self.state == CardState.FRONT or self.state == CardState.MATCHED:
            return True
        if self.state == CardState.FLIPPING_TO_FRONT:
            progress = self.get_flip_progress(current_time)
            return progress > 0.5
        if self.state == CardState.FLIPPING_TO_BACK:
            progress = self.get_flip_progress(current_time)
            return progress < 0.5
        return False
    
    def draw(self, screen, colors, current_time):
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        shape_size = min(self.width, self.height) - 20
        
        showing_front = self.is_showing_front(current_time)
        
        if self.state == CardState.MATCHED:
            progress = self.get_flip_progress(current_time) if hasattr(self, 'flip_start_time') else 1.0
            scale_width = 1.0
            
            if self.state == CardState.MATCHED and hasattr(self, 'match_animation_start'):
                match_elapsed = (current_time - self.match_animation_start) / 1000.0
                if match_elapsed < 0.5:
                    scale_width = 1.0 - 0.1 * math.sin(match_elapsed * math.pi * 4)
            
            draw_width = int(self.width * scale_width)
            draw_x = center_x - draw_width // 2
            draw_rect = pygame.Rect(draw_x, self.y, draw_width, self.height)
            
            pygame.draw.rect(screen, colors["matched_card_bg"], draw_rect, border_radius=8)
            pygame.draw.rect(screen, colors["matched_card_border"], draw_rect, 3, border_radius=8)
            
            if showing_front:
                faded_color = tuple(int(c * 0.6) for c in SHAPE_COLORS[self.shape_type])
                draw_shape(screen, self.shape_type, faded_color, center_x, center_y, int(shape_size * scale_width))
        
        elif showing_front:
            progress = self.get_flip_progress(current_time)
            if progress > 0:
                if self.state == CardState.FLIPPING_TO_FRONT:
                    scale_width = abs(math.cos(progress * math.pi))
                else:
                    scale_width = abs(math.cos(progress * math.pi))
                
                if scale_width < 0.05:
                    scale_width = 0.05
                
                draw_width = int(self.width * scale_width)
                draw_x = center_x - draw_width // 2
                draw_rect = pygame.Rect(draw_x, self.y, draw_width, self.height)
                
                pygame.draw.rect(screen, colors["card_bg"], draw_rect, border_radius=8)
                pygame.draw.rect(screen, colors["card_border"], draw_rect, 3, border_radius=8)
                
                if scale_width > 0.3:
                    shape_scale = min(scale_width * 2, 1.0)
                    draw_shape(screen, self.shape_type, SHAPE_COLORS[self.shape_type], 
                              center_x, center_y, int(shape_size * shape_scale))
            else:
                pygame.draw.rect(screen, colors["card_bg"], self.rect, border_radius=8)
                pygame.draw.rect(screen, colors["card_border"], self.rect, 3, border_radius=8)
                draw_shape(screen, self.shape_type, SHAPE_COLORS[self.shape_type], center_x, center_y, shape_size)
        
        else:
            progress = self.get_flip_progress(current_time)
            if progress > 0:
                scale_width = abs(math.cos(progress * math.pi))
                if scale_width < 0.05:
                    scale_width = 0.05
                
                draw_width = int(self.width * scale_width)
                draw_x = center_x - draw_width // 2
                draw_rect = pygame.Rect(draw_x, self.y, draw_width, self.height)
                
                pygame.draw.rect(screen, colors["card_back"], draw_rect, border_radius=8)
                pygame.draw.rect(screen, colors["card_back_border"], draw_rect, 3, border_radius=8)
            else:
                pygame.draw.rect(screen, colors["card_back"], self.rect, border_radius=8)
                pygame.draw.rect(screen, colors["card_back_border"], self.rect, 3, border_radius=8)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos) and self.state == CardState.BACK


class Button:
    def __init__(self, x, y, width, height, text, font, colors, callback=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.colors = colors
        self.callback = callback
        self.is_hovered = False
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, screen):
        bg_color = self.colors["button_hover"] if self.is_hovered else self.colors["button_bg"]
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, self.colors["button_border"], self.rect, 3, border_radius=10)
        
        text_color = self.colors["button_text_hover"] if self.is_hovered else self.colors["button_text"]
        
        try:
            text_surface = self.font.render(self.text, True, text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
        except:
            pass
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class UIManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.shapes = list(range(8))
        
        self.colors = {
            "bg": (255, 248, 220),
            "title": (139, 69, 19),
            "text": (101, 67, 33),
            "card_back": (70, 130, 180),
            "card_back_border": (47, 79, 79),
            "card_back_text": (255, 255, 255),
            "card_bg": (255, 250, 240),
            "card_border": (210, 180, 140),
            "matched_card_bg": (220, 220, 220),
            "matched_card_border": (169, 169, 169),
            "matched_text": (150, 150, 150),
            "button_bg": (255, 215, 0),
            "button_hover": (255, 193, 7),
            "button_border": (205, 133, 63),
            "button_text": (139, 69, 19),
            "button_text_hover": (85, 107, 47),
            "info_bg": (255, 240, 245),
            "info_border": (221, 160, 221)
        }
        
        self.cards = []
        self.start_button = None
        self.restart_button = None
        self.moves = 0
        self.start_time = 0
        self.end_time = 0
        self.game_state = GameState.MENU
        self.current_time = 0
        
        self._init_fonts()
    
    def _init_fonts(self):
        try:
            self.title_font = create_chinese_font(48, bold=True)
            self.subtitle_font = create_chinese_font(24)
            self.text_font = create_chinese_font(18)
            self.button_font = create_chinese_font(28, bold=True)
        except:
            self.title_font = pygame.font.Font(None, 64)
            self.subtitle_font = pygame.font.Font(None, 32)
            self.text_font = pygame.font.Font(None, 24)
            self.button_font = pygame.font.Font(None, 36)
    
    def _render_text(self, font, text, color):
        try:
            return font.render(text, True, color)
        except:
            return font.render("?", True, color)
    
    def init_menu(self):
        self.game_state = GameState.MENU
        center_x = self.screen_width // 2
        button_width = 200
        button_height = 60
        button_x = center_x - button_width // 2
        button_y = self.screen_height - 150
        
        self.start_button = Button(
            button_x, button_y, button_width, button_height,
            "开始游戏", self.button_font, self.colors,
            callback=self.start_game
        )
    
    def start_game(self):
        self.game_state = GameState.PLAYING
        self.moves = 0
        self.start_time = pygame.time.get_ticks()
        self.end_time = 0
        
        card_width = 80
        card_height = 100
        margin_x = 30
        margin_y = 40
        start_x = (self.screen_width - (4 * card_width + 3 * margin_x)) // 2
        start_y = 100
        
        shape_pairs = []
        for i, shape_type in enumerate(self.shapes):
            shape_pairs.append((shape_type, i))
            shape_pairs.append((shape_type, i))
        
        random.shuffle(shape_pairs)
        
        self.cards = []
        for row in range(4):
            for col in range(4):
                index = row * 4 + col
                shape_type, pattern_idx = shape_pairs[index]
                x = start_x + col * (card_width + margin_x)
                y = start_y + row * (card_height + margin_y)
                card = Card(x, y, card_width, card_height, shape_type, pattern_idx)
                self.cards.append(card)
    
    def init_game_over(self):
        self.game_state = GameState.GAME_OVER
        self.end_time = self.current_time
        center_x = self.screen_width // 2
        button_width = 200
        button_height = 60
        button_x = center_x - button_width // 2
        button_y = self.screen_height - 150
        
        self.restart_button = Button(
            button_x, button_y, button_width, button_height,
            "重新开始", self.button_font, self.colors,
            callback=self.start_game
        )
    
    def draw_menu(self, screen):
        screen.fill(self.colors["bg"])
        
        title_text = "记忆翻牌游戏"
        title = self._render_text(self.title_font, title_text, self.colors["title"])
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title, title_rect)
        
        instructions = [
            "游戏说明：",
            "1. 这是一个经典的记忆翻牌游戏",
            "2. 点击卡片翻转，寻找相同的图案",
            "3. 每次只能翻开两张卡片",
            "4. 图案相同则配对成功，卡片保持翻开",
            "5. 图案不同则短暂显示后翻回",
            "6. 用最少的步数和时间完成游戏！"
        ]
        
        y_offset = 160
        for i, line in enumerate(instructions):
            if i == 0:
                text_surface = self._render_text(self.subtitle_font, line, self.colors["title"])
            else:
                text_surface = self._render_text(self.text_font, line, self.colors["text"])
            screen.blit(text_surface, (50, y_offset))
            y_offset += 35
        
        legend_y = y_offset + 20
        legend_title = self._render_text(self.subtitle_font, "8种不同图案：", self.colors["title"])
        screen.blit(legend_title, (50, legend_y))
        
        legend_start_y = legend_y + 35
        for i in range(8):
            row = i // 4
            col = i % 4
            x = 80 + col * 130
            y = legend_start_y + row * 40
            
            pygame.draw.rect(screen, (255, 255, 255), (x - 5, y - 5, 30, 30), border_radius=4)
            pygame.draw.rect(screen, (200, 200, 200), (x - 5, y - 5, 30, 30), 2, border_radius=4)
            
            draw_shape(screen, i, SHAPE_COLORS[i], x + 10, y + 10, 20)
            
            name_text = self._render_text(self.text_font, SHAPE_NAMES[i], self.colors["text"])
            screen.blit(name_text, (x + 35, y))
        
        if self.start_button:
            self.start_button.draw(screen)
    
    def draw_playing(self, screen):
        screen.fill(self.colors["bg"])
        
        for card in self.cards:
            card.update(self.current_time)
            card.draw(screen, self.colors, self.current_time)
        
        info_bg = pygame.Rect(20, self.screen_height - 60, self.screen_width - 40, 40)
        pygame.draw.rect(screen, self.colors["info_bg"], info_bg, border_radius=8)
        pygame.draw.rect(screen, self.colors["info_border"], info_bg, 2, border_radius=8)
        
        elapsed_time = (self.current_time - self.start_time) // 1000
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        
        moves_text = self._render_text(self.text_font, f"步数: {self.moves}", self.colors["text"])
        time_str = f"时间: {minutes:02d}:{seconds:02d}"
        time_text = self._render_text(self.text_font, time_str, self.colors["text"])
        
        screen.blit(moves_text, (40, self.screen_height - 52))
        screen.blit(time_text, (self.screen_width - 160, self.screen_height - 52))
    
    def draw_game_over(self, screen):
        screen.fill(self.colors["bg"])
        
        title = self._render_text(self.title_font, "恭喜获胜！", self.colors["title"])
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title, title_rect)
        
        elapsed_time = (self.end_time - self.start_time) // 1000
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        
        stats = [
            f"总步数: {self.moves}",
            f"总耗时: {minutes} 分 {seconds} 秒"
        ]
        
        y_offset = 200
        for stat in stats:
            text_surface = self._render_text(self.subtitle_font, stat, self.colors["text"])
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 60
        
        tips = [
            "尝试用更少的步数完成游戏吧！",
            "记忆力会越来越好的！"
        ]
        
        y_offset = 350
        for tip in tips:
            text_surface = self._render_text(self.text_font, tip, self.colors["text"])
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 35
        
        if self.restart_button:
            self.restart_button.draw(screen)
    
    def draw(self, screen):
        self.current_time = pygame.time.get_ticks()
        
        if self.game_state == GameState.MENU:
            self.draw_menu(screen)
        elif self.game_state == GameState.PLAYING:
            self.draw_playing(screen)
        elif self.game_state == GameState.GAME_OVER:
            self.draw_game_over(screen)
    
    def handle_mouse_click(self, pos):
        if self.game_state == GameState.MENU:
            if self.start_button and self.start_button.is_clicked(pos):
                self.start_button.callback()
                return True
        elif self.game_state == GameState.PLAYING:
            for card in self.cards:
                if card.is_clicked(pos):
                    return card
        elif self.game_state == GameState.GAME_OVER:
            if self.restart_button and self.restart_button.is_clicked(pos):
                self.restart_button.callback()
                return True
        return None
    
    def handle_mouse_motion(self, pos):
        if self.game_state == GameState.MENU:
            if self.start_button:
                self.start_button.check_hover(pos)
        elif self.game_state == GameState.GAME_OVER:
            if self.restart_button:
                self.restart_button.check_hover(pos)
    
    def is_game_complete(self):
        return all(card.state == CardState.MATCHED for card in self.cards)
    
    def get_elapsed_seconds(self):
        return (self.current_time - self.start_time) // 1000
