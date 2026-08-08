import { Weapon } from './weapon.js';
import { Player } from './player.js';
import { Enemy } from './enemy.js';
import { Map } from './map.js';
import { UI } from './ui.js';

class Game {
    constructor() {
        this.isRunning = false;
        this.isPaused = false;
        this.isGameOver = false;
        this.score = 0;
        this.wave = 1;
        this.enemies = [];
        this.lastTime = 0;
        
        // 初始化 Three.js
        this.initThree();
        
        // 初始化 UI
        this.ui = new UI(this);
        
        // 创建地图
        this.map = new Map(this);
        
        // 创建玩家
        this.player = new Player(this);
        
        // 创建武器
        this.weapon = new Weapon(this, 'ak47');
        
        // 绑定事件
        this.bindEvents();
        
        // 模拟加载
        this.simulateLoading();
    }
    
    initThree() {
        // 创建场景
        this.scene = new THREE.Scene();
        
        // 创建相机
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        
        // 创建渲染器
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        // 添加到 DOM
        this.canvas = this.renderer.domElement;
        document.getElementById('game-container').appendChild(this.canvas);
        
        // 窗口大小调整
        window.addEventListener('resize', () => this.onWindowResize(), false);
    }
    
    bindEvents() {
        // 主菜单按钮
        document.getElementById('start-btn').addEventListener('click', () => {
            this.startGame();
        });
        
        document.getElementById('controls-btn').addEventListener('click', () => {
            this.ui.showControls();
        });
        
        document.getElementById('close-controls').addEventListener('click', () => {
            this.ui.hideControls();
        });
        
        // 暂停菜单按钮
        document.getElementById('resume-btn').addEventListener('click', () => {
            this.resumeGame();
        });
        
        document.getElementById('restart-btn').addEventListener('click', () => {
            this.restartGame();
        });
        
        document.getElementById('menu-btn').addEventListener('click', () => {
            this.returnToMenu();
        });
        
        // 游戏结束按钮
        document.getElementById('retry-btn').addEventListener('click', () => {
            this.restartGame();
        });
        
        document.getElementById('go-menu-btn').addEventListener('click', () => {
            this.returnToMenu();
        });
        
        // ESC 键暂停
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Escape' && this.isRunning && !this.isGameOver) {
                if (this.isPaused) {
                    this.resumeGame();
                } else {
                    this.pauseGame();
                }
            }
        });
        
        // 设置玩家控制
        this.player.setupControls();
    }
    
    simulateLoading() {
        this.ui.showLoading();
        let progress = 0;
        const interval = setInterval(() => {
            progress += 5;
            this.ui.updateLoadingProgress(progress);
            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    this.ui.hideLoading();
                    this.ui.showMainMenu();
                }, 500);
            }
        }, 50);
    }
    
    startGame() {
        this.isRunning = true;
        this.isPaused = false;
        this.isGameOver = false;
        this.score = 0;
        this.wave = 1;
        
        // 创建地图
        this.map.create();
        
        // 重置玩家
        this.player.reset();
        
        // 更新 UI
        this.ui.startGame();
        this.ui.updateScore(0);
        this.ui.updateWave(1);
        this.ui.updateWeapon(this.weapon.config.name);
        this.ui.updateAmmo(this.weapon.currentMagazine, this.weapon.currentReserve);
        
        // 生成第一波敌人
        this.spawnWave();
        
        // 开始游戏循环
        this.lastTime = performance.now();
        this.animate();
    }
    
    spawnWave() {
        const enemyCount = 3 + this.wave * 2; // 每波增加 2 个敌人
        
        for (let i = 0; i < enemyCount; i++) {
            setTimeout(() => {
                if (!this.isGameOver) {
                    this.spawnEnemy();
                }
            }, i * 1000);
        }
    }
    
    spawnEnemy() {
        const spawnPoint = this.map.getRandomEnemySpawnPoint();
        const enemy = new Enemy(this, spawnPoint);
        this.enemies.push(enemy);
    }
    
    pauseGame() {
        this.isPaused = true;
        this.ui.pauseGame();
        document.exitPointerLock();
    }
    
    resumeGame() {
        this.isPaused = false;
        this.ui.resumeGame();
        this.canvas.requestPointerLock();
        this.lastTime = performance.now();
    }
    
    restartGame() {
        // 清理现有敌人
        this.enemies.forEach(enemy => {
            if (enemy.mesh && enemy.mesh.parent) {
                this.scene.remove(enemy.mesh);
            }
        });
        this.enemies = [];
        
        this.startGame();
    }
    
    returnToMenu() {
        this.isRunning = false;
        this.isPaused = false;
        this.isGameOver = false;
        
        // 清理场景
        this.enemies.forEach(enemy => {
            if (enemy.mesh && enemy.mesh.parent) {
                this.scene.remove(enemy.mesh);
            }
        });
        this.enemies = [];
        
        this.ui.showMainMenu();
        document.exitPointerLock();
    }
    
    gameOver() {
        this.isGameOver = true;
        this.isRunning = false;
        this.ui.setFinalScore(this.score);
        this.ui.showGameOver();
        document.exitPointerLock();
    }
    
    checkWaveComplete() {
        const activeEnemies = this.enemies.filter(e => e.active).length;
        
        if (activeEnemies === 0) {
            // 波次完成
            this.wave++;
            this.ui.updateWave(this.wave);
            
            // 延迟生成下一波
            setTimeout(() => {
                if (!this.isGameOver) {
                    this.spawnWave();
                }
            }, 2000);
        }
    }
    
    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    animate() {
        if (!this.isRunning || this.isPaused) {
            requestAnimationFrame(() => this.animate());
            return;
        }
        
        const currentTime = performance.now();
        const deltaTime = Math.min((currentTime - this.lastTime) / 1000, 0.1); // 限制最大帧时间
        this.lastTime = currentTime;
        
        // 更新玩家
        this.player.update(deltaTime);
        
        // 更新敌人
        this.enemies.forEach(enemy => {
            enemy.update(deltaTime);
        });
        
        // 检查波次完成
        this.checkWaveComplete();
        
        // 渲染场景
        this.render();
        
        requestAnimationFrame(() => this.animate());
    }
    
    render() {
        this.renderer.render(this.scene, this.camera);
    }
}

// 启动游戏
window.addEventListener('load', () => {
    window.game = new Game();
});
