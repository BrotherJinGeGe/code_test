// 武器配置数据
export const WEAPONS = {
    ak47: {
        name: 'AK-47',
        damage: 35,
        fireRate: 100, // 毫秒/发
        magazineSize: 30,
        reserveAmmo: 90,
        reloadTime: 2000,
        spread: 0.05,
        range: 100,
        auto: true,
        color: 0x8B4513
    },
    m4a1: {
        name: 'M4A1',
        damage: 30,
        fireRate: 80,
        magazineSize: 30,
        reserveAmmo: 90,
        reloadTime: 2200,
        spread: 0.03,
        range: 100,
        auto: true,
        color: 0x2F4F4F
    },
    awm: {
        name: 'AWM',
        damage: 100,
        fireRate: 1500,
        magazineSize: 5,
        reserveAmmo: 30,
        reloadTime: 3000,
        spread: 0.001,
        range: 200,
        auto: false,
        color: 0x006400
    },
    pistol: {
        name: '手枪',
        damage: 25,
        fireRate: 200,
        magazineSize: 12,
        reserveAmmo: 48,
        reloadTime: 1500,
        spread: 0.02,
        range: 50,
        auto: false,
        color: 0x708090
    }
};

export class Weapon {
    constructor(game, weaponType = 'ak47') {
        this.game = game;
        this.config = WEAPONS[weaponType];
        this.type = weaponType;
        
        this.currentMagazine = this.config.magazineSize;
        this.currentReserve = this.config.reserveAmmo;
        this.isReloading = false;
        this.lastFireTime = 0;
        this.isAiming = false;
        
        // 创建武器模型（简单几何体）
        this.createWeaponModel();
    }
    
    createWeaponModel() {
        // 使用 Three.js 几何体创建简单的武器模型
        const weaponGroup = new THREE.Group();
        
        // 枪身
        const bodyGeometry = new THREE.BoxGeometry(0.1, 0.15, 0.6);
        const bodyMaterial = new THREE.MeshLambertMaterial({ color: this.config.color });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        weaponGroup.add(body);
        
        // 枪管
        const barrelGeometry = new THREE.CylinderGeometry(0.03, 0.03, 0.4, 8);
        const barrelMaterial = new THREE.MeshLambertMaterial({ color: 0x333333 });
        const barrel = new THREE.Mesh(barrelGeometry, barrelMaterial);
        barrel.rotation.x = Math.PI / 2;
        barrel.position.set(0, 0.05, -0.4);
        weaponGroup.add(barrel);
        
        // 握把
        const gripGeometry = new THREE.BoxGeometry(0.08, 0.2, 0.1);
        const gripMaterial = new THREE.MeshLambertMaterial({ color: 0x1a1a1a });
        const grip = new THREE.Mesh(gripGeometry, gripMaterial);
        grip.position.set(0, -0.15, 0.2);
        grip.rotation.x = 0.2;
        weaponGroup.add(grip);
        
        // 瞄准镜（仅狙击枪）
        if (this.type === 'awm') {
            const scopeGeometry = new THREE.CylinderGeometry(0.04, 0.04, 0.15, 8);
            const scopeMaterial = new THREE.MeshLambertMaterial({ color: 0x111111 });
            const scope = new THREE.Mesh(scopeGeometry, scopeMaterial);
            scope.rotation.z = Math.PI / 2;
            scope.position.set(0, 0.12, 0);
            weaponGroup.add(scope);
        }
        
        // 将武器添加到相机
        weaponGroup.position.set(0.3, -0.25, -0.5);
        this.game.camera.add(weaponGroup);
        this.weaponModel = weaponGroup;
    }
    
    fire() {
        const now = Date.now();
        
        // 检查是否可以射击
        if (this.isReloading) return false;
        if (this.currentMagazine <= 0) {
            this.reload();
            return false;
        }
        if (now - this.lastFireTime < this.config.fireRate) return false;
        
        this.lastFireTime = now;
        this.currentMagazine--;
        
        // 更新UI
        this.game.ui.updateAmmo(this.currentMagazine, this.currentReserve);
        
        // 创建子弹轨迹
        this.createBulletTrail();
        
        // 检测命中
        this.checkHit();
        
        // 后坐力
        this.applyRecoil();
        
        return true;
    }
    
