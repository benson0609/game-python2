import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random

COOLDOWN_TIME = 1000  # 冷却时间，单位为毫秒
KNOCKBACK_DISTANCE = 20  # 击退距离

class BattleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Battle Game")

        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="white")
        self.canvas.pack()

        # 加载并调整玩家图片大小
        player1_original_image = Image.open("player1.png")
        player2_original_image = Image.open("player2.png")

        # 将图片缩小到 100x100 像素（可根据需要调整）
        self.image_size = 100
        player1_resized_image = player1_original_image.resize((self.image_size, self.image_size), Image.ANTIALIAS)
        player2_resized_image = player2_original_image.resize((self.image_size, self.image_size), Image.ANTIALIAS)

        self.player1_image = ImageTk.PhotoImage(player1_resized_image)
        self.player2_image = ImageTk.PhotoImage(player2_resized_image)

        # 设置玩家初始位置在底部
        self.player1 = self.canvas.create_image(50, 300, image=self.player1_image, anchor='nw')
        self.player2 = self.canvas.create_image(500, 300, image=self.player2_image, anchor='nw')

        self.player1_health = 100
        self.player2_health = 100

        self.player1_health_text = self.canvas.create_text(75, 20, text="Player 1 Health: 100", fill="blue", font=('Helvetica', '12', 'bold'))
        self.player2_health_text = self.canvas.create_text(525, 20, text="Player 2 Health: 100", fill="red", font=('Helvetica', '12', 'bold'))

        self.player1_cooldown_text = self.canvas.create_text(75, 40, text="Player 1 Cooldown: 0", fill="blue", font=('Helvetica', '12', 'bold'))
        self.player2_cooldown_text = self.canvas.create_text(525, 40, text="Player 2 Cooldown: 0", fill="red", font=('Helvetica', '12', 'bold'))

        self.gravity = 2
        self.on_ground = {self.player1: True, self.player2: True}  # Initially, both players are on the ground

        self.attack_cooldowns = {self.player1: 0, self.player2: 0}  # 初始化冷却时间

        self.root.bind("<KeyPress>", self.key_press)
        self.update_positions()

        self.auto_move_opponent()
        self.reduce_cooldowns()

    def key_press(self, event):
        key = event.keysym

        if key == "a":
            self.move_player(self.player1, -10, 0)
        elif key == "d":
            self.move_player(self.player1, 10, 0)
        elif key == "w" and self.on_ground[self.player1]:
            self.move_player(self.player1, 0, -30)  # Jump
        elif key == "space":
            self.attack(self.player1)

    def move_player(self, player, dx, dy):
        new_pos = self.canvas.coords(player)
        new_pos[0] += dx
        new_pos[1] += dy

        if self.check_boundary(new_pos) and not self.will_collide(player, new_pos):
            self.canvas.move(player, dx, dy)
            self.on_ground[player] = False  # Reset ground status because of the move

    def check_boundary(self, pos):
        return 0 <= pos[0] <= 600 - self.image_size and 0 <= pos[1] <= 400 - self.image_size

    def will_collide(self, player, new_pos):
        other_player = self.player1 if player == self.player2 else self.player2
        pos2 = self.canvas.coords(other_player)
        player_bbox = (new_pos[0], new_pos[1], new_pos[0] + self.image_size, new_pos[1] + self.image_size)
        other_bbox = (pos2[0], pos2[1], pos2[0] + self.image_size, pos2[1] + self.image_size)
        
        return (player_bbox[2] > other_bbox[0] and player_bbox[0] < other_bbox[2] and
                player_bbox[3] > other_bbox[1] and player_bbox[1] < other_bbox[3])

    def attack(self, attacker):
        if self.attack_cooldowns[attacker] <= 0:
            if self.is_colliding(self.player1, self.player2):
                if attacker == self.player1:
                    self.player2_health -= 10
                    self.update_health(self.player2_health_text, self.player2_health, "Player 2")
                    self.knockback(self.player2, self.player1)
                    if self.player2_health <= 0:
                        messagebox.showinfo("Battle Game", "Player 1 wins!")
                        self.root.quit()
                else:
                    self.player1_health -= 10
                    self.update_health(self.player1_health_text, self.player1_health, "Player 1")
                    self.knockback(self.player1, self.player2)
                    if self.player1_health <= 0:
                        messagebox.showinfo("Battle Game", "Player 2 wins!")
                        self.root.quit()
            self.attack_cooldowns[attacker] = COOLDOWN_TIME  # 重置攻击冷却时间

    def knockback(self, victim, attacker):
        pos_victim = self.canvas.coords(victim)
        pos_attacker = self.canvas.coords(attacker)
        
        dx = KNOCKBACK_DISTANCE if pos_victim[0] < pos_attacker[0] else -KNOCKBACK_DISTANCE
        new_pos_victim = [pos_victim[0] + dx, pos_victim[1]]

        # 检查边界和碰撞
        if self.check_boundary(new_pos_victim) and not self.will_collide(victim, new_pos_victim):
            self.canvas.move(victim, dx, 0)
        else:  # 如果检测到冲突或边界问题，则适当调整位移
            if not self.check_boundary(new_pos_victim):
                if new_pos_victim[0] < 0:
                    dx = -pos_victim[0]
                elif new_pos_victim[0] > 600 - self.image_size:
                    dx = 600 - self.image_size - pos_victim[0]
            if self.will_collide(victim, new_pos_victim):
                dx = 0  # 避免碰撞时不进行移动
            self.canvas.move(victim, dx, 0)
        
        self.on_ground[victim] = False  # 重置地面状态

    def is_colliding(self, player1, player2):
        pos1 = self.canvas.bbox(player1)
        pos2 = self.canvas.bbox(player2)
        return not (pos1[2] < pos2[0] or pos1[0] > pos2[2] or pos1[3] < pos2[1] or pos1[1] > pos2[3])

    def update_health(self, health_text, health, player):
        self.canvas.itemconfig(health_text, text=f"{player} Health: {health}")

    def update_cooldown(self, cooldown_text, cooldown, player):
        self.canvas.itemconfig(cooldown_text, text=f"{player} Cooldown: {max(0, cooldown // 100)}")

    def apply_gravity(self, player):
        pos = self.canvas.coords(player)
        if pos[1] < 400 - self.image_size:  # 检查是否在地面上方
            self.canvas.move(player, 0, self.gravity)
            self.on_ground[player] = False
        else:
            # 调整位置确保玩家不会超出地面
            if pos[1] > 400 - self.image_size:
                self.canvas.move(player, 0, 400 - self.image_size - pos[1])
            self.on_ground[player] = True

    def update_positions(self):
        self.apply_gravity(self.player1)
        self.apply_gravity(self.player2)
        self.root.after(50, self.update_positions)
    
    def auto_move_opponent(self):
        # Simple AI for player2
        pos1 = self.canvas.coords(self.player1)
        pos2 = self.canvas.coords(self.player2)
        dx, dy = 0, 0

        if pos2[0] < pos1[0]:
            dx = 5
        elif pos2[0] > pos1[0]:
            dx = -5
        
        if random.random() < 0.1 and self.on_ground[self.player2]:
            dy = -30  # Random jump

        self.move_player(self.player2, dx, dy)
        
        # Attack if colliding with player1
        if self.is_colliding(self.player1, self.player2):
            self.attack(self.player2)

        self.root.after(200, self.auto_move_opponent)
    
    def reduce_cooldowns(self):
        for player in self.attack_cooldowns:
            if self.attack_cooldowns[player] > 0:
                self.attack_cooldowns[player] -= 50  # 减少冷却时间
            cooldown_text = self.player1_cooldown_text if player == self.player1 else self.player2_cooldown_text
            player_name = "Player 1" if player == self.player1 else "Player 2"
            self.update_cooldown(cooldown_text, self.attack_cooldowns[player], player_name)

        self.root.after(50, self.reduce_cooldowns)

if __name__ == "__main__":
    root = tk.Tk()
    game = BattleGame(root)
    root.mainloop()
