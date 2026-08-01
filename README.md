# SCUM-DirtySlower

SCUM 游戏服装脏污积累速度控制模组（服务端 PAK）。

## 两个版本

| 版本 | 文件 | 效果 |
|------|------|------|
| **A — 万能降低** | `SCUM-DirtySlower-A.pak` | 脏污速度降到原来的 1/3~1/5，保留表面间的相对差异 |
| **B — 几乎清零** | `SCUM-DirtySlower-B.pak` | 所有表面 DirtinessFactor = 0.01，衣服几乎永远不会脏 |

## 工作原理

修改 `PhysicalSurfacesData` 中所有 41 个表面材质的 `DirtinessFactor`（脏污系数），游戏运行时根据此系数计算衣服的脏污积累速度。

### 详细改动对照

### A 版（万能降低）

| 表面 | 原值 → 新值 |
|------|:-:|
| 泥土 / 泥浆 (Dirt / Mud) | 1.0 → **0.20** |
| 大陆森林地 (ForrestGroundContinental) | 0.7 → **0.15** |
| 沿海森林地 (ForrestGroundCoastal) | 0.5 → **0.10** |
| 草地 / 灌木 / 血肉 (Grass / Foliage / Flesh) | 0.3 → **0.06** |
| 砾石 / 沙 / 树皮 / 树叶 / 果实 | 0.2 → **0.05** |
| 硬表面（水泥 / 沥青 / 木头 / 金属 等） | 0.1 → **0.02** |
| 雪 / 冰 (Snow / Ice) | 0.01 → **0.005** |

### B 版（几乎清零）

全部 41 个表面 → **0.01**（统一雪地级别）。

## 安装

### 服务端

将其中一个 `.pak` 放入：

```
SCUMServer/Content/Paks/~mod/SCUM-DirtySlower-A.pak
```

**注意**：只放一个版本，不要同时放两个。

### 客户端

无需安装，服务端 PAK 不下发客户端。

## 构建

```bash
# 重新打包 A 版
python build_mod.py build --version A

# 重新打包 B 版
python build_mod.py build --version B
```

## 依赖

- [repak](https://github.com/trumank/repak) — UE4 PAK 打包工具
- [UAssetCLI](https://github.com/atenfyr/UAssetGUI) — .uasset ↔ JSON 转换

## 源码结构

```
source/
  version_a/  → A 版的 .uasset / .uexp / .json
  version_b/  → B 版的 .uasset / .uexp / .json
```

---

### 互补模组

- [SCUM-ChestMaxWeight](https://github.com/LHuiMeng/SCUM-ChestMaxWeight) — 箱子货舱上限提升
- [SCUM-VehicleMaxWeight](https://github.com/LHuiMeng/SCUM-VehicleMaxWeight) — 载具货舱上限提升
- [SCUM-OceanToFreshWater](https://github.com/LHuiMeng/SCUM-OceanToFreshWater) — 海水可淡化饮用
