export class Map {
    constructor(game) {
        this.game = game;
        this.obstacles = [];
    }
    
    create() {
        // 创建地面
        this.createGround();
        
        // 创建天空
        this.createSky();
        
        // 创建光照
        this.createLighting();
        
        // 创建障碍物（箱子、墙壁等）
        this.createObstacles();
        
        // 创建出生点
        this.createSpawnPoints();
    }
    
    createGround() {
        // 地面几何体
        const groundGeometry = new THREE.PlaneGeometry(100, 100);
        
        // 创建程序化纹理
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');
        
        // 填充底色（混凝土色）
        ctx.fillStyle = '#4a4a4a';
        ctx.fillRect(0, 0, 512, 512);
        
        // 添加噪点
        for (let i = 0; i < 10000; i++) {
            const x = Math.random() * 512;
            const y = Math.random() * 512;
            const gray = Math.floor(Math.random() * 50 + 50);
            ctx.fillStyle = `rgb(${gray}, ${gray}, ${gray})`;
            ctx.fillRect(x, y, 2, 2);
        }
        
        // 添加网格线
        ctx.strokeStyle = '#3a3a3a';
        ctx.lineWidth = 2;
        for (let i = 0; i <= 512; i += 64) {
            ctx.beginPath();
            ctx.moveTo(i, 0);
            ctx.lineTo(i, 512);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(0, i);
            ctx.lineTo(512, i);
            ctx.stroke();
        }
        
        const groundTexture = new THREE.CanvasTexture(canvas);
        groundTexture.wrapS = THREE.RepeatWrapping;
        groundTexture.wrapT = THREE.RepeatWrapping;
        groundTexture.repeat.set(10, 10);
        
        const groundMaterial = new THREE.MeshLambertMaterial({ 
            map: groundTexture,
            side: THREE.DoubleSide
        });
        
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = 0;
        this.game.scene.add(ground);
        this.ground = ground;
    }
    
    createSky() {
        // 简单的天空颜色
        this.game.scene.background = new THREE.Color(0x87ceeb);
        
        // 添加雾效果
        this.game.scene.fog = new THREE.Fog(0x87ceeb, 20, 80);
    }
    
    createLighting() {
        // 环境光
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.game.scene.add(ambientLight);
        
        // 方向光（太阳）
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 50, 50);
        directionalLight.castShadow = true;
        
        // 阴影配置
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 100;
        directionalLight.shadow.camera.left = -50;
        directionalLight.shadow.camera.right = 50;
        directionalLight.shadow.camera.top = 50;
        directionalLight.shadow.camera.bottom = -50;
        
