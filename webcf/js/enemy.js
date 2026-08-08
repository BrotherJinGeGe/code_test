export class Enemy {
    constructor(game, position) {
        this.game = game;
        this.active = true;
        this.health = 100;
        this.maxHealth = 100;
        this.speed = 2 + Math.random() * 2; // 随机速度
        this.damage = 10;
        this.attackRange = 2;
        this.lastAttackTime = 0;
        this.attackCooldown = 1000;
        
        // 创建敌人模型
        this.createMesh(position);
    }
    
    createMesh(position) {
        const enemyGroup = new THREE.Group();
        
        // 身体
        const bodyGeometry = new THREE.CylinderGeometry(0.3, 0.4, 1.2, 8);
        const bodyMaterial = new THREE.MeshLambertMaterial({ color: 0x8B0000 });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.position.y = 0.6;
        enemyGroup.add(body);
        
        // 头部
        const headGeometry = new THREE.SphereGeometry(0.25, 8, 8);
        const headMaterial = new THREE.MeshLambertMaterial({ color: 0xFFD700 });
        const head = new THREE.Mesh(headGeometry, headMaterial);
        head.position.y = 1.4;
        enemyGroup.add(head);
        this.headMesh = head;
        
        // 手臂
        const armGeometry = new THREE.CylinderGeometry(0.1, 0.1, 0.6, 6);
        const armMaterial = new THREE.MeshLambertMaterial({ color: 0x8B0000 });
        
        const leftArm = new THREE.Mesh(armGeometry, armMaterial);
        leftArm.position.set(-0.4, 0.8, 0);
        leftArm.rotation.z = 0.5;
        enemyGroup.add(leftArm);
        
        const rightArm = new THREE.Mesh(armGeometry, armMaterial);
        rightArm.position.set(0.4, 0.8, 0);
        rightArm.rotation.z = -0.5;
        enemyGroup.add(rightArm);
        
        // 腿部
        const legGeometry = new THREE.CylinderGeometry(0.12, 0.12, 0.7, 6);
        const legMaterial = new THREE.MeshLambertMaterial({ color: 0x2F4F4F });
        
        const leftLeg = new THREE.Mesh(legGeometry, legMaterial);
        leftLeg.position.set(-0.2, 0.35, 0);
        enemyGroup.add(leftLeg);
        
        const rightLeg = new THREE.Mesh(legGeometry, legMaterial);
        rightLeg.position.set(0.2, 0.35, 0);
        enemyGroup.add(rightLeg);
        
        // 设置位置
        enemyGroup.position.copy(position);
        this.game.scene.add(enemyGroup);
        this.mesh = enemyGroup;
        
        // 添加血条
        this.createHealthBar();
    }
    
    createHealthBar() {
        const barGroup = new THREE.Group();
        
        // 背景
        const bgGeometry = new THREE.PlaneGeometry(1, 0.1);
        const bgMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 });
        const bg = new THREE.Mesh(bgGeometry, bgMaterial);
        barGroup.add(bg);
        
        // 血量填充
        this.healthBarGeometry = new THREE.PlaneGeometry(0.96, 0.08);
        const healthBarMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
        this.healthBar = new THREE.Mesh(this.healthBarGeometry, healthBarMaterial);
        this.healthBar.position.z = 0.01;
        barGroup.add(this.healthBar);
        
        barGroup.position.y = 2.2;
        this.mesh.add(barGroup);
        this.healthBarGroup = barGroup;
    }
    
    update(deltaTime) {
        if (!this.active) return;
        
        // 获取玩家位置
        const playerPos = this.game.player.position;
        const enemyPos = this.mesh.position;
        
        // 计算到玩家的距离
        const distance = enemyPos.distanceTo(playerPos);
        
        // 简单的AI：向玩家移动
        if (distance > this.attackRange) {
            const direction = new THREE.Vector3()
                .subVectors(playerPos, enemyPos)
                .normalize();
            
            // 忽略Y轴，只在地面移动
            direction.y = 0;
            direction.normalize();
            
            // 移动
            const moveDistance = this.speed * deltaTime;
            this.mesh.position.add(direction.multiplyScalar(moveDistance));
            
            // 面向玩家
            this.mesh.lookAt(playerPos.x, enemyPos.y, playerPos.z);
        } else {
            // 攻击玩家
            this.attack();
        }
        
        // 更新血条朝向（始终面向相机）
        if (this.healthBarGroup) {
            this.healthBarGroup.lookAt(this.game.camera.position);
        }
    }
    
    attack() {
        const now = Date.now();
        if (now - this.lastAttackTime < this.attackCooldown) return;
        
        this.lastAttackTime = now;
        
        // 对玩家造成伤害
        this.game.player.takeDamage(this.damage);
        
        // 显示攻击提示
        this.showAttackIndicator();
    }
    
    takeDamage(amount) {
        this.health -= amount;
        
        // 更新血条
        this.updateHealthBar();
        
        // 受伤效果（闪烁）
        this.flashRed();
        
        // 检查死亡
        if (this.health <= 0) {
            this.die();
        }
    }
    
    updateHealthBar() {
        if (!this.healthBar) return;
        
        const healthPercent = this.health / this.maxHealth;
        this.healthBar.scale.x = healthPercent;
        
        // 根据血量改变颜色
        if (healthPercent > 0.5) {
            this.healthBar.material.color.setHex(0x00ff00);
        } else if (healthPercent > 0.25) {
            this.healthBar.material.color.setHex(0xffff00);
        } else {
            this.healthBar.material.color.setHex(0xff0000);
        }
    }
    
    flashRed() {
        // 简单闪烁效果
        this.mesh.children.forEach(child => {
            if (child.material) {
                const originalColor = child.material.color.getHex();
                child.material.color.setHex(0xff0000);
                setTimeout(() => {
                    child.material.color.setHex(originalColor);
                }, 100);
            }
        });
    }
    
    showAttackIndicator() {
        // 可以在UI上显示被攻击提示
        const indicator = document.createElement('div');
        indicator.className = 'damage-indicator';
        indicator.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100vw;
            height: 100vh;
            border: 5px solid red;
            border-radius: 50%;
            pointer-events: none;
            animation: fadeOut 0.5s forwards;
        `;
        document.getElementById('game-ui').appendChild(indicator);
        
        setTimeout(() => {
            indicator.remove();
        }, 500);
    }
    
    die() {
        this.active = false;
        
        // 播放死亡动画（简化版：倒下）
        this.mesh.rotation.x = -Math.PI / 2;
        this.mesh.position.y = 0.3;
        
        // 增加得分
        this.game.score += 100;
        this.game.ui.updateScore(this.game.score);
        
        // 显示击杀提示
        this.game.ui.showKillMessage('消灭敌人 +100');
        
        // 延迟移除
        setTimeout(() => {
            if (this.mesh && this.mesh.parent) {
                this.game.scene.remove(this.mesh);
            }
        }, 3000);
    }
}
