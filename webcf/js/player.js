export class Player {
    constructor(game) {
        this.game = game;
        
        // 玩家属性
        this.health = 100;
        this.maxHealth = 100;
        this.speed = 5;
        this.sprintSpeed = 8;
        this.jumpForce = 8;
        
        // 运动状态
        this.velocity = new THREE.Vector3();
        this.direction = new THREE.Vector3();
        this.isGrounded = false;
        this.isSprinting = false;
        
        // 输入状态
        this.moveForward = false;
        this.moveBackward = false;
        this.moveLeft = false;
        this.moveRight = false;
        this.canJump = true;
        
        // 相机控制
        this.euler = new THREE.Euler(0, 0, 0, 'YXZ');
        this.PI_2 = Math.PI / 2;
        
        // 创建玩家对象（用于碰撞检测）
        this.createPlayerMesh();
    }
    
    createPlayerMesh() {
        // 简单的玩家表示（第一人称不可见，但用于物理）
        const geometry = new THREE.CapsuleGeometry(0.5, 1, 4, 8);
        const material = new THREE.MeshBasicMaterial({ 
            color: 0x00ff00,
            transparent: true,
            opacity: 0.3,
            visible: false // 第一人称不需要看到自己
        });
        this.mesh = new THREE.Mesh(geometry, material);
        this.mesh.position.copy(this.game.map.getPlayerSpawnPoint());
        this.game.scene.add(this.mesh);
        
        // 初始位置
        this.position = this.mesh.position.clone();
    }
    
    setupControls() {
        // 键盘事件
        document.addEventListener('keydown', (e) => this.onKeyDown(e));
        document.addEventListener('keyup', (e) => this.onKeyUp(e));
        
        // 鼠标事件
        document.addEventListener('mousemove', (e) => this.onMouseMove(e));
        document.addEventListener('mousedown', (e) => this.onMouseDown(e));
        document.addEventListener('mouseup', (e) => this.onMouseUp(e));
        
        // 指针锁定
        this.game.canvas.addEventListener('click', () => {
            if (!this.game.isPaused && !this.game.isGameOver) {
                this.game.canvas.requestPointerLock();
            }
        });
    }
    
    onKeyDown(event) {
        switch (event.code) {
            case 'KeyW':
                this.moveForward = true;
                break;
            case 'KeyS':
                this.moveBackward = true;
                break;
            case 'KeyA':
                this.moveLeft = true;
                break;
            case 'KeyD':
                this.moveRight = true;
                break;
            case 'Space':
                if (this.isGrounded && this.canJump) {
                    this.velocity.y = this.jumpForce;
                    this.isGrounded = false;
                    this.canJump = false;
                }
                break;
            case 'ShiftLeft':
                this.isSprinting = true;
                break;
            case 'KeyR':
                this.game.weapon.reload();
                break;
            case 'Digit1':
                this.game.weapon.switchWeapon('ak47');
                break;
            case 'Digit2':
                this.game.weapon.switchWeapon('m4a1');
                break;
            case 'Digit3':
                this.game.weapon.switchWeapon('awm');
                break;
            case 'Digit4':
                this.game.weapon.switchWeapon('pistol');
                break;
        }
    }
    
    onKeyUp(event) {
        switch (event.code) {
            case 'KeyW':
                this.moveForward = false;
                break;
            case 'KeyS':
                this.moveBackward = false;
                break;
            case 'KeyA':
                this.moveLeft = false;
                break;
            case 'KeyD':
                this.moveRight = false;
                break;
            case 'ShiftLeft':
                this.isSprinting = false;
                break;
        }
    }
    
    onMouseMove(event) {
        if (document.pointerLockElement !== this.game.canvas) return;
        
        const movementX = event.movementX || 0;
        const movementY = event.movementY || 0;
        
        // 更新视角
        this.euler.setFromQuaternion(this.game.camera.quaternion);
        this.euler.y -= movementX * 0.002;
        this.euler.x -= movementY * 0.002;
        this.euler.x = Math.max(-this.PI_2, Math.min(this.PI_2, this.euler.x));
        
        this.game.camera.quaternion.setFromEuler(this.euler);
    }
    
    onMouseDown(event) {
        if (document.pointerLockElement !== this.game.canvas) return;
        
        if (event.button === 0) { // 左键
            this.isFiring = true;
            if (!this.game.weapon.config.auto) {
                this.game.weapon.fire();
            }
        } else if (event.button === 2) { // 右键
            this.game.weapon.setAiming(true);
        }
    }
    
    onMouseUp(event) {
        if (event.button === 0) {
            this.isFiring = false;
        } else if (event.button === 2) {
            this.game.weapon.setAiming(false);
        }
    }
    
    update(deltaTime) {
        // 应用重力
        this.velocity.y -= 20 * deltaTime;
        
        // 计算移动方向
        this.direction.z = Number(this.moveForward) - Number(this.moveBackward);
        this.direction.x = Number(this.moveRight) - Number(this.moveLeft);
        this.direction.normalize();
        
        // 获取当前速度
        const currentSpeed = this.isSprinting ? this.sprintSpeed : this.speed;
        
        // 应用移动
        if (this.moveForward || this.moveBackward) {
            this.velocity.z = -this.direction.z * currentSpeed;
        } else {
            this.velocity.z = 0;
        }
        
        if (this.moveLeft || this.moveRight) {
            this.velocity.x = -this.direction.x * currentSpeed;
        } else {
            this.velocity.x = 0;
        }
        
        // 应用速度到位置（考虑相机方向）
        const cameraDirection = new THREE.Vector3();
        this.game.camera.getWorldDirection(cameraDirection);
        cameraDirection.y = 0;
        cameraDirection.normalize();
        
        const cameraRight = new THREE.Vector3();
        cameraRight.crossVectors(cameraDirection, new THREE.Vector3(0, 1, 0));
        
        // 计算实际移动向量
        const moveVector = new THREE.Vector3();
        moveVector.addScaledVector(cameraDirection, -this.velocity.z * deltaTime);
        moveVector.addScaledVector(cameraRight, this.velocity.x * deltaTime);
        
        // 更新位置
        this.mesh.position.add(moveVector);
        this.mesh.position.y += this.velocity.y * deltaTime;
        
        // 地面碰撞检测
        if (this.mesh.position.y <= 1) {
            this.mesh.position.y = 1;
            this.velocity.y = 0;
            this.isGrounded = true;
            this.canJump = true;
        }
        
        // 边界限制
        const limit = 49;
        this.mesh.position.x = Math.max(-limit, Math.min(limit, this.mesh.position.x));
        this.mesh.position.z = Math.max(-limit, Math.min(limit, this.mesh.position.z));
        
        // 同步相机位置
        this.game.camera.position.copy(this.mesh.position);
        this.game.camera.position.y += 0.6; // 眼睛高度
        
        // 更新玩家位置引用
        this.position = this.mesh.position.clone();
        
        // 自动武器连射
        if (this.isFiring && this.game.weapon.config.auto) {
            this.game.weapon.fire();
        }
        
        // 跳跃后允许再次跳跃的冷却
        if (!this.isGrounded) {
            setTimeout(() => {
                this.canJump = true;
            }, 300);
        }
    }
    
    takeDamage(amount) {
        this.health -= amount;
        this.game.ui.updateHealth(this.health, this.maxHealth);
        
        // 检查死亡
        if (this.health <= 0) {
            this.die();
        }
    }
    
    die() {
        this.game.gameOver();
    }
    
    reset() {
        this.health = this.maxHealth;
        this.velocity.set(0, 0, 0);
        this.mesh.position.copy(this.game.map.getPlayerSpawnPoint());
        this.game.camera.position.copy(this.mesh.position);
        this.game.camera.position.y += 0.6;
        this.game.camera.rotation.set(0, 0, 0);
        this.euler.set(0, 0, 0);
        this.game.ui.updateHealth(this.health, this.maxHealth);
    }
}
