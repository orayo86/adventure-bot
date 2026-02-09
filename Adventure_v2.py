import time
import random
import json
import os
from enum import Enum

class SkillType(Enum):
    SLASH = "Slash"
    POWER_STRIKE = "Power Strike"
    MAGIC_BOLT = "Magic Bolt"
    HEAL = "Heal"
    POISON_STRIKE = "Poison Strike"
    ARROW_SHOT = "Arrow Shot"
    MULTI_SHOT = "Multi Shot"

class StatusEffect:
    def __init__(self, nama, tipe, nilai, durasi):
        self.nama = nama
        self.tipe = tipe
        self.nilai = nilai
        self.durasi = durasi

class Potion:
    def __init__(self, nama, harga, hp_restore=0, effect=None):
        self.nama = nama
        self.harga = harga
        self.hp_restore = hp_restore
        self.effect = effect

class Bomb:
    def __init__(self, nama, harga, damage):
        self.nama = nama
        self.harga = harga
        self.damage = damage

class Weapon:
    def __init__(self, nama, harga, attack_bonus):
        self.nama = nama
        self.harga = harga
        self.attack_bonus = attack_bonus

class Armor:
    def __init__(self, nama, harga, defense_bonus):
        self.nama = nama
        self.harga = harga
        self.defense_bonus = defense_bonus

