import pyxel
import random

# ドット絵のサイズ（10×10）
masu_w, masu_h = 10, 10
# 各色のパレットインデックス
IRO_LIST = [8, 0, 9, 1,12]

class DotEditor:
    def __init__(self):
        self.dot_data = [2] * (masu_w * masu_h)
        self.color    = 1
        self.cx = 0
        self.cy = 0
        self.ox = (256 - masu_w * 16)//2
        self.oy = (266 - 10  - masu_h * 16)//2

    def update(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        self.cx = max(0, min(masu_w-1, (mx - self.ox)//16))
        self.cy = max(0, min(masu_h-1, (my - self.oy)//16))

        if pyxel.btnp(pyxel.KEY_SPACE):
            idx = self.cy * masu_w + self.cx
            self.dot_data[idx] = self.color

        # 色切替
        if pyxel.btnp(pyxel.KEY_1): self.color = 1
        if pyxel.btnp(pyxel.KEY_2): self.color = 3
        if pyxel.btnp(pyxel.KEY_3): self.color = 8
        if pyxel.btnp(pyxel.KEY_0): self.color = 2

        # Enter で次フェーズへ
        return pyxel.btnp(pyxel.KEY_RETURN)

    def draw(self):
        pyxel.cls(0)
        idx = 0
        for y in range(masu_h):
            for x in range(masu_w):
                c  = self.dot_data[idx]
                px = self.ox + x*16
                py = self.oy + y*16
                pyxel.rect(px, py, 16, 16, IRO_LIST[c])
                idx += 1
        # 枠線
        pyxel.rectb(self.ox-1, self.oy-1,
                    masu_w*16+2, masu_h*16+2, 7)
        # カーソル
        cx = self.ox + self.cx*16
        cy = self.oy + self.cy*16
        pyxel.rectb(cx, cy, 16, 16, 6)
        pyxel.text(10, 210, "[Space] Draw pixel", 7)
        pyxel.text(10, 220, "[1][2][3][0] Select color", 7)
        pyxel.text(10, 230, "[Enter] Start Game", 7)


class CharViewer:
    def __init__(self, dot_data):
        self.dots      = dot_data
        self.scale     = 2
        self.char_w    = masu_w * self.scale
        self.char_h    = masu_h * self.scale
        self.x         = 30
        self.y_ground  = 200
        self.y         = self.y_ground
        self.vy        = 0
        self.jumping   = False
        self.obstacles = []
        self.spawn_t   = 0
        self.score     = 0
        self.speed     = 3
        self.countdown_t = 40 * 4  # 約4秒のカウントダウン


    def update(self):
        # カウントダウン
        if self.countdown_t > 0:
            self.countdown_t -= 1
            return False

        # Q で即終了
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # ジャンプ
        if pyxel.btnp(pyxel.KEY_SPACE) and not self.jumping:
            self.vy      = -10
            self.jumping = True
        if self.jumping:
            self.y  += self.vy
            self.vy += 0.8
            if self.y >= self.y_ground:
                self.y       = self.y_ground
                self.vy      = 0
                self.jumping = False

        # 障害物スポーン
        self.spawn_t -= 1 
        if self.spawn_t <= 0:
            self.spawn_t = random.randint(20, 80)
            h = random. randint(  20,  40)
            w = self.scale * 2
            self.obstacles.append({'x':256, 'w':w, 'h':h, 'passed':False})

        # 障害物更新＆判定
        for o in list(self.obstacles):
            o['x'] -= self.speed
            # スコア加算
            if not o['passed'] and o['x']+o['w'] < self.x:
                o['passed'] = True
                self.score += 1
                self.speed += 0.2
            # 画面外削除
            if o['x']+o['w'] < 0:
                self.obstacles.remove(o)
                continue
            # シンプル衝突判定
            char_bot = self.y + self.char_h
            obs_top  = self.y_ground + self.char_h - o['h']
            if (o['x'] < self.x + self.char_w and
                o['x']+o['w'] > self.x and
                char_bot > obs_top):
                # 衝突したら True を返して結果表示へ
                return True

        return False

    def draw(self):
        pyxel.cls(0)
        # カウントダウン追加
        if self.countdown_t > 0:
            count = self.countdown_t // 60
            msg = "GO!" if count == 0 else str(count)
            pyxel.text(120, 100, msg, 7)
            return

        # 地面
        pyxel.rect(0, self.y_ground + self.char_h, 256, 4, 2)
        # キャラ
        for ry in range(masu_h):
            for rx in range(masu_w):
                c = self.dots[ry*masu_w+rx]
                if c:
                    px = self.x + rx*self.scale
                    py = self.y + ry*self.scale
                    pyxel.rect(px, py, self.scale, self.scale, IRO_LIST[c])
        # 障害物
        for o in self.obstacles:
            y = self.y_ground + self.char_h - o['h']
            pyxel.rect(o['x'], y, o['w'], o['h'], 7)
        # UI
        pyxel.text(4, 4,   f"SCORE:{self.score}", 7)
        pyxel.text(200,4,   "Q:Quit",            7)

class ResultViewer:
    def __init__(self, score, dots):
        self.score = score
        self.dots = dots

    def update(self):
        # Q で終了
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        pyxel.rectb(40, 80, 176, 100, 7)
        pyxel.text(108, 90, "Game Over!", 7)
        pyxel.text(95, 110, f"Your Score: {self.score}", 7)
        pyxel.text(85, 130, "[Space] Restart / [Q] Quit", 7)

        x = 128 - (masu_w * 2) // 2
        y = 160
        for ry in range(masu_h):
            for rx in range(masu_w):
                c = self.dots[ry * masu_w + rx]
                if c:
                    px = x + rx * 2
                    py = y + ry * 2
                    pyxel.rect(px, py, 2, 2, IRO_LIST[c])

# ここからが本当のupdate and draw のエフェzーう

phase   = "edit"
editor  = DotEditor()
runner  = None
result  = None

def update():
    global phase, editor, runner, result  # ★ここだけでOK！

    if phase == "edit":
        if editor.update():
            runner = CharViewer(editor.dot_data[:])
            phase = "run"

    elif phase == "run":
        if runner.update():
            result = ResultViewer(runner.score, runner.dots)
            phase = "result"

    elif phase == "result":
        if pyxel.btnp(pyxel.KEY_SPACE):
            editor = DotEditor()
            runner = None
            result = None
            phase = "edit"
        else:
            result.update()


def draw():
    if phase == "edit":
        editor.draw()
    elif phase == "run":
        runner.draw()
    else:
        result.draw()

pyxel.init(256, 266, title="あなたのキャラクターが走る")
pyxel.mouse(True)
pyxel.run(update, draw)
