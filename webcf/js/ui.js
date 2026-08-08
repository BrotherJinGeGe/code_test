export class UI {
    constructor(game) {
        this.game = game;
        
        // 缓存UI元素
        this.healthFill = document.getElementById('health-fill');
        this.healthText = document.getElementById('health-text');
        this.ammoText = document.getElementById('ammo-text');
        this.weaponName = document.getElementById('weapon-name');
        this.scoreText = document.getElementById('score-text');
        this.waveText = document.getElementById('wave-text');
        this.killFeed = document.getElementById('kill-feed');
        
        // 加载界面
        this.loadingScreen = document.getElementById('loading-screen');
        this.loadingProgress = document.getElementById('loading-progress');
        
        // 菜单
        this.mainMenu = document.getElementById('main-menu');
        this.gameUI = document.getElementById('game-ui');
        this.pauseMenu = document.getElementById('pause-menu');
        this.gameOver = document.getElementById('game-over');
        this.controlsModal = document.getElementById('controls-modal');
    }
    
    showLoading() {
        this.loadingScreen.classList.remove('hidden');
    }
    
    hideLoading() {
        this.loadingScreen.classList.add('hidden');
    }
    
    updateLoadingProgress(progress) {
        this.loadingProgress.style.width = `${progress}%`;
    }
    
    showMainMenu() {
        this.mainMenu.classList.remove('hidden');
        this.gameUI.classList.add('hidden');
    }
    
    startGame() {
        this.mainMenu.classList.add('hidden');
        this.gameUI.classList.remove('hidden');
        this.pauseMenu.classList.add('hidden');
        this.gameOver.classList.add('hidden');
    }
    
    pauseGame() {
        this.pauseMenu.classList.remove('hidden');
    }
    
    resumeGame() {
        this.pauseMenu.classList.add('hidden');
    }
    
    showGameOver() {
        this.gameOver.classList.remove('hidden');
    }
    
    updateHealth(health, maxHealth) {
        const percent = (health / maxHealth) * 100;
        this.healthFill.style.width = `${percent}%`;
        this.healthText.textContent = Math.ceil(health);
        
        // 根据血量改变颜色
        if (percent > 50) {
            this.healthFill.style.background = 'linear-gradient(90deg, #44ff44, #66ff66)';
        } else if (percent > 25) {
            this.healthFill.style.background = 'linear-gradient(90deg, #ffff44, #ffff66)';
        } else {
            this.healthFill.style.background = 'linear-gradient(90deg, #ff4444, #ff6666)';
        }
    }
    
    updateAmmo(magazine, reserve) {
        this.ammoText.textContent = `${magazine}/${reserve}`;
        
        // 低弹药警告
        if (magazine <= 5) {
            this.ammoText.style.color = '#ff4444';
        } else {
            this.ammoText.style.color = '#fff';
        }
    }
    
    updateWeapon(name) {
        this.weaponName.textContent = name;
    }
    
    updateScore(score) {
        this.scoreText.textContent = score;
    }
    
    updateWave(wave) {
        this.waveText.textContent = wave;
    }
    
    showReloadIndicator() {
        this.ammoText.textContent = '换弹中...';
        this.ammoText.style.color = '#ffff00';
    }
    
    hideReloadIndicator() {
        // 会在 updateAmmo 中恢复正常显示
    }
    
    showKillMessage(message) {
        const killMsg = document.createElement('div');
        killMsg.className = 'kill-message';
        killMsg.textContent = message;
        this.killFeed.appendChild(killMsg);
        
        // 3 秒后移除
        setTimeout(() => {
            killMsg.remove();
        }, 3000);
    }
    
    showControls() {
        this.controlsModal.classList.remove('hidden');
    }
    
    hideControls() {
        this.controlsModal.classList.add('hidden');
    }
    
    setFinalScore(score) {
        document.getElementById('final-score').textContent = score;
    }
}