class Character:
    def __init__(self, nama, role="Warrior", hp=100, mp=50, attack=10, defense=5, magic=8, agility=7):
        self.nama = nama
        self.role = role
        self.level = 1
        self.exp = 0
        self.exp_max = 100
        
        self.hp = hp
        self.hp_max = hp
        self.mp = mp
        self.mp_max = mp
        self.attack = attack
        self.defense = defense
        self.magic = magic
        self.agility = agility
        
        self.gold = 0
        self.potions = {}
        self.bombs = {}
        self.equipped_weapon = None
        self.equipped_armor = None
        self.weapon_inventory = []
        self.armor_inventory = []
        self.bomb_inventory = []
        self.skills = [SkillType.SLASH]
        self.status_effects = []
        
    def apply_status_effect(self, effect):
        self.status_effects.append(effect)
    
    def reduce_status_effects(self):
        for effect in self.status_effects[:]:
            effect.durasi -= 1
            if effect.durasi <= 0:
                self.status_effects.remove(effect)
    
    def get_damage_multiplier(self):
        """Hitung multiplier damage dari status effect"""
        multiplier = 1.0
        for effect in self.status_effects:
            if effect.nama == "rage" and effect.tipe == "buff":
                multiplier += effect.nilai / 100
        return multiplier
    
    def get_damage_reduction(self):
        """Hitung reduction damage dari status effect"""
        reduction = 1.0
        for effect in self.status_effects:
            if effect.nama == "weaken" and effect.tipe == "debuff":
                reduction -= effect.nilai / 100
        return max(0.1, reduction)
    
    def take_damage(self, damage):
        reduced_damage = max(1, damage - self.defense // 2)
        reduced_damage = int(reduced_damage * self.get_damage_reduction())
        self.hp -= reduced_damage
        return reduced_damage
    
    def use_mp(self, amount):
        if self.mp >= amount:
            self.mp -= amount
            return True
        return False
    
    def restore_mp(self, amount):
        self.mp = min(self.mp_max, self.mp + amount)
    
    def restore_hp(self, amount):
        self.hp = min(self.hp_max, self.hp + amount)
    
    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_max:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.exp = 0
        self.exp_max = int(self.exp_max * 1.2)
        
        self.hp_max += 15
        self.mp_max += 10
        self.attack += 3
        self.defense += 2
        self.magic += 2
        self.agility += 1
        
        self.hp = self.hp_max
        self.mp = self.mp_max
        
        print(f"\n✨ LEVEL UP! {self.nama} sekarang level {self.level}!")
        
    def show_status(self):
        print(f"\n{'='*50}")
        print(f"👤 {self.nama.upper()} ({self.role}) - Level {self.level}")
        print(f"{'='*50}")
        print(f"❤️  HP: {self.hp}/{self.hp_max}")
        print(f"✨ MP: {self.mp}/{self.mp_max}")
        print(f"⚔️  Attack: {self.attack}  🛡️  Defense: {self.defense}")
        print(f"🔮 Magic: {self.magic}  ⚡ Agility: {self.agility}")
        print(f"💰 Gold: {self.gold}")
        if self.status_effects:
            print(f"\n📊 Status Effects:")
            for effect in self.status_effects:
                print(f"  - {effect.nama} ({effect.durasi} turns)")
        if self.equipped_weapon:
            print(f"\n🗡️  Weapon: {self.equipped_weapon.nama} (+{self.equipped_weapon.attack_bonus} ATK)")
        if self.equipped_armor:
            print(f"🛡️  Armor: {self.equipped_armor.nama} (+{self.equipped_armor.defense_bonus} DEF)")
        print(f"📚 Skills: {', '.join([s.value for s in self.skills])}")
        if self.potions:
            print(f"\n🧪 Potions:")
            for nama, jumlah in self.potions.items():
                print(f"  - {nama}: {jumlah}x")
        if self.bombs:
            print(f"\n💣 Bombs:")
            for nama, jumlah in self.bombs.items():
                print(f"  - {nama}: {jumlah}x")
        print(f"{'='*50}\n")

class Enemy:
    def __init__(self, nama, hp, attack, defense, magic, gold_drop, exp_drop, level=1):
        self.nama = nama
        self.hp = hp
        self.hp_max = hp
        self.attack = attack
        self.defense = defense
        self.magic = magic
        self.gold_drop = gold_drop
        self.exp_drop = exp_drop
        self.level = level
        self.skills = [SkillType.SLASH, SkillType.POWER_STRIKE]
        self.status_effects = []
    
    def apply_status_effect(self, effect):
        self.status_effects.append(effect)
    
    def reduce_status_effects(self):
        for effect in self.status_effects[:]:
            effect.durasi -= 1
            if effect.durasi <= 0:
                self.status_effects.remove(effect)
    
    def get_damage_reduction(self):
        reduction = 1.0
        for effect in self.status_effects:
            if effect.nama == "weaken":
                reduction -= effect.nilai / 100
        return max(0.1, reduction)
    
    def take_damage(self, damage):
        reduced_damage = max(1, damage - self.defense // 2)
        reduced_damage = int(reduced_damage * self.get_damage_reduction())
        self.hp -= reduced_damage
        return reduced_damage
    
    def show_status(self):
        status_str = f"👹 {self.nama} - Level {self.level}"
        if self.status_effects:
            status_str += " ["
            for effect in self.status_effects:
                status_str += f"{effect.nama}({effect.durasi}) "
            status_str += "]"
        print(status_str)
        print(f"HP: {self.hp}/{self.hp_max} | Attack: {self.attack}")

class Battle:
    def __init__(self, players, enemies):
        self.players = players if isinstance(players, list) else [players]
        self.enemies = enemies if isinstance(enemies, list) else [enemies]
        self.turn = 0
        self.current_player_idx = 0
    
    def calculate_damage(self, attacker, skill_type=SkillType.SLASH):
        base_damage = attacker.attack
        multiplier = attacker.get_damage_multiplier() if hasattr(attacker, 'get_damage_multiplier') else 1.0
        
        if skill_type == SkillType.SLASH:
            damage = int((base_damage + random.randint(-3, 5)) * multiplier)
        elif skill_type == SkillType.POWER_STRIKE:
            damage = int((int(base_damage * 1.5) + random.randint(0, 10)) * multiplier)
        elif skill_type == SkillType.MAGIC_BOLT:
            damage = int((attacker.magic + random.randint(5, 15)) * multiplier)
        elif skill_type == SkillType.POISON_STRIKE:
            damage = int((base_damage + random.randint(5, 12)) * multiplier)
        elif skill_type == SkillType.ARROW_SHOT:
            damage = int((base_damage + random.randint(3, 8)) * multiplier)
        elif skill_type == SkillType.MULTI_SHOT:
            damage = int((int(base_damage * 1.3) + random.randint(2, 6)) * multiplier)
        else:
            damage = int((base_damage + random.randint(-2, 3)) * multiplier)
        
        return max(1, damage)
    
    def player_turn(self):
        player = self.players[self.current_player_idx]
        
        print(f"\n{'─'*60}")
        print(f"GILIRAN {player.nama} ({player.role})")
        print(f"{'─'*60}")
        print(f"❤️  HP: {player.hp}/{player.hp_max} | ✨ MP: {player.mp}/{player.mp_max}")
        
        if self.enemies:
            print(f"\n👹 Musuh:")
            for idx, enemy in enumerate(self.enemies):
                if enemy.hp > 0:
                    enemy.show_status()
        
        while True:
            print(f"\n{player.nama}, pilih aksi:")
            print("[1] Slash")
            print("[2] Power Strike (MP: 10)")
            print("[3] Magic Bolt (MP: 15)")
            print("[4] Poison Strike (MP: 12)")
            print("[5] Heal (MP: 20)")
            
            if player.role == "Archer":
                print("[6] Arrow Shot")
                print("[7] Multi Shot (MP: 15)")
            
            if player.potions:
                print("[8] Gunakan Potion")
            if player.bombs:
                print("[9] Gunakan Bomb")
            
            print("[0] Status")
            
            pilihan = input("\nPilihan: ").strip()
            
            if pilihan == "1":
                if not self.enemies:
                    print("❌ Tidak ada musuh!")
                    continue
                target_idx = 0 if len(self.enemies) == 1 else self.select_target()
                if target_idx is None:
                    continue
                damage = self.calculate_damage(player, SkillType.SLASH)
                actual_damage = self.enemies[target_idx].take_damage(damage)
                print(f"⚔️  Menyerang dengan Slash!")
                print(f"💥 Damage: {actual_damage}")
                return "attack"
            
            elif pilihan == "2":
                if not self.enemies:
                    print("❌ Tidak ada musuh!")
                    continue
                if not player.use_mp(10):
                    print("❌ MP tidak cukup!")
                    continue
                target_idx = 0 if len(self.enemies) == 1 else self.select_target()
                if target_idx is None:
                    player.mp += 10
                    continue
                damage = self.calculate_damage(player, SkillType.POWER_STRIKE)
                actual_damage = self.enemies[target_idx].take_damage(damage)
                print(f"⚡ Power Strike!")
                print(f"💥 Damage: {actual_damage}")
                return "attack"
            
            elif pilihan == "3":
                if SkillType.MAGIC_BOLT not in player.skills:
                    print("❌ Skill tidak dimiliki!")
                    continue
                if not self.enemies:
                    print("❌ Tidak ada musuh!")
                    continue
                if not player.use_mp(15):
                    print("❌ MP tidak cukup!")
                    continue
                target_idx = 0 if len(self.enemies) == 1 else self.select_target()
                if target_idx is None:
                    player.mp += 15
                    continue
                damage = self.calculate_damage(player, SkillType.MAGIC_BOLT)
                actual_damage = self.enemies[target_idx].take_damage(damage)
                print(f"🔮 Magic Bolt!")
                print(f"💥 Damage: {actual_damage}")
                return "attack"
            
            elif pilihan == "4":
                if SkillType.POISON_STRIKE not in player.skills:
                    print("❌ Skill tidak dimiliki!")
                    continue
                if not self.enemies:
                    print("❌ Tidak ada musuh!")
                    continue
                if not player.use_mp(12):
                    print("❌ MP tidak cukup!")
                    continue
                target_idx = 0 if len(self.enemies) == 1 else self.select_target()
                if target_idx is None:
                    player.mp += 12
                    continue
                damage = self.calculate_damage(player, SkillType.POISON_STRIKE)
                actual_damage = self.enemies[target_idx].take_damage(damage)
                print(f"☠️  Poison Strike!")
                print(f"💥 Damage: {actual_damage}")
                return "attack"
            
            elif pilihan == "5":
                if SkillType.HEAL not in player.skills:
                    print("❌ Skill tidak dimiliki!")
                    continue
                if not player.use_mp(20):
                    print("❌ MP tidak cukup!")
                    continue
                heal_amount = player.magic + random.randint(10, 20)
                player.restore_hp(heal_amount)
                print(f"💚 Menyembuhkan diri!")
                print(f"❤️  HP: +{heal_amount}")
                return "heal"
            
            elif pilihan == "6" and player.role == "Archer":
                if SkillType.ARROW_SHOT not in player.skills:
                    print("❌ Skill tidak dimiliki!")
                    continue
                if not self.enemies:
                    print("❌ Tidak ada musuh!")
                    continue
                target_idx = 0 if len(self.enemies) == 1 else self.select_target()
                if target_idx is None:
                    continue
                damage = self.calculate_damage(player, SkillType.ARROW_SHOT)
                actual_damage = self.enemies[target_idx].take_damage(damage)
                print(f"🏹 Arrow Shot!")
                print(f"💥 Damage: {actual_damage}")
                return "attack"
            
            elif pilihan == "7" and player.role == "Archer":
                if SkillType.MULTI_SHOT not in player.skills:
                    print("❌ Skill tidak dimiliki!")
                    continue
                if not player.use_mp(15):
                    print("❌ MP tidak cukup!")
                    continue
                total_damage = 0
                print(f"🏹 Multi Shot! Serangan ke semua musuh!")
                for enemy in self.enemies:
                    if enemy.hp > 0:
                        damage = self.calculate_damage(player, SkillType.MULTI_SHOT)
                        actual_damage = enemy.take_damage(damage)
                        total_damage += actual_damage
                        print(f"  {enemy.nama}: {actual_damage} damage")
                return "attack"
            
            elif pilihan == "8" and player.potions:
                self.use_potion(player)
                return "item"
            
            elif pilihan == "9" and player.bombs:
                self.use_bomb(player)
                return "item"
            
            elif pilihan == "0":
                player.show_status()
                continue
            
            else:
                print("❌ Input tidak valid!")
    
    def select_target(self):
        """Pilih target musuh"""
        if not self.enemies:
            return None
        
        if len(self.enemies) == 1:
            return 0
        
        print("\n🎯 Pilih target:")
        for idx, enemy in enumerate(self.enemies):
            if enemy.hp > 0:
                print(f"[{idx+1}] {enemy.nama} (HP: {enemy.hp}/{enemy.hp_max})")
        
        while True:
            try:
                choice = int(input("Pilih (0 batal): ")) - 1
                if choice == -1:
                    return None
                if 0 <= choice < len(self.enemies):
                    return choice
            except:
                pass
            print("❌ Input tidak valid!")
    
    def use_potion(self, player):
        """Menu gunakan potion"""
        print("\n🧪 Pilih Potion:")
        for idx, (nama, jumlah) in enumerate(player.potions.items(), 1):
            print(f"[{idx}] {nama} (x{jumlah})")
        
        try:
            choice = int(input("Pilih (0 batal): ")) - 1
            if choice == -1:
                return
            potion_names = list(player.potions.keys())
            if 0 <= choice < len(potion_names):
                nama = potion_names[choice]
                
                if "Health" in nama:
                    hp_restore = 30 if nama == "Health Potion" else 80
                    player.restore_hp(hp_restore)
                    print(f"✅ Gunakan {nama}! ❤️  +{hp_restore} HP")
                elif "Rage" in nama:
                    effect = StatusEffect("rage", "buff", 20, 3)
                    player.apply_status_effect(effect)
                    print(f"✅ Gunakan {nama}! ⚡ +20% Damage untuk 3 turn!")
                elif "Weaken" in nama:
                    if self.enemies:
                        target_idx = 0 if len(self.enemies) == 1 else self.select_target()
                        if target_idx is not None:
                            effect = StatusEffect("weaken", "debuff", 15, 3)
                            self.enemies[target_idx].apply_status_effect(effect)
                            print(f"✅ Gunakan {nama} ke {self.enemies[target_idx].nama}! -15% Damage musuh selama 3 turn!")
                
                player.potions[nama] -= 1
                if player.potions[nama] == 0:
                    del player.potions[nama]
        except:
            pass
    
    def use_bomb(self, player):
        """Menu gunakan bomb"""
        print("\n💣 Pilih Bomb:")
        for idx, (nama, jumlah) in enumerate(player.bombs.items(), 1):
            print(f"[{idx}] {nama} (x{jumlah})")
        
        try:
            choice = int(input("Pilih (0 batal): ")) - 1
            if choice == -1:
                return
            bomb_names = list(player.bombs.keys())
            if 0 <= choice < len(bomb_names):
                nama = bomb_names[choice]
                total_damage = 0
                print(f"💣 Ledakan {nama}! AOE Damage ke semua musuh!")
                for enemy in self.enemies:
                    if enemy.hp > 0:
                        damage = random.randint(30, 50)
                        actual_damage = enemy.take_damage(damage)
                        total_damage += actual_damage
                        print(f"  {enemy.nama}: {actual_damage} damage")
                
                player.bombs[nama] -= 1
                if player.bombs[nama] == 0:
                    del player.bombs[nama]
                print(f"💥 Total damage: {total_damage}")
        except:
            pass
    
    def enemy_turn(self):
        """Giliran musuh"""
        for enemy in self.enemies:
            if enemy.hp <= 0:
                continue
            
            target = random.choice(self.players)
            action = random.choice(["attack", "attack", "power_strike"])
            
            if action == "power_strike" and random.random() > 0.4:
                damage = self.calculate_damage(enemy, SkillType.POWER_STRIKE)
                actual_damage = target.take_damage(damage)
                print(f"\n👹 {enemy.nama} menggunakan Power Strike ke {target.nama}!")
                print(f"💥 Damage: {actual_damage}")
            else:
                damage = self.calculate_damage(enemy, SkillType.SLASH)
                actual_damage = target.take_damage(damage)
                print(f"\n👹 {enemy.nama} menyerang {target.nama}!")
                print(f"💥 Damage: {actual_damage}")
            
            enemy.reduce_status_effects()
        
        for player in self.players:
            player.reduce_status_effects()
    
    def start_battle(self, story_text=""):
        """Mulai battle"""
        print(f"\n{'='*60}")
        print("⚔️  PERTEMPURAN DIMULAI! ⚔️")
        print(f"{'='*60}")
        if story_text:
            print(story_text)
        
        while True:
            self.turn += 1
            
            for idx, player in enumerate(self.players):
                self.current_player_idx = idx
                if player.hp <= 0:
                    continue
                
                action = self.player_turn()
                
                if all(enemy.hp <= 0 for enemy in self.enemies):
                    return self.battle_won()
                
                print()
                time.sleep(1)
                self.enemy_turn()
                
                if any(player.hp <= 0 for player in self.players):
                    return self.battle_lost()
                
                time.sleep(2)

    def battle_won(self):
        """Menang"""
        print(f"\n{'='*60}")
        print("🎉 KEMENANGAN! 🎉")
        print(f"{'='*60}")
        
        total_exp = 0
        total_gold = 0
        
        for enemy in self.enemies:
            total_exp += enemy.exp_drop
            total_gold += enemy.gold_drop
        
        for player in self.players:
            player.gain_exp(total_exp // len(self.players))
            player.gold += total_gold // len(self.players)
        
        print(f"✨ EXP: +{total_exp // len(self.players)} per karakter")
        print(f"💰 Gold: +{total_gold // len(self.players)} per karakter")
        return True
    
    def battle_lost(self):
        """Kalah"""
        print(f"\n{'='*60}")
        print("💀 KALAH DALAM PERTEMPURAN 💀")
        print(f"{'='*60}")
        return False

def save_game(players, chapter, save_name="autosave"):
    """Simpan game"""
    save_data = {
        "chapter": chapter,
        "players": []
    }
    
    for player in players:
        player_data = {
            "nama": player.nama,
            "role": player.role,
            "level": player.level,
            "exp": player.exp,
            "exp_max": player.exp_max,
            "hp": player.hp,
            "hp_max": player.hp_max,
            "mp": player.mp,
            "mp_max": player.mp_max,
            "attack": player.attack,
            "defense": player.defense,
            "magic": player.magic,
            "agility": player.agility,
            "gold": player.gold,
            "skills": [s.name for s in player.skills],
            "potions": player.potions,
            "bombs": player.bombs,
        }
        save_data["players"].append(player_data)
    
    os.makedirs("saves", exist_ok=True)
    
    with open(f"saves/{save_name}.json", "w") as f:
        json.dump(save_data, f, indent=2)
    
    print(f"✅ Game disimpan!")

def load_game(save_name="autosave"):
    """Load game"""
    try:
        with open(f"saves/{save_name}.json", "r") as f:
            save_data = json.load(f)
        
        players = []
        for player_data in save_data["players"]:
            player = Character(
                player_data["nama"],
                role=player_data["role"],
                hp=player_data["hp_max"],
                mp=player_data["mp_max"],
                attack=player_data["attack"],
                defense=player_data["defense"],
                magic=player_data["magic"],
                agility=player_data["agility"]
            )
            
            player.level = player_data["level"]
            player.exp = player_data["exp"]
            player.exp_max = player_data["exp_max"]
            player.hp = player_data["hp"]
            player.mp = player_data["mp"]
            player.gold = player_data["gold"]
            player.skills = [SkillType[s] for s in player_data["skills"]]
            player.potions = player_data["potions"]
            player.bombs = player_data["bombs"]
            
            players.append(player)
        
        chapter = save_data["chapter"]
        
        print(f"✅ Game dimuat!")
        for player in players:
            print(f"👤 {player.nama} ({player.role}) - Level {player.level}")
        
        return players, chapter
    
    except FileNotFoundError:
        print(f"❌ File save tidak ditemukan!")
        return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def list_save_files():
    """Daftar save file"""
    if not os.path.exists("saves"):
        return []
    
    save_files = [f[:-5] for f in os.listdir("saves") if f.endswith(".json")]
    
    if not save_files:
        return []
    
    print("\n📂 DAFTAR SAVE FILE:")
    for idx, save in enumerate(save_files, 1):
        try:
            with open(f"saves/{save}.json", "r") as f:
                data = json.load(f)
            player_names = ", ".join([p["nama"] for p in data["players"]])
            print(f"[{idx}] {save} - {player_names} (Chapter {data['chapter']})")
        except:
            pass
    
    return save_files

def visit_shop(players):
    """Shop"""
    potions = [
        Potion("Health Potion", 50, hp_restore=30),
        Potion("Greater Health Potion", 100, hp_restore=80),
        Potion("Rage Potion", 150, effect=StatusEffect("rage", "buff", 20, 3)),
        Potion("Weaken Potion", 120, effect=StatusEffect("weaken", "debuff", 15, 3)),
    ]
    
    bombs = [
        Bomb("Fire Bomb", 200, 40),
        Bomb("Ice Bomb", 200, 40),
    ]
    
    weapons = [
        Weapon("Iron Sword", 250, 8),
        Weapon("Steel Sword", 500, 15),
        Weapon("Wooden Bow", 200, 7),
        Weapon("Steel Bow", 400, 12),
    ]
    
    armor_list = [
        Armor("Iron Plate", 300, 6),
        Armor("Steel Plate", 700, 12),
    ]
    
    while True:
        print(f"\n🏪 SHOP")
        for idx, player in enumerate(players, 1):
            print(f"[{idx}] {player.nama} ({player.role}) - Gold: {player.gold}")
        print("[0] Keluar Shop")
        
        pilihan = input("Pilih karakter: ").strip()
        
        try:
            idx = int(pilihan) - 1
            if idx == -1:
                break
            if 0 <= idx < len(players):
                player = players[idx]
                
                print(f"\n{player.nama}, pilih item:")
                print("[1] Potion  [2] Bomb  [3] Weapon  [4] Armor  [5] Keluar")
                
                item_pilihan = input("Pilihan: ").strip()
                
                if item_pilihan == "1":
                    for i, p in enumerate(potions, 1):
                        print(f"[{i}] {p.nama} - ${p.harga}")
                    p_idx = input("Pilih (0 batal): ").strip()
                    try:
                        p_idx = int(p_idx) - 1
                        if 0 <= p_idx < len(potions):
                            p = potions[p_idx]
                            if player.gold >= p.harga:
                                player.gold -= p.harga
                                if p.nama not in player.potions:
                                    player.potions[p.nama] = 0
                                player.potions[p.nama] += 1
                                print(f"✅ Beli {p.nama}")
                            else:
                                print("❌ Gold kurang!")
                    except:
                        pass
                
                elif item_pilihan == "2":
                    for i, b in enumerate(bombs, 1):
                        print(f"[{i}] {b.nama} - ${b.harga}")
                    b_idx = input("Pilih (0 batal): ").strip()
                    try:
                        b_idx = int(b_idx) - 1
                        if 0 <= b_idx < len(bombs):
                            b = bombs[b_idx]
                            if player.gold >= b.harga:
                                player.gold -= b.harga
                                if b.nama not in player.bombs:
                                    player.bombs[b.nama] = 0
                                player.bombs[b.nama] += 1
                                print(f"✅ Beli {b.nama}")
                            else:
                                print("❌ Gold kurang!")
                    except:
                        pass
                
                elif item_pilihan == "3":
                    for i, w in enumerate(weapons, 1):
                        print(f"[{i}] {w.nama} - ${w.harga}")
                    w_idx = input("Pilih (0 batal): ").strip()
                    try:
                        w_idx = int(w_idx) - 1
                        if 0 <= w_idx < len(weapons):
                            w = weapons[w_idx]
                            if player.gold >= w.harga:
                                player.gold -= w.harga
                                player.weapon_inventory.append(w)
                                print(f"✅ Beli {w.nama}")
                            else:
                                print("❌ Gold kurang!")
                    except:
                        pass
                
                elif item_pilihan == "4":
                    for i, a in enumerate(armor_list, 1):
                        print(f"[{i}] {a.nama} - ${a.harga}")
                    a_idx = input("Pilih (0 batal): ").strip()
                    try:
                        a_idx = int(a_idx) - 1
                        if 0 <= a_idx < len(armor_list):
                            a = armor_list[a_idx]
                            if player.gold >= a.harga:
                                player.gold -= a.harga
                                player.armor_inventory.append(a)
                                print(f"✅ Beli {a.nama}")
                            else:
                                print("❌ Gold kurang!")
                    except:
                        pass
        except:
            pass

def intro_scene(nama):
    """Intro"""
    print("\n" + "="*70)
    print("🌙 SHADOW OF NARCOTICS 🌙".center(70))
    print("="*70)
    
    print(f"""
Tahun 2120, di kota NOVA RAYA...

Namamu adalah {nama}. Seorang rakyat jelata yang bekerja sebagai 
pedagang sayuran di pasar sore. Hidupmu sederhana, meski kadang sulit.

Tapi semenjak 3 bulan lalu, obat terlarang "VENOM" mulai beredar.
Banyak anak muda adiktif. Kota berubah suram. Kejahatan meningkat pesat.

---

Malam ini, setelah menutup lapakmu, kamu pulang lewat gang sempit.
Tiba-tiba, suara jeritan anak kecil!

Seorang anak (±8 tahun) sedang dirembugkan tiga preman.
Salah seorang mencekoki anak itu dengan VENOM.

"TIDAK! AAAAHHH!" teriak si anak.

Sesuatu dalam hatimu bergerak. Kamu tidak bisa diam melihat ini.
    """)
    
    print("\n" + "="*70)
    time.sleep(2)

def encounter_thugs(player):
    """Encounter preman"""
    print("\n" + "="*70)
    print("⚠️  PERTAMA KALI BERTEMPUR ⚠️".center(70))
    print("="*70)
    
    print(f"""
Kamu melangkah berani menuju ketiga preman itu.

"HEY! LEPASKAN ANAK ITU!" teriakmu.

Ketiga preman menoleh. Mereka terkejut. Yang terdepan, pria bertubuh kekar
bertato di wajahnya, menatapmu sinis.

PREMAN KEPALA: "Heh? Ada yang berani mengganggu bisnis kami?"

Kamu berdiri tegak. "{player.nama}! Aku akan menghentikan kalian!"

Mereka tertawa mengejek, tapi mata mereka menunjukkan marah.

PREMAN KEPALA: "Baiklah! Kami akan mengajarimu adab, nak!"

Mereka bersiap menyerang!
    """)
    
    input("\nTekan ENTER untuk mulai pertempuran...")

def thug_encounter_battle(player):
    """Battle preman"""
    enemy = Enemy(
        "Kepala Preman SCAR",
        hp=60, attack=12, defense=6, magic=3,
        gold_drop=150, exp_drop=80,
        level=2
    )
    
    battle = Battle(player, enemy)
    
    if battle.start_battle():
        print(f"""
"ARGH! Cukup!" teriak SCAR sambil mundur.

Dia menatapmu penuh dendam, tapi juga keraguan.
Dua temannya melihat bosnya terluka dan mundur.

"Kita pergi dari sini!" SCAR memanggil rekannya.

Mereka berlari meninggalkan gang, meninggalkan {player.nama} dan anak itu...

Anak itu berlari menghampirimu dengan mata berair.
"Terima kasih, kak! Terima kasih sudah menyelamatkan aku!"
        """)
        return True
    else:
        print("""
Tubuhmu lemas. Ketiga preman terus menyerang tanpa henti.
Kamu jatuh... dan anak itu pun ditangkap...

[GAME OVER]
        """)
        return False

def chapter_2_intro(player):
    """Intro Chapter 2"""
    print(f"""
Kamu membawa anak itu ke rumah sakit. Dokter memeriksa dan menjamin
anak itu akan baik-baik saja.

Saat keluar rumah sakit, seorang wanita menemuimu.

"Kami melihat keberanianmu tadi," katanya. "Aku dari SHADOW GUARDIANS,
organisasi yang melawan perdaran VENOM. Kami butuh orang sepertimu."

Kamu menerima ajakan itu. Perjalananmu melawan narkoba dimulai...
    """)
    
    input("Tekan ENTER...")

def chapter_3_intro(players):
    """Intro Chapter 3 - Misi Kereta Pedagang"""
    print(f"""
Kamu sudah melatih diri selama beberapa minggu sebagai anggota Shadow Guardians.
Sekarang kamu sudah cukup kuat untuk misi yang lebih berat.

Ketua organisasi memanggilmu ke ruang rahasia mereka.

KETUA SHADOW GUARDIANS: "Kami menerima informasi bahwa ada kereta pedagang
yang akan melewati jalanan kota malam ini. Mereka adalah distributor utama VENOM
di wilayah ini."

"Tugasmu adalah menghentikan kereta itu dan mengamankan kiriman VENOM
sebelum sampai ke tangan pengedar lokal."

"Karena ini misi berat, aku akan memberikan rekan yang telah terlatih untuk
membantumu. Dia adalah SANTOSO, salah satu pemanah terbaik kami."

Pintu ruang terbuka, dan seorang pria tinggi dengan busur di tangannya
melangkah masuk. Dia memperkenalkan dirinya dengan tepat sasaran.

SANTOSO: "Nama saya Santoso. Aku siap mendukung misimu."

Mereka memberikan kalian informasi lengkap:
- Kereta akan melewati JALANAN GELAP (rute cepat menuju pelabuhan)
- Dijaga oleh 3 pengawal profesional
- Mereka bersenjata dan terlatih

KETUA: "Siapkan diri kalian. Misi dimulai dalam 1 jam."

Kamu dan Santoso mempersiapkan diri untuk misi yang paling berbahaya sampai saat ini...
    """)
    
    input("Tekan ENTER untuk lanjut...")

def merchant_caravan_battle(players):
    """Battle Kereta Pedagang"""
    enemies = [
        Enemy("Pengawal Kereta 1", hp=80, attack=14, defense=7, magic=2, gold_drop=200, exp_drop=100, level=3),
        Enemy("Pengawal Kereta 2", hp=75, attack=13, defense=6, magic=3, gold_drop=200, exp_drop=100, level=3),
        Enemy("Kapten Pengawal", hp=100, attack=16, defense=8, magic=4, gold_drop=300, exp_drop=150, level=4),
    ]
    
    battle = Battle(players, enemies)
    story = """
Jalanan gelap sepi. Hanya cahaya bulan yang menerangi.

Tiba-tiba, terdengar bunyi roda kereta. Kereta besar muncul dari kegelapan,
dikawal oleh tiga prajurit berseragam tanpa lencana resmi.

Kamu dan Santoso melompat keluar dari perdu, memblokir jalan kereta.

KAPTEN PENGAWAL: "Hah? Siapa kalian?!"

SANTOSO: "SHADOW GUARDIANS! Kalian ditangkap!"

Kapten dan pengawalnya langsung mengeluarkan senjata. Pertarungan pun dimulai!

---PERTEMPURAN DIMULAI---
    """
    
    if battle.start_battle(story):
        print("""
Setelah pertarungan sengit, ketiga pengawal akhirnya tumbang.

Santoso langsung membuka pekat kereta. Ribuan paket VENOM berisi di dalamnya.

SANTOSO: "Ini dia! Stok besar VENOM akan ditangkap!"

Tim Shadow Guardians segera tiba dan menangkap semua VENOM serta membawa
ketiga pengawal ke kantor polisi dengan bukti lengkap.

Misi terselesaikan dengan sempurna!

KETUA SHADOW GUARDIANS: "Kalian berdua telah berbuat luar biasa.
Dengan penangkapan ini, kami bisa menekan aktivitas pengedar VENOM di kota ini.
Ini adalah awal dari akhir untuk para pengedar narkoba!"

Kamu dan Santoso kembali ke markas dengan penuh kebanggaan.
Perjalanan panjang masih menanti...
        """)
        return True
    else:
        print("""
Pertarungan sangat sengit. Pengawal kereta lebih kuat dari yang diperkirakan.

Kamu dan Santoso berusaha sebaik mungkin, namun akhirnya kewalahan.
Kereta berhasil lolos, meninggalkan kalian dalam keadaan terluka.

SANTOSO: "Mereka terlalu kuat... aku minta maaf, aku gagal..."

Tim Shadow Guardians mengambil kalian dan merawat di markas.

KETUA: "Kalian masih perlu banyak latihan. Jangan menyerah. Kita akan coba lagi."
        """)
        return False

def explore_world(players):
    """Explore"""
    monsters = {
        "Slime Hijau": Enemy("Slime Hijau", 25, 5, 2, 2, 30, 25, level=1),
        "Goblin Kecil": Enemy("Goblin Kecil", 40, 8, 3, 1, 60, 50, level=2),
        "Orc Prajurit": Enemy("Orc Prajurit", 70, 14, 6, 3, 150, 120, level=3),
    }
    
    locations = [
        ("Hutan Gelap", ["Slime Hijau", "Goblin Kecil"]),
        ("Gua Orc", ["Goblin Kecil", "Orc Prajurit"]),
    ]
    
    print(f"\n{'='*60}")
    print("🌍 JELAJAHI DUNIA".center(60))
    print(f"{'='*60}")
    
    for idx, (nama, _) in enumerate(locations, 1):
        print(f"[{idx}] {nama}")
    
    pilihan = input("\nPilih lokasi (0 batal): ").strip()
    
    try:
        idx = int(pilihan) - 1
        if idx == -1:
            return None
        if 0 <= idx < len(locations):
            location_name, possible_monsters = locations[idx]
            print(f"\n🗺️  Kamu memasuki {location_name}...")
            time.sleep(1)
            
            enemy_name = random.choice(possible_monsters)
            enemy = monsters[enemy_name]
            
            enemy_encounter = Enemy(
                enemy.nama, enemy.hp_max, enemy.attack, enemy.defense,
                enemy.magic, enemy.gold_drop, enemy.exp_drop, enemy.level
            )
            
            print(f"\n⚠️  {enemy_encounter.nama} muncul!")
            time.sleep(1)
            
            return enemy_encounter
    except ValueError:
        pass
    
    return None

def main_menu(players, chapter):
    """Main Menu"""
    print(f"\n{'='*60}")
    print("MENU UTAMA".center(60))
    print(f"{'='*60}")
    print(f"Chapter: {chapter}")
    for player in players:
        print(f"👤 {player.nama} ({player.role}) - Level {player.level}, Gold: {player.gold}")
    print("[1] Jelajahi Dunia")
    print("[2] Kunjungi Shop")
    print("[3] Status Karakter")
    print("[4] Simpan Game")
    print("[5] Keluar Game")
    
    while True:
        pilihan = input("\nPilihan (1-5): ").strip()
        if pilihan == "1":
            return "explore"
        elif pilihan == "2":
            visit_shop(players)
        elif pilihan == "3":
            for player in players:
                player.show_status()
        elif pilihan == "4":
            save_name = input("Nama save (default: autosave): ").strip() or "autosave"
            save_game(players, chapter, save_name)
        elif pilihan == "5":
            return "exit"
        else:
            print("❌ Input tidak valid!")

def game_utama():
    """Main"""
    print("\n" + "="*70)
    print("SHADOW OF NARCOTICS".center(70))
    print("="*70)
    print("\n[1] Game Baru")
    print("[2] Lanjutkan Game (Load Save)")
    print("[3] Keluar")
    
    while True:
        pilihan = input("\nPilihan (1-3): ").strip()
        
        if pilihan == "1":
            break
        elif pilihan == "2":
            save_files = list_save_files()
            if save_files:
                pilihan_save = input("\nPilih save file (0 batal): ").strip()
                try:
                    idx = int(pilihan_save) - 1
                    if idx == -1:
                        continue
                    if 0 <= idx < len(save_files):
                        players, chapter = load_game(save_files[idx])
                        if players:
                            if chapter == 2:
                                main_game_loop(players, chapter)
                            elif chapter == 3:
                                chapter_3_intro(players)
                                main_game_loop(players, chapter)
                            return
                except ValueError:
                    pass
            continue
        elif pilihan == "3":
            print("Terima kasih sudah bermain!")
            return
        else:
            print("❌ Input tidak valid!")
    
    # Game baru
    nama = input("\nSiapa namamu? ").strip()
    player = Character(nama, role="Warrior")
    
    intro_scene(nama)
    input("Tekan ENTER...")
    
    encounter_thugs(player)
    battle_result = thug_encounter_battle(player)
    
    if battle_result:
        players = [player]
        chapter = 2
        chapter_2_intro(player)
        main_game_loop(players, chapter)
    else:
        print("\n[Coba lagi?]")
        game_utama()

def main_game_loop(players, chapter):
    """Game loop"""
    while True:
        if chapter == 2:
            menu_choice = main_menu(players, chapter)
            
            if menu_choice == "exit":
                print(f"\nTerima kasih sudah bermain!")
                break
            
            elif menu_choice == "explore":
                enemy = explore_world(players)
                
                if enemy:
                    input("\nTekan ENTER untuk pertempuran...")
                    battle = Battle(players[0], enemy)
                    
                    if battle.start_battle():
                        print("\n⏳ Kamu kembali ke kota...")
                        input("Tekan ENTER...")
                    else:
                        print("\n💀 Kamu kalah!")
                        players[0].hp = players[0].hp_max
                        print("Dirawat di markas...")
                        input("Tekan ENTER...")
            
            # Trigger Chapter 3 saat level cukup
            if players[0].level >= 3:
                print("\n📬 Kamu menerima panggilan dari Ketua Shadow Guardians...")
                input("Tekan ENTER...")
                chapter = 3
                
                santoso = Character("Santoso", role="Archer", hp=90, mp=60, attack=9, defense=4, magic=7, agility=9)
                santoso.level = 3
                santoso.skills = [SkillType.SLASH, SkillType.ARROW_SHOT, SkillType.MULTI_SHOT]
                players.append(santoso)
                
                chapter_3_intro(players)
                
                print("\n🗺️  Kamu dan Santoso menuju Jalanan Gelap...")
                input("Tekan ENTER...")
                
                if merchant_caravan_battle(players):
                    print("\n🎊 Misi Chapter 3 berhasil!")
                    chapter = 4
                else:
                    print("\n💪 Kamu akan coba lagi...")
                    players[1].hp = players[1].hp_max
                    players[0].hp = players[0].hp_max
                input("Tekan ENTER...")
        
        elif chapter >= 3:
            menu_choice = main_menu(players, chapter)
            
            if menu_choice == "exit":
                print(f"\nTerima kasih sudah bermain!")
                break
            
            elif menu_choice == "explore":
                if len(players) == 1:
                    enemy = explore_world(players)
                    if enemy:
                        input("\nTekan ENTER untuk pertempuran...")
                        battle = Battle(players[0], enemy)
                        if battle.start_battle():
                            print("\n⏳ Kembali ke kota...")
                            input("Tekan ENTER...")
                        else:
                            print("\n💀 Kalah!")
                            players[0].hp = players[0].hp_max
                            input("Tekan ENTER...")
                else:
                    enemy = explore_world(players)
                    if enemy:
                        input("\nTekan ENTER untuk pertempuran...")
                        battle = Battle(players, enemy)
                        if battle.start_battle():
                            print("\n⏳ Kembali ke kota...")
                            input("Tekan ENTER...")
                        else:
                            print("\n💀 Kalah!")
                            for p in players:
                                p.hp = p.hp_max
                            input("Tekan ENTER...")

if __name__ == "__main__":
    game_utama()
