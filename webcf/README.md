# WebCF - 网页版穿越火线射击游戏

## 项目简介
这是一个使用纯前端技术（HTML5 + Three.js）开发的简易第一人称射击游戏，模拟 CF（穿越火线）的核心玩法。

## 快速开始

### 方法一：直接打开
1. 在浏览器中直接打开 `webcf/index.html` 文件
2. 点击"开始游戏"按钮
3. 点击游戏画面锁定鼠标，开始游戏

### 方法二：使用本地服务器（推荐）
由于浏览器的安全限制，建议使用本地服务器运行：

```bash
# 使用 Python
cd webcf
python -m http.server 8080

# 或使用 Node.js
npx serve webcf

# 然后访问 http://localhost:8080
```

## 操作说明

| 按键 | 功能 |
|------|------|
| W/A/S/D | 移动 |
| 鼠标移动 | 控制视角 |
| 左键 | 射击 |
| 右键 | 瞄准（降低后坐力） |
| R | 换弹 |
| 空格 | 跳跃 |
| Shift | 奔跑 |
| 1/2/3/4 | 切换武器（AK47/M4A1/AWM/手枪） |
| ESC | 暂停 |

## 游戏特性

### 武器系统
- **AK-47**: 高伤害，中等后坐力
- **M4A1**: 平衡型，低后坐力
- **AWM**: 狙击枪，高伤害，慢射速
- **手枪**: 备用武器

### 敌人 AI
- 自动追踪玩家
- 近战攻击
- 血量显示
- 死亡动画

### 游戏模式
- 生存模式（波次防御）
- 每波敌人数量递增
- 得分系统

## 项目结构

```
webcf/
├── index.html          # 主页面
├── css/
│   └── style.css      # 样式文件
├── js/
│   ├── main.js        # 游戏入口和主循环
│   ├── player.js      # 玩家控制
│   ├── weapon.js      # 武器系统
│   ├── enemy.js       # 敌人 AI
│   ├── map.js         # 地图生成
│   └── ui.js          # UI 管理
└── assets/            # 资源目录（可选）
```

## 技术栈

- **Three.js**: 3D 渲染引擎
- **HTML5/CSS3**: 界面和样式
- **ES6 Modules**: 模块化 JavaScript

## 自定义和扩展

### 添加新武器
编辑 `js/weapon.js` 中的 `WEAPONS` 对象：

```javascript
newWeapon: {
    name: '新武器',
    damage: 50,
    fireRate: 150,
    magazineSize: 20,
    reserveAmmo: 60,
    reloadTime: 2500,
    spread: 0.04,
    range: 80,
    auto: true,
    color: 0xFF0000
}
```

### 修改地图
编辑 `js/map.js` 中的地图生成逻辑，可以：
- 调整地图大小
- 添加更多障碍物
- 修改出生点位置

### 更换贴图
当前版本使用程序生成的贴图。你可以：
1. 准备 PNG/JPG 格式的贴图文件
2. 放入 `assets/textures/` 目录
3. 在 `map.js` 中使用 `THREE.TextureLoader` 加载

示例：
```javascript
const texture = new THREE.TextureLoader().load('assets/textures/ground.jpg');
```

### 添加 3D 模型
从以下网站获取免费模型：
- [Sketchfab](https://sketchfab.com) - 搜索免费可商用的 GLTF/GLB 模型
- [Kenney.nl](https://kenney.nl/assets) - 免费游戏资产包
- [Poly Haven](https://polyhaven.com) - 免费高质量贴图和模型

加载示例：
```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const loader = new GLTFLoader();
loader.load('assets/models/ak47.glb', (gltf) => {
    this.weaponModel = gltf.scene;
});
```

## 性能优化建议

1. **减少面数**: 使用低多边形模型
2. **贴图压缩**: 使用 WebP 格式，分辨率不超过 2K
3. **实例化渲染**: 大量相同物体使用 `InstancedMesh`
4. **阴影质量**: 根据设备性能调整阴影分辨率
5. **雾效果**: 限制可视距离，减少渲染负担

## 浏览器兼容性

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 注意事项

1. **指针锁定**: 游戏需要鼠标指针锁定功能，某些浏览器可能需要用户交互才能启用
2. **WebGL 支持**: 确保浏览器启用了 WebGL
3. **性能**: 在低端设备上可能需要降低画质设置

## 后续开发计划

- [ ] 添加更多武器
- [ ] 多人联机模式
- [ ] 更多地图场景
- [ ] 成就系统
- [ ] 武器皮肤系统
- [ ] 更智能的敌人 AI
- [ ] 音效系统

## 许可证

本项目为学习演示用途，所有代码和资源请遵守相应的开源协议。

## 致谢

感谢 Three.js 社区提供的优秀工具和资源！
