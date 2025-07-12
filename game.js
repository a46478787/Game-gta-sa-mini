// GTA San Andreas - Минимальная версия
class GTAGame {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.player = null;
        this.buildings = [];
        this.vehicles = [];
        this.health = 100;
        this.keys = {};
        this.mouseX = 0;
        this.mouseY = 0;
        this.isPointerLocked = false;
        
        this.init();
    }
    
    init() {
        this.setupScene();
        this.createPlayer();
        this.createCity();
        this.createVehicles();
        this.setupControls();
        this.animate();
    }
    
    setupScene() {
        // Создаем сцену
        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.Fog(0x87CEEB, 50, 200);
        
        // Создаем камеру
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(0, 2, 0);
        
        // Создаем рендерер
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setClearColor(0x87CEEB);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        document.getElementById('gameContainer').appendChild(this.renderer.domElement);
        
        // Освещение
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 50, 50);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        
        // Земля
        const groundGeometry = new THREE.PlaneGeometry(200, 200);
        const groundMaterial = new THREE.MeshLambertMaterial({ color: 0x228B22 });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);
    }
    
    createPlayer() {
        // Создаем персонажа (простой куб)
        const playerGeometry = new THREE.BoxGeometry(0.5, 1.8, 0.5);
        const playerMaterial = new THREE.MeshLambertMaterial({ color: 0x0000ff });
        this.player = new THREE.Mesh(playerGeometry, playerMaterial);
        this.player.position.set(0, 0.9, 0);
        this.player.castShadow = true;
        this.scene.add(this.player);
        
        // Камера следует за игроком
        this.camera.position.copy(this.player.position);
        this.camera.position.y += 0.5;
    }
    
    createCity() {
        // Создаем здания
        const buildingColors = [0x8B4513, 0x696969, 0x2F4F4F, 0x708090, 0x556B2F];
        
        for (let i = 0; i < 20; i++) {
            const width = Math.random() * 10 + 5;
            const height = Math.random() * 20 + 10;
            const depth = Math.random() * 10 + 5;
            
            const buildingGeometry = new THREE.BoxGeometry(width, height, depth);
            const buildingMaterial = new THREE.MeshLambertMaterial({ 
                color: buildingColors[Math.floor(Math.random() * buildingColors.length)] 
            });
            const building = new THREE.Mesh(buildingGeometry, buildingMaterial);
            
            building.position.set(
                (Math.random() - 0.5) * 150,
                height / 2,
                (Math.random() - 0.5) * 150
            );
            
            building.castShadow = true;
            building.receiveShadow = true;
            this.scene.add(building);
            this.buildings.push(building);
        }
        
        // Создаем дороги
        const roadGeometry = new THREE.PlaneGeometry(200, 10);
        const roadMaterial = new THREE.MeshLambertMaterial({ color: 0x333333 });
        
        const road1 = new THREE.Mesh(roadGeometry, roadMaterial);
        road1.rotation.x = -Math.PI / 2;
        road1.position.y = 0.01;
        this.scene.add(road1);
        
        const road2 = new THREE.Mesh(roadGeometry, roadMaterial);
        road2.rotation.x = -Math.PI / 2;
        road2.rotation.z = Math.PI / 2;
        road2.position.y = 0.01;
        this.scene.add(road2);
    }
    
    createVehicles() {
        // Создаем несколько машин
        for (let i = 0; i < 5; i++) {
            const carGeometry = new THREE.BoxGeometry(2, 1, 4);
            const carMaterial = new THREE.MeshLambertMaterial({ 
                color: Math.random() * 0xffffff 
            });
            const car = new THREE.Mesh(carGeometry, carMaterial);
            
            car.position.set(
                (Math.random() - 0.5) * 100,
                0.5,
                (Math.random() - 0.5) * 100
            );
            
            car.castShadow = true;
            this.scene.add(car);
            this.vehicles.push(car);
        }
    }
    
    setupControls() {
        // Обработка клавиатуры
        document.addEventListener('keydown', (event) => {
            this.keys[event.code] = true;
            
            if (event.code === 'Space') {
                this.jump();
            }
            if (event.code === 'KeyE') {
                this.interact();
            }
        });
        
        document.addEventListener('keyup', (event) => {
            this.keys[event.code] = false;
        });
        
        // Обработка мыши
        document.addEventListener('click', () => {
            this.renderer.domElement.requestPointerLock();
        });
        
        document.addEventListener('pointerlockchange', () => {
            this.isPointerLocked = document.pointerLockElement === this.renderer.domElement;
        });
        
        document.addEventListener('mousemove', (event) => {
            if (this.isPointerLocked) {
                this.mouseX = event.movementX || 0;
                this.mouseY = event.movementY || 0;
            }
        });
        
        // Изменение размера окна
        window.addEventListener('resize', () => {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });
    }
    
    jump() {
        // Простой прыжок
        if (this.player.position.y <= 1) {
            this.player.position.y += 3;
        }
    }
    
    interact() {
        // Взаимодействие с объектами
        console.log('Взаимодействие!');
        
        // Проверяем близость к машинам
        this.vehicles.forEach(vehicle => {
            const distance = this.player.position.distanceTo(vehicle.position);
            if (distance < 3) {
                console.log('Сесть в машину!');
            }
        });
    }
    
    updatePlayer() {
        const speed = 0.1;
        const rotationSpeed = 0.02;
        
        // Поворот камеры
        if (this.isPointerLocked) {
            this.camera.rotation.y -= this.mouseX * rotationSpeed;
            this.camera.rotation.x -= this.mouseY * rotationSpeed;
            
            // Ограничиваем вертикальный поворот
            this.camera.rotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, this.camera.rotation.x));
        }
        
        // Движение
        const direction = new THREE.Vector3();
        
        if (this.keys['KeyW']) {
            direction.z -= 1;
        }
        if (this.keys['KeyS']) {
            direction.z += 1;
        }
        if (this.keys['KeyA']) {
            direction.x -= 1;
        }
        if (this.keys['KeyD']) {
            direction.x += 1;
        }
        
        if (direction.length() > 0) {
            direction.normalize();
            
            // Применяем поворот камеры к направлению движения
            direction.applyEuler(new THREE.Euler(0, this.camera.rotation.y, 0));
            
            this.player.position.add(direction.multiplyScalar(speed));
        }
        
        // Гравитация
        if (this.player.position.y > 0.9) {
            this.player.position.y -= 0.1;
        } else {
            this.player.position.y = 0.9;
        }
        
        // Обновляем позицию камеры
        this.camera.position.copy(this.player.position);
        this.camera.position.y += 0.5;
        
        // Обновляем UI
        this.updateUI();
    }
    
    updateUI() {
        document.getElementById('healthValue').textContent = this.health;
        document.getElementById('healthFill').style.width = this.health + '%';
        document.getElementById('position').textContent = 
            `${Math.round(this.player.position.x)}, ${Math.round(this.player.position.y)}, ${Math.round(this.player.position.z)}`;
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.updatePlayer();
        this.renderer.render(this.scene, this.camera);
    }
}

// Запускаем игру
const game = new GTAGame();