    createBulletTrail() {
        // 从武器位置到准星方向的射线
        const start = new THREE.Vector3();
        const end = new THREE.Vector3();
        
        // 获取武器世界坐标
        this.weaponModel.getWorldPosition(start);
        
        // 计算射击方向（从相机中心）
        const direction = new THREE.Vector3();
        this.game.camera.getWorldDirection(direction);
        
        // 添加散布
        if (!this.isAiming) {
            direction.x += (Math.random() - 0.5) * this.config.spread;
            direction.y += (Math.random() - 0.5) * this.config.spread;
        }
        direction.normalize();
        
        end.copy(start).add(direction.multiplyScalar(this.config.range));
        
        // 创建轨迹线
        const points = [start, end];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({ 
            color: 0xffff00,
            transparent: true,
            opacity: 0.8
        });
        const trail = new THREE.Line(geometry, material);
        this.game.scene.add(trail);
        
        // 短暂显示后移除
        setTimeout(() => {
            this.game.scene.remove(trail);
            geometry.dispose();
            material.dispose();
        }, 50);
    }
    
    checkHit() {
        const direction = new THREE.Vector3();
        this.game.camera.getWorldDirection(direction);
        
        // 添加散布
        if (!this.isAiming) {
            direction.x += (Math.random() - 0.5) * this.config.spread;
            direction.y += (Math.random() - 0.5) * this.config.spread;
        }
        direction.normalize();
        
        const raycaster = new THREE.Raycaster(
            this.game.camera.position,
            direction,
            0,
            this.config.range
        );
        
        // 检测与敌人的碰撞
        const enemies = this.game.enemies.filter(enemy => enemy.active);
        const enemyMeshes = enemies.map(enemy => enemy.mesh);
        
        const intersects = raycaster.intersectObjects(enemyMeshes);
        
        if (intersects.length > 0) {
            const hitObject = intersects[0].object;
            const enemy = enemies.find(e => e.mesh === hitObject || e.mesh.children.includes(hitObject));
            
            if (enemy) {
                enemy.takeDamage(this.config.damage);
                
                // 爆头判定（击中头部造成双倍伤害）
                if (hitObject === enemy.headMesh) {
                    enemy.takeDamage(this.config.damage);
                }
            }
        }
    }
    
    applyRecoil() {
        // 简单的后坐力效果
        const recoilAmount = this.isAiming ? 0.02 : 0.05;
        this.game.camera.rotation.x += recoilAmount;
    }
    
    reload() {
        if (this.isReloading || this.currentMagazine === this.config.magazineSize) return;
        if (this.currentReserve <= 0) return;
        
        this.isReloading = true;
        this.game.ui.showReloadIndicator();
        
        // 播放换弹动画（简化版）
        this.weaponModel.rotation.x = -0.5;
        
        setTimeout(() => {
            const needed = this.config.magazineSize - this.currentMagazine;
            const available = Math.min(needed, this.currentReserve);
            
            this.currentMagazine += available;
            this.currentReserve -= available;
            
            this.isReloading = false;
            this.weaponModel.rotation.x = 0;
            
            this.game.ui.updateAmmo(this.currentMagazine, this.currentReserve);
            this.game.ui.hideReloadIndicator();
        }, this.config.reloadTime);
    }
    
    setAiming(aiming) {
        this.isAiming = aiming;
        
        // 瞄准时的武器位置调整
        const targetPos = aiming ? 
            new THREE.Vector3(0, -0.15, -0.3) : 
            new THREE.Vector3(0.3, -0.25, -0.5);
        
        // 平滑过渡（简化版直接设置）
        this.weaponModel.position.lerp(targetPos, 0.2);
    }
    
    switchWeapon(weaponType) {
        if (this.isReloading) return;
        
        // 移除旧武器模型
        if (this.weaponModel) {
            this.game.camera.remove(this.weaponModel);
        }
        
        // 创建新武器
        this.type = weaponType;
        this.config = WEAPONS[weaponType];
        this.currentMagazine = this.config.magazineSize;
        this.currentReserve = this.config.reserveAmmo;
        
        this.createWeaponModel();
        this.game.ui.updateWeapon(this.config.name);
        this.game.ui.updateAmmo(this.currentMagazine, this.currentReserve);
    }
}