        this.game.scene.add(directionalLight);
        this.sunLight = directionalLight;
    }
    
    createObstacles() {
        // 创建箱子
        this.createBoxes();
        
        // 创建墙壁
        this.createWalls();
        
        // 创建其他掩体
        this.createCover();
    }
    
    createBoxes() {
        const boxGeometry = new THREE.BoxGeometry(2, 2, 2);
        
        // 创建程序化贴图
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        
        // 木头颜色
        ctx.fillStyle = '#8B4513';
        ctx.fillRect(0, 0, 256, 256);
        
        // 木纹
        for (let i = 0; i < 50; i++) {
            const y = Math.random() * 256;
            ctx.strokeStyle = `rgba(60, 30, 10, ${Math.random() * 0.5})`;
            ctx.lineWidth = Math.random() * 3 + 1;
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.bezierCurveTo(
                64, y + Math.random() * 20 - 10,
                192, y + Math.random() * 20 - 10,
                256, y
            );
            ctx.stroke();
        }
        
        const boxTexture = new THREE.CanvasTexture(canvas);
        const boxMaterial = new THREE.MeshLambertMaterial({ map: boxTexture });
        
        // 放置多个箱子
        const boxPositions = [
            { x: 10, z: 10 },
            { x: -10, z: 10 },
            { x: 10, z: -10 },
            { x: -10, z: -10 },
            { x: 20, z: 0 },
            { x: -20, z: 0 },
            { x: 0, z: 20 },
            { x: 0, z: -20 },
            { x: 15, z: 15 },
            { x: -15, z: -15 }
        ];
        
        boxPositions.forEach(pos => {
            const box = new THREE.Mesh(boxGeometry, boxMaterial);
            box.position.set(pos.x, 1, pos.z);
            box.castShadow = true;
            box.receiveShadow = true;
            this.game.scene.add(box);
            this.obstacles.push(box);
            
            // 有些箱子叠起来
            if (Math.random() > 0.5) {
                const box2 = new THREE.Mesh(boxGeometry, boxMaterial);
                box2.position.set(pos.x, 3, pos.z);
                box2.castShadow = true;
                box2.receiveShadow = true;
                this.game.scene.add(box2);
                this.obstacles.push(box2);
            }
        });
    }
    
    createWalls() {
        const wallGeometry = new THREE.BoxGeometry(10, 4, 0.5);
        
        // 创建砖墙贴图
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        
        // 砖块颜色
        ctx.fillStyle = '#8B0000';
        ctx.fillRect(0, 0, 512, 256);
        
        // 绘制砖块
        const brickHeight = 32;
        const brickWidth = 64;
        for (let row = 0; row < 8; row++) {
            const offset = (row % 2) * 32;
            for (let col = -1; col < 9; col++) {
                const x = col * brickWidth + offset;
                const y = row * brickHeight;
                
                // 砖块主体
                ctx.fillStyle = `rgb(${100 + Math.random() * 40}, ${Math.random() * 30}, ${Math.random() * 30})`;
                ctx.fillRect(x + 2, y + 2, brickWidth - 4, brickHeight - 4);
                
                // 水泥缝
                ctx.strokeStyle = '#666';
                ctx.lineWidth = 2;
                ctx.strokeRect(x + 2, y + 2, brickWidth - 4, brickHeight - 4);
            }
        }
        
        const wallTexture = new THREE.CanvasTexture(canvas);
        const wallMaterial = new THREE.MeshLambertMaterial({ map: wallTexture });
        
        // 放置墙壁
        const wallPositions = [
            { x: 0, z: 30, rotY: 0 },
            { x: 0, z: -30, rotY: 0 },
            { x: 30, z: 0, rotY: Math.PI / 2 },
            { x: -30, z: 0, rotY: Math.PI / 2 }
        ];
        
        wallPositions.forEach(pos => {
            const wall = new THREE.Mesh(wallGeometry, wallMaterial);
            wall.position.set(pos.x, 2, pos.z);
            wall.rotation.y = pos.rotY;
            wall.castShadow = true;
            wall.receiveShadow = true;
            this.game.scene.add(wall);
            this.obstacles.push(wall);
        });
    }
    
    createCover() {
        // 创建一些圆柱形掩体
        const cylinderGeometry = new THREE.CylinderGeometry(1, 1, 2, 8);
        const cylinderMaterial = new THREE.MeshLambertMaterial({ color: 0x555555 });
        
        const coverPositions = [
            { x: 5, z: 5 },
            { x: -5, z: 15 },
            { x: 15, z: -5 },
            { x: -15, z: -5 }
        ];
        
        coverPositions.forEach(pos => {
            const cover = new THREE.Mesh(cylinderGeometry, cylinderMaterial);
            cover.position.set(pos.x, 1, pos.z);
            cover.castShadow = true;
            cover.receiveShadow = true;
            this.game.scene.add(cover);
            this.obstacles.push(cover);
        });
    }
    
    createSpawnPoints() {
        // 定义敌人出生点（远离玩家出生点）
        this.enemySpawnPoints = [
            new THREE.Vector3(20, 0, 20),
            new THREE.Vector3(-20, 0, 20),
            new THREE.Vector3(20, 0, -20),
            new THREE.Vector3(-20, 0, -20),
            new THREE.Vector3(25, 0, 0),
            new THREE.Vector3(-25, 0, 0),
            new THREE.Vector3(0, 0, 25),
            new THREE.Vector3(0, 0, -25)
        ];
        
        // 玩家出生点（地图中心）
        this.playerSpawnPoint = new THREE.Vector3(0, 1, 0);
    }
    
    getRandomEnemySpawnPoint() {
        const index = Math.floor(Math.random() * this.enemySpawnPoints.length);
        return this.enemySpawnPoints[index].clone();
    }
    
    getPlayerSpawnPoint() {
        return this.playerSpawnPoint.clone();
    }
}
