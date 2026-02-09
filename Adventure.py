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

class Potion:
    def __init__(self, nama, harga, hp_restore):
        self.nama = nama
        self.harga = harga
        self.hp_restore = hp_restore

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
    def __init__(self, nama, hp=100, mp=50, attack=10, defense=5, magic=8, agility=7):
        self.nama = nama
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
        self.equipped_weapon = None
        self.equipped_armor = None
        self.weapon_inventory = []
        self.armor_inventory = []
        self.skills = [SkillType.SLASH]
        
    def take_damage(self, damage):
        reduced_damage = max(1, damage - self.defense // 2)
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
        
        print(f"\n✨ LEVEL UP! Kamu sekarang level {self.level}!")
        print(f"HP Max: +15 → {self.hp_max}")
        print(f"MP Max: +10 → {self.mp_max}")
        
    def show_status(self):
        print(f"\n{'='*50}")
        print(f"👤 {self.nama.upper()} - Level {self.level}")
        print(f"{'='*50}")
        print(f"❤️  HP: {self.hp}/{self.hp_max}")
        print(f"✨ MP: {self.mp}/{self.mp_max}")
        print(f"⚔️  Attack: {self.attack}  🛡️  Defense: {self.defense}")
        print(f"🔮 Magic: {self.magic}  ⚡ Agility: {self.agility}")
        print(f"💰 Gold: {self.gold}")
        print(f"Level {self.level}: {self.exp}/{self.exp_max} EXP")
        if self.equipped_weapon:
            print(f"🗡️  Weapon: {self.equipped_weapon.nama}")
        if self.equipped_armor:
            print(f"🛡️  Armor: {self.equipped_armor.nama}")
        print(f"📚 Skills: {', '.join([s.value for s in self.skills])}")
        if self.potions:
            print(f"\n🧪 Potions:")
            for nama, jumlah in self.potions.items():
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
    
    def take_damage(self, damage):
        reduced_damage = max(1, damage - self.defense // 2)
        self.hp -= reduced_damage
        return reduced_damage
    
    def show_status(self):
        print(f"👹 {self.nama} - Level {self.level}")
        print(f"HP: {self.hp}/{self.hp_max} | Attack: {self.attack}")

class Battle:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.turn = 0
    
    def calculate_damage(self, attacker, skill_type=SkillType.SLASH):
        base_damage = attacker.attack
        
        if skill_type == SkillType.SLASH:
            damage = base_damage + random.randint(-3, 5)
        elif skill_type == SkillType.POWER_STRIKE:
            damage = int(base_damage * 1.5) + random.randint(0, 10)
        elif skill_type == SkillType.MAGIC_BOLT:
            damage = attacker.magic + random.randint(5, 15)
        elif skill_type == SkillType.POISON_STRIKE:
            damage = base_damage + random.randint(5, 12)
        else:
            damage = base_damage + random.randint(-2, 3)
        
        return max(1, damage)
    
    def player_turn(self):
        print(f"\n--- GILIRAN {self.player.nama} (TURN {self.turn}) ---")
        self.enemy.show_status()
        
        print("\n[1] Slash - Serangan dasar")
        print("[2] Power Strike - Serangan kuat (MP: 10)")
        print("[3] Magic Bolt - Ledak sihir (MP: 15)")
        print("[4] Poison Strike - Serangan beracun (MP: 12)")
        print("[5] Heal - Penyembuhan (MP: 20)")
        print("[6] Status")
        
        while True:
            pilihan = input("\nPilih aksi (1-6): ").strip()
            
            if pilihan == "1":
                damage = self.calculate_damage(self.player, SkillType.SLASH)
                actual_damage = self.enemy.take_damage(damage)
                print(f"\n⚔️  Menyerang dengan Slash!")
                print(f"💥 Damage: {actual_damage}")
                return "attack"
            
            elif pilihan == "2":
                if not self.player.use_mp(10):
                    print("❌ MP tidak cukup!")
                    continue
                damage = self.calculate_damage(self.player, SkillType.POWER_STRIKE)
                actual_damage = self.enemy.take_damage(damage)
                print(f"\n⚡ Power Strike!")
                print(f"💥 Damage: {actual_damage}")
                return "attack"
            
            elif pilihan == "3":
                if SkillType.MAGIC_BOLT not in self.player.skills:
                    print("❌ Skill tidak dimiliki!")
                    continue
                if not self.player.use_mp(15):
                    print("❌ MP tidak cukup!")
                    continue
                damage = self.calculate_damage(self.player, SkillType.MAGIC_BOLT)
                actual_damage = self.enemy.take_damage(damage)
                print(f"\n🔮 Magic Bolt!")
                print(f"💥 Damage: {actual_damage}")
                return "attack"
            
            elif pilihan == "4":
                if SkillType.POISON_STRIKE not in self.player.skills:
                    print("❌ Skill tidak dimiliki!")
                    continue
                if not self.player.use_mp(12):
                    print("❌ MP tidak cukup!")
                    continue
                damage = self.calculate_damage(self.player, SkillType.POISON_STRIKE)
                actual_damage = self.enemy.take_damage(damage)
                print(f"\n☠️  Poison Strike!")
                print(f"💥 Damage: {actual_damage}")
                return "attack"
            
            elif pilihan == "5":
                if SkillType.HEAL not in self.player.skills:
                    print("❌ Skill tidak dimiliki!")
                    continue
                if not self.player.use_mp(20):
                    print("❌ MP tidak cukup!")
                    continue
                heal_amount = self.player.magic + random.randint(10, 20)
                self.player.restore_hp(heal_amount)
                print(f"\n💚 Menyembuhkan diri!")
                print(f"❤️  HP: +{heal_amount}")
                return "heal"
            
            elif pilihan == "6":
                self.player.show_status()
                continue
            
            else:
                print("❌ Pilihan tidak valid!")
    
    def enemy_turn(self):
        action = random.choice(["attack", "attack", "attack", "power_strike"])
        
        if action == "power_strike" and random.random() > 0.4:
            damage = self.calculate_damage(self.enemy, SkillType.POWER_STRIKE)
            actual_damage = self.player.take_damage(damage)
            print(f"\n👹 {self.enemy.nama} menggunakan Power Strike!")
            print(f"💥 Damage: {actual_damage}")
        else:
            damage = self.calculate_damage(self.enemy, SkillType.SLASH)
            actual_damage = self.player.take_damage(damage)
            print(f"\n👹 {self.enemy.nama} menyerang!")
            print(f"💥 Damage: {actual_damage}")
        
        self.player.show_status()
    
    def start_battle(self, story_text=""):
        print(f"\n{'='*60}")
        print("⚔️  PERTEMPURAN DIMULAI! ⚔️")
        print(f"{'='*60}")
        if story_text:
            print(story_text)
        
        while True:
            self.turn += 1
            self.player_turn()
            
            if self.enemy.hp <= 0:
                return self.battle_won()
            
            print()
            time.sleep(1)
            self.enemy_turn()
            
            if self.player.hp <= 0:
                return self.battle_lost()
            
            time.sleep(2)
    
    def battle_won(self):
        print(f"\n{'='*60}")
        print("🎉 KEMENANGAN! 🎉")
        print(f"{'='*60}")
        exp_gained = self.enemy.exp_drop
        gold_gained = self.enemy.gold_drop
        
        self.player.gain_exp(exp_gained)
        self.player.gold += gold_gained
        
        print(f"✨ EXP: +{exp_gained}")
        print(f"💰 Gold: +{gold_gained}")
        return True
    
    def battle_lost(self):
        print(f"\n{'='*60}")
        print("💀 KALAH DALAM PERTEMPURAN 💀")
        print(f"{'='*60}")
        return False

def save_game(player, chapter, save_name="autosave"):
    """Simpan game ke JSON file"""
    save_data = {
        "nama": player.nama,
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
        "chapter": chapter,
        "skills": [s.name for s in player.skills],
        "potions": player.potions,
    }
    
    os.makedirs("saves", exist_ok=True)
    
    with open(f"saves/{save_name}.json", "w") as f:
        json.dump(save_data, f, indent=2)
    
    print(f"✅ Game disimpan!")

def load_game(save_name="autosave"):
    """Buka game dari JSON file"""
    try:
        with open(f"saves/{save_name}.json", "r") as f:
            save_data = json.load(f)
        
        player = Character(
            save_data["nama"],
            hp=save_data["hp_max"],
            mp=save_data["mp_max"],
            attack=save_data["attack"],
            defense=save_data["defense"],
            magic=save_data["magic"],
            agility=save_data["agility"]
        )
        
        player.level = save_data["level"]
        player.exp = save_data["exp"]
        player.exp_max = save_data["exp_max"]
        player.hp = save_data["hp"]
        player.mp = save_data["mp"]
        player.gold = save_data["gold"]
        player.skills = [SkillType[s] for s in save_data["skills"]]
        player.potions = save_data["potions"]
        
        chapter = save_data["chapter"]
        
        print(f"✅ Game dimuat!")
        print(f"👤 {player.nama} - Level {player.level} | 💰 Gold: {player.gold}")
        
        return player, chapter
    
    except FileNotFoundError:
        print(f"❌ File save tidak ditemukan!")
        return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def list_save_files():
    """Tampilkan daftar save file"""
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
            print(f"[{idx}] {save} - {data['nama']} (Level {data['level']}, Chapter {data['chapter']})")
        except:
            pass
    
    return save_files

def choose_skill(player):
    """Memilih skill baru saat level up"""
    available_skills = [
        (SkillType.MAGIC_BOLT, "Magic Bolt (Damage: Magic, MP: 15)"),
        (SkillType.POISON_STRIKE, "Poison Strike (Damage: High, MP: 12)"),
        (SkillType.HEAL, "Heal (Restore HP, MP: 20)"),
    ]
    
    unlearned_skills = [(s, name) for s, name in available_skills if s not in player.skills]
    
    if not unlearned_skills:
        print("✅ Semua skill sudah dikuasai!")
        return
    
    print(f"\n{'='*60}")
    print("PILIH SKILL BARU".center(60))
    print(f"{'='*60}")
    
    for idx, (skill, name) in enumerate(unlearned_skills, 1):
        print(f"[{idx}] {name}")
    
    while True:
        pilihan = input("\nPilihan: ").strip()
        try:
            idx = int(pilihan) - 1
            if 0 <= idx < len(unlearned_skills):
                skill, name = unlearned_skills[idx]
                player.skills.append(skill)
                print(f"\n✨ Kamu belajar {skill.value}!")
                return
            else:
                print("❌ Pilihan tidak valid!")
        except ValueError:
            print("❌ Input harus angka!")

def visit_shop(player):
    """Menu shop"""
    potions = [
        Potion("Health Potion", 50, 30),
        Potion("Greater Health Potion", 100, 80),
    ]
    
    weapons = [
        Weapon("Iron Sword", 250, 8),
        Weapon("Steel Sword", 500, 15),
    ]
    
    armor_list = [
        Armor("Iron Plate", 300, 6),
        Armor("Steel Plate", 700, 12),
    ]
    
    while True:
        print(f"\n🏪 SHOP - Gold: {player.gold}")
        print("[1] Beli Potion  [2] Beli Weapon  [3] Beli Armor  [4] Keluar")
        
        pilihan = input("Pilihan: ").strip()
        
        if pilihan == "1":
            for idx, p in enumerate(potions, 1):
                print(f"[{idx}] {p.nama} - ${p.harga}")
            idx_pilihan = input("Pilih (0 batal): ").strip()
            try:
                idx = int(idx_pilihan) - 1
                if idx >= 0 and idx < len(potions):
                    p = potions[idx]
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
        
        elif pilihan == "2":
            for idx, w in enumerate(weapons, 1):
                print(f"[{idx}] {w.nama} - ${w.harga} (+{w.attack_bonus} ATK)")
            idx_pilihan = input("Pilih (0 batal): ").strip()
            try:
                idx = int(idx_pilihan) - 1
                if idx >= 0 and idx < len(weapons):
                    w = weapons[idx]
                    if player.gold >= w.harga:
                        player.gold -= w.harga
                        player.weapon_inventory.append(w)
                        print(f"✅ Beli {w.nama}")
                    else:
                        print("❌ Gold kurang!")
            except:
                pass
        
        elif pilihan == "3":
            for idx, a in enumerate(armor_list, 1):
                print(f"[{idx}] {a.nama} - ${a.harga} (+{a.defense_bonus} DEF)")
            idx_pilihan = input("Pilih (0 batal): ").strip()
            try:
                idx = int(idx_pilihan) - 1
                if idx >= 0 and idx < len(armor_list):
                    a = armor_list[idx]
                    if player.gold >= a.harga:
                        player.gold -= a.harga
                        player.armor_inventory.append(a)
                        print(f"✅ Beli {a.nama}")
                    else:
                        print("❌ Gold kurang!")
            except:
                pass
        
        elif pilihan == "4":
            break

def intro_scene(nama):
    """Intro cerita awal"""
    print("\n" + "="*70)
    print("🌙 SHADOW OF NARCOTICS 🌙".center(70))
    print("="*70)
    
    print(f"""
Tahun 2120, di kota NOVA RAYA...

Namamu adalah {nama}. Seorang rakyat jelata biasa yang bekerja sebagai 
pedagang sayuran di pasar sore. Hidupmu sederhana, meski kadang sulit.

Tapi semenjak 3 bulan lalu, sesuatu mengerikan terjadi di kota ini.
Obat terlarang bernama "VENOM" mulai beredar. Banyak anak muda adiktif.
Kota yang dulu cerah, kini berubah suram. Kejahatan meningkat pesat.

---

Malam ini, setelah menutup lapakmu, kamu pulang lewat gang sempit.
Cuaca mendung, suasana gelap, angin dingin...

Tiba-tiba, suara jeritan anak kecil! Kamu mempercepat langkah.

Seorang anak kecil (±8 tahun) sedang dirembugkan tiga pria preman.
Salah seorang sedang mencekoki anak itu dengan sesuatu (VENOM).

"TIDAK! AAAAHHH!" teriak si anak.

Sesuatu dalam hatimu bergerak. Kamu tidak bisa diam melihat ini.
    """)
    
    print("\n" + "="*70)
    time.sleep(2)

def encounter_thugs(player):
    """Cutscene bertemu preman"""
    print("\n" + "="*70)
    print("⚠️  PENGALAMAN PERTAMA PERTEMPURAN ⚠️".center(70))
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
    """Battle dengan preman"""
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

def explore_world(player):
    """Explorasi dan random encounter"""
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

def main_menu(player, chapter):
    """Menu utama"""
    print(f"\n{'='*60}")
    print("MENU UTAMA".center(60))
    print(f"{'='*60}")
    print(f"💰 Gold: {player.gold} | Level: {player.level} | Chapter: {chapter}")
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
            visit_shop(player)
        elif pilihan == "3":
            player.show_status()
        elif pilihan == "4":
            save_name = input("Nama save (default: autosave): ").strip() or "autosave"
            save_game(player, chapter, save_name)
        elif pilihan == "5":
            return "exit"
        else:
            print("❌ Pilihan tidak valid!")

def game_utama():
    """Main game function"""
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
                        player, chapter = load_game(save_files[idx])
                        if player:
                            main_game_loop(player, chapter)
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
    player = Character(nama)
    chapter = 1
    
    intro_scene(nama)
    input("Tekan ENTER...")
    
    encounter_thugs(player)
    battle_result = thug_encounter_battle(player)
    
    if battle_result:
        chapter = 2
        print(f"""
Kamu membawa anak itu ke rumah sakit. Dokter memeriksa dan menjamin
anak itu akan baik-baik saja.

Saat keluar rumah sakit, seorang wanita menemuimu.

"Kami melihat keberanianmu tadi," katanya. "Aku dari SHADOW GUARDIANS,
organisasi yang melawan perdaran VENOM. Kami butuh orang sepertimu."

Kamu menerima ajakan itu. Perjalananmu melawan narkoba dimulai...
        """)
        input("\nTekan ENTER...")
        main_game_loop(player, chapter)
    else:
        print("\n[Coba lagi?]")
        game_utama()

def main_game_loop(player, chapter):
    """Game loop utama"""
    while True:
        menu_choice = main_menu(player, chapter)
        
        if menu_choice == "exit":
            print(f"\nTerima kasih sudah bermain, {player.nama}!")
            break
        
        elif menu_choice == "explore":
            enemy = explore_world(player)
            
            if enemy:
                input("\nTekan ENTER untuk pertempuran...")
                battle = Battle(player, enemy)
                
                if battle.start_battle():
                    print("\n⏳ Kamu kembali ke kota...")
                    input("Tekan ENTER...")
                else:
                    print("\n💀 Kamu kalah!")
                    player.hp = player.hp_max
                    print("Dirawat di markas Shadow Guardians...")
                    input("Tekan ENTER...")

if __name__ == "__main__":
    game_utama()
