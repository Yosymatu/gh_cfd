import Rhino
import scriptcontext
import System.Guid
import rhinoscriptsyntax as rs

class CFD:
    def __init__(self):
        self.WX = 12            #壁x位置
        self.WY = 12            #壁y位置
        self.vx = [[0] * WX+1 for i in range(WY)]         #速度x成分[配列]
        self.vx_after = [[0] * WX+1 for i in range(WY)]    #修正後速度x成分
        self.vy = [[0] * WX for i in range(WY+1)]          #速度y成分
        self.vy_after = [[0] * WX for i in range(WY+1)]     #修正後速度y成分
        self.s = [[0] * WX for i in range(WY)]

        self.p = [[0] * WX for i in range(WY)]             #圧力
        self.p_after = [[0] * WX for i in range(WY)]       #修正後圧力
        self.rys =  [[0] * 1024 for i in range(2)]         #粒子のx,y座標
        self.delta_t = 0.2           #デルタT
        self.Re=1000000.0            #レイノルズ数
        self.omega=1.8               #加速係数

    #移流
    def Adve(self):
        #vx の更新
        for i in range(WX-2):
            for j in range(WY-2):
                u = vx[i][j]
                v = (vx[i - 1][j] + vx[i][j] + vx[i - 1][j + 1] + vx[i][j + 1]) / 4
                if u>= 0 and v >= 0:
                    vx_after[i][j] = vx[i][j] - u*(vx[i][j] - vx[i -1][j])*delta_t - v * (vx[i][j] - vx[i][j-1]) * delta_t
                else if u < 0 and v >= 0:
                    vx_after[i][j] = vx[i][j] - u*(vx[i + 1][j] - vx[i][j])*delta_t - v * (vx[i][j] - vx[i][j-1]) * delta_t
                else if u >= 0 and v < 0:
                    vx_after[i][j] = vx[i][j] - u*(vx[i][j] - vx[i - 1][j])*delta_t - v * (vx[i][j + 1] - vx[i][j]) * delta_t
                else if u < 0 and v < 0:
                    vx_after[i][j] = vx[i][j] - u*(vx[i + 1][j] - vx[i][j])*delta_t - v * (vx[i][j + 1] - vx[i][j]) * delta_t

        #vy の更新
        for i in range(WX-2):
            for j in range(WY-2):
                u = (vy[i][j - 1] + vy[i + 1][j - 1] + vy[i][j] + vy[i + 1][j]) / 4
                v = vy[i][j]

                if u>= 0 and v >= 0:
                    vy_after[i][j] = vy[i][j] - u*(vy[i][j] - vy[i -1][j])*delta_t - v * (vy[i][j] - vy[i][j-1]) * delta_t
                else if u < 0 and v >= 0:
                    vy_after[i][j] = vy[i][j] - u*(vy[i + 1][j] - vy[i][j])*delta_t - v * (vy[i][j] - vy[i][j-1]) * delta_t
                else if u >= 0 and v < 0:
                    vy_after[i][j] = vy[i][j] - u*(vy[i][j] - vy[i - 1][j])*delta_t - v * (vy[i][j + 1] - vy[i][j]) * delta_t
                else if u < 0 and v < 0:
                    vy_after[i][j] = vy[i][j] - u*(vy[i + 1][j] - vy[i][j])*delta_t - v * (vy[i][j + 1] - vy[i][j]) * delta_t

        return vx, vx_after, 8*(WX+1)*WY, vy, vy_after, 8*WX*(WY+1)

    #粘性
    def Viscosity(self):
        for i in range(WX-2):
            for  j in range(WY-2):
                vx_after[i][j] = vx.[i][j] -1 / Re * (vx[i + 1][j] + vx[i][j + 1] + vx[i - 1][j] + vx[i][j - 1])*delta_t
                vy_after[i][j] = vy.[i][j] -1 / Re * (vy[i + 1][j] + vy[i][j + 1] + vy[i - 1][j] + vy[i][j - 1])*delta_t
        return vx, vx_after, 8*(WX+1)*WY, vy, vyafter, 8*WX*(WY+1)

    # 壁の設定
    def Set(self):
        for i in range(WX):
            for j in range(WY):
                if i == 0 or i == WX-1 or j == 0 or j = WY - 1:
                    vx[i][j] = 0
                    vx[i + 1][j] == 0
                    vy[i][j] == 0
                    vy[i][j + 1] == 0
        return

    # ダイバージェンスの計算
    def Div(self):
        for i in range(WX-2):
            for j in range(WY-2):
                s[i][j] = (-vx[i][j] - vy[i][j] + vx[i+1][j] + vy[i][j+1]) / delta_t
        return

    # 圧力のポアソン方程式
    def Poisson(self):
        for n in range(100):
            for i in range(WX-2):
                for j in range(WY-2):
                    if i == 1:
                        p[i - 1][j] = p[i][j]
                    else if i == WX-2:
                        p[i + 1][j] = p[i][j]
                    else if j == 1:
                        p[i][j - 1] = p[i][j]
                    else if j == WY-2:
                        p[i][j + 1] = p[i][j]
                    
                    p[i][j] = (1 - omega)*p[i][j] + omega/4*(p[i - 1][j] + p[i + 1][j] + p[i][j - 1] + p[i][j + 1] - s[i][j])
        return

    #修正項
    def Rhs(self):
        for i in range(WX-2):
            for j in range(WY-2):
                vx[i][j] -= (p[i][j] - p[i - 1][j]) * delta_t
                vy[i][j] -= (p[i][j] - p[i][j - 1]) * delta_t
        return

# メッシュの作成
def AddMesh

def main():
    # mesh = AddMesh()
    while 0:
        cfd = CFD()
        cfd.Adve()
        cfd.Viscosity()
        cfd.Set()
        cfd.Div()
        cfd.Poisson()
        cfd.Rhs()




if __name__ == '__main__()':
    main()
