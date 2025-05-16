// Global variables
let scene, camera, renderer, jersey, controls;
let activeView = 'front';
let animationInProgress = false;

// Design state
const frontDesign = {
    primaryColor: '#ffffff',
    secondaryColor: '#000000',
    textColor: '#000000',
    number: '',
    pattern: 'none',
    logoUrl: '',
    logoSize: 0.5
};

const backDesign = {
    primaryColor: '#ffffff',
    secondaryColor: '#000000',
    textColor: '#000000',
    name: '',
    number: '',
    pattern: 'none',
    logoUrl: '',
    logoSize: 0.5
};

// Initialize the scene
function init() {
    console.log('Initializing 3D scene...');
    
    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111111);
    
    // Create camera
    const container = document.getElementById('canvas-container');
    const aspect = container.clientWidth / container.clientHeight;
    camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
    camera.position.z = 5;
    
    // Create renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    // Create jersey model
    createJersey();
    
    // Add orbit controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    
    // Set up event listeners
    setupEventListeners();
    
    // Start animation loop
    animate();
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    console.log('3D scene initialized');
}

// Create the jersey model
function createJersey() {
    jersey = new THREE.Group();
    
    // Create front panel
    const frontGeometry = new THREE.BoxGeometry(2, 3, 0.2);
    const frontMaterial = new THREE.MeshStandardMaterial({
        color: frontDesign.primaryColor,
        side: THREE.DoubleSide
    });
    const frontPanel = new THREE.Mesh(frontGeometry, frontMaterial);
    frontPanel.position.z = 0.1;
    frontPanel.userData.side = 'front';
    jersey.add(frontPanel);
    
    // Create back panel
    const backGeometry = new THREE.BoxGeometry(2, 3, 0.2);
    const backMaterial = new THREE.MeshStandardMaterial({
        color: backDesign.primaryColor,
        side: THREE.DoubleSide
    });
    const backPanel = new THREE.Mesh(backGeometry, backMaterial);
    backPanel.position.z = -0.1;
    backPanel.rotation.y = Math.PI;
    backPanel.userData.side = 'back';
    jersey.add(backPanel);
    
    // Add sleeves
    addSleeves();
    
    scene.add(jersey);
}

// Add sleeves to the jersey
function addSleeves() {
    // Front sleeves
    const leftSleeveGeometry = new THREE.BoxGeometry(0.8, 1, 0.2);
    const leftSleeveMaterial = new THREE.MeshStandardMaterial({
        color: frontDesign.secondaryColor,
        side: THREE.DoubleSide
    });
    const leftSleeve = new THREE.Mesh(leftSleeveGeometry, leftSleeveMaterial);
    leftSleeve.position.set(-1.4, 0.5, 0.1);
    leftSleeve.userData.side = 'front';
    leftSleeve.userData.part = 'sleeve';
    jersey.add(leftSleeve);
    
    const rightSleeveGeometry = new THREE.BoxGeometry(0.8, 1, 0.2);
    const rightSleeveMaterial = new THREE.MeshStandardMaterial({
        color: frontDesign.secondaryColor,
        side: THREE.DoubleSide
    });
    const rightSleeve = new THREE.Mesh(rightSleeveGeometry, rightSleeveMaterial);
    rightSleeve.position.set(1.4, 0.5, 0.1);
    rightSleeve.userData.side = 'front';
    rightSleeve.userData.part = 'sleeve';
    jersey.add(rightSleeve);
    
    // Back sleeves
    const backLeftSleeve = leftSleeve.clone();
    backLeftSleeve.position.z = -0.1;
    backLeftSleeve.rotation.y = Math.PI;
    backLeftSleeve.userData.side = 'back';
    jersey.add(backLeftSleeve);
    
    const backRightSleeve = rightSleeve.clone();
    backRightSleeve.position.z = -0.1;
    backRightSleeve.rotation.y = Math.PI;
    backRightSleeve.userData.side = 'back';
    jersey.add(backRightSleeve);
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    
    if (controls) {
        controls.update();
    }
    
    renderer.render(scene, camera);
}

// Handle window resize
function onWindowResize() {
    const container = document.getElementById('canvas-container');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

// Set up event listeners
function setupEventListeners() {
    // View controls
    document.getElementById('front-view').addEventListener('click', () => setActiveView('front'));
    document.getElementById('back-view').addEventListener('click', () => setActiveView('back'));
    
    // Jersey type
    document.getElementById('jersey-type').addEventListener('change', updateJerseyType);
    
    // Colors
    document.getElementById('primary-color').addEventListener('input', (e) => {
        const design = activeView === 'front' ? frontDesign : backDesign;
        design.primaryColor = e.target.value;
        updateJerseyMaterials();
    });
    
    document.getElementById('secondary-color').addEventListener('input', (e) => {
        const design = activeView === 'front' ? frontDesign : backDesign;
        design.secondaryColor = e.target.value;
        updateJerseyMaterials();
    });
    
    document.getElementById('text-color').addEventListener('input', (e) => {
        const design = activeView === 'front' ? frontDesign : backDesign;
        design.textColor = e.target.value;
        updateJerseyText();
    });
    
    // Pattern
    document.getElementById('pattern').addEventListener('change', (e) => {
        const design = activeView === 'front' ? frontDesign : backDesign;
        design.pattern = e.target.value;
        updateJerseyMaterials();
    });
    
    // Text inputs
    document.getElementById('front-number').addEventListener('input', (e) => {
        frontDesign.number = e.target.value;
        updateJerseyText();
    });
    
    document.getElementById('back-name').addEventListener('input', (e) => {
        backDesign.name = e.target.value;
        updateJerseyText();
    });
    
    document.getElementById('back-number').addEventListener('input', (e) => {
        backDesign.number = e.target.value;
        updateJerseyText();
    });
    
    // Logo
    document.getElementById('logo-upload').addEventListener('change', handleLogoUpload);
    document.getElementById('logo-size').addEventListener('input', (e) => {
        const design = activeView === 'front' ? frontDesign : backDesign;
        design.logoSize = parseFloat(e.target.value);
        updateJerseyLogo();
    });
    
    // Reset view
    document.getElementById('reset-view').addEventListener('click', resetView);
    
    // Clear all
    document.getElementById('clear-all').addEventListener('click', clearAll);
    
    // Download design
    document.getElementById('download-design').addEventListener('click', downloadDesign);
}

// Set active view (front or back)
function setActiveView(view) {
    if (activeView === view || animationInProgress) return;
    
    activeView = view;
    
    // Update UI
    document.getElementById('front-view').classList.toggle('bg-white', view === 'front');
    document.getElementById('front-view').classList.toggle('shadow', view === 'front');
    document.getElementById('front-view').classList.toggle('text-gray-900', view === 'front');
    document.getElementById('front-view').classList.toggle('text-gray-600', view === 'back');
    
    document.getElementById('back-view').classList.toggle('bg-white', view === 'back');
    document.getElementById('back-view').classList.toggle('shadow', view === 'back');
    document.getElementById('back-view').classList.toggle('text-gray-900', view === 'back');
    document.getElementById('back-view').classList.toggle('text-gray-600', view === 'front');
    
    document.getElementById('front-options').style.display = view === 'front' ? 'block' : 'none';
    document.getElementById('back-options').style.display = view === 'back' ? 'block' : 'none';
    
    // Rotate jersey
    rotateJersey();
}

// Rotate jersey to show front or back
function rotateJersey() {
    animationInProgress = true;
    
    const targetRotation = activeView === 'front' ? 0 : Math.PI;
    const startRotation = jersey.rotation.y;
    const duration = 500; // milliseconds
    const startTime = Date.now();
    
    function animateRotation() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Use easing function for smoother animation
        const easeProgress = 1 - Math.pow(1 - progress, 3); // cubic ease out
        
        jersey.rotation.y = startRotation + (targetRotation - startRotation) * easeProgress;
        
        if (progress < 1) {
            requestAnimationFrame(animateRotation);
        } else {
            jersey.rotation.y = targetRotation;
            animationInProgress = false;
        }
    }
    
    animateRotation();
}

// Update jersey type (t-shirt or sleeveless)
function updateJerseyType() {
    const jerseyType = document.getElementById('jersey-type').value;
    
    // Show/hide sleeves based on jersey type
    jersey.children.forEach(child => {
        if (child.userData.part === 'sleeve') {
            child.visible = jerseyType === 'tshirt';
        }
    });
}

// Update jersey materials (colors and patterns)
function updateJerseyMaterials() {
    jersey.children.forEach(child => {
        if (!child.userData.side) return;
        
        const design = child.userData.side === 'front' ? frontDesign : backDesign;
        
        if (child.userData.part === 'sleeve') {
            child.material.color.set(design.secondaryColor);
        } else {
            child.material.color.set(design.primaryColor);
            
            // Apply pattern if selected
            if (design.pattern !== 'none') {
                const textureLoader = new THREE.TextureLoader();
                textureLoader.load(`/static/patterns/${design.pattern}.png`, texture => {
                    texture.wrapS = THREE.RepeatWrapping;
                    texture.wrapT = THREE.RepeatWrapping;
                    texture.repeat.set(4, 4);
                    child.material.map = texture;
                    child.material.needsUpdate = true;
                });
            } else {
                child.material.map = null;
                child.material.needsUpdate = true;
            }
        }
    });
}

// Update jersey text (numbers and name)
function updateJerseyText() {
    // Remove existing text meshes
    jersey.children.forEach(child => {
        if (child.userData.type === 'text') {
            jersey.remove(child);
        }
    });
    
    // Add front number (upper right)
    if (frontDesign.number) {
        try {
            const loader = new THREE.FontLoader();
            loader.load('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/fonts/helvetiker_bold.typeface.json', font => {
                const textGeometry = new THREE.TextGeometry(frontDesign.number, {
                    font: font,
                    size: 0.2,
                    height: 0.05
                });
                
                const textMaterial = new THREE.MeshStandardMaterial({ color: frontDesign.textColor });
                const textMesh = new THREE.Mesh(textGeometry, textMaterial);
                
                // Center the text
                textGeometry.computeBoundingBox();
                const textWidth = textGeometry.boundingBox.max.x - textGeometry.boundingBox.min.x;
                
                textMesh.position.set(0.8 - textWidth / 2, 1.2, 0.21);
                textMesh.userData.type = 'text';
                textMesh.userData.side = 'front';
                
                jersey.add(textMesh);
            });
        } catch (error) {
            console.error('Error creating front number:', error);
        }
    }
    
    // Add back name (upper middle)
    if (backDesign.name) {
        try {
            const loader = new THREE.FontLoader();
            loader.load('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/fonts/helvetiker_bold.typeface.json', font => {
                const textGeometry = new THREE.TextGeometry(backDesign.name.toUpperCase(), {
                    font: font,
                    size: 0.2,
                    height: 0.05
                });
                
                const textMaterial = new THREE.MeshStandardMaterial({ color: backDesign.textColor });
                const textMesh = new THREE.Mesh(textGeometry, textMaterial);
                
                // Center the text
                textGeometry.computeBoundingBox();
                const textWidth = textGeometry.boundingBox.max.x - textGeometry.boundingBox.min.x;
                
                textMesh.position.set(-textWidth / 2, 1.2, -0.21);
                textMesh.rotation.y = Math.PI;
                textMesh.userData.type = 'text';
                textMesh.userData.side = 'back';
                
                jersey.add(textMesh);
            });
        } catch (error) {
            console.error('Error creating back name:', error);
        }
    }
    
    // Add back number (center, large)
    if (backDesign.number) {
        try {
            const loader = new THREE.FontLoader();
            loader.load('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/fonts/helvetiker_bold.typeface.json', font => {
                const textGeometry = new THREE.TextGeometry(backDesign.number, {
                    font: font,
                    size: 0.8,
                    height: 0.1
                });
                
                const textMaterial = new THREE.MeshStandardMaterial({ color: backDesign.textColor });
                const textMesh = new THREE.Mesh(textGeometry, textMaterial);
                
                // Center the text
                textGeometry.computeBoundingBox();
                const textWidth = textGeometry.boundingBox.max.x - textGeometry.boundingBox.min.x;
                
                textMesh.position.set(-textWidth / 2, 0, -0.21);
                textMesh.rotation.y = Math.PI;
                textMesh.userData.type = 'text';
                textMesh.userData.side = 'back';
                
                jersey.add(textMesh);
            });
        } catch (error) {
            console.error('Error creating back number:', error);
        }
    }
}

// Handle logo upload
function handleLogoUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const design = activeView === 'front' ? frontDesign : backDesign;
        design.logoUrl = e.target.result;
        
        // Show logo size slider
        document.getElementById('logo-size-container').style.display = 'block';
        
        updateJerseyLogo();
    };
    reader.readAsDataURL(file);
}

// Update jersey logo
function updateJerseyLogo() {
    // Remove existing logos
    jersey.children.forEach(child => {
        if (child.userData.type === 'logo') {
            jersey.remove(child);
        }
    });
    
    // Add front logo if exists
    if (frontDesign.logoUrl) {
        const textureLoader = new THREE.TextureLoader();
        textureLoader.load(frontDesign.logoUrl, texture => {
            const aspect = texture.image.width / texture.image.height;
            const logoGeometry = new THREE.PlaneGeometry(frontDesign.logoSize * aspect, frontDesign.logoSize);
            const logoMaterial = new THREE.MeshBasicMaterial({
                map: texture,
                transparent: true,
                side: THREE.DoubleSide
            });
            
            const logoMesh = new THREE.Mesh(logoGeometry, logoMaterial);
            logoMesh.position.set(0, 0.5, 0.21);
            logoMesh.userData.type = 'logo';
            logoMesh.userData.side = 'front';
            
            jersey.add(logoMesh);
        });
    }
    
    // Add back logo if exists
    if (backDesign.logoUrl) {
        const textureLoader = new THREE.TextureLoader();
        textureLoader.load(backDesign.logoUrl, texture => {
            const aspect = texture.image.width / texture.image.height;
            const logoGeometry = new THREE.PlaneGeometry(backDesign.logoSize * aspect, backDesign.logoSize);
            const logoMaterial = new THREE.MeshBasicMaterial({
                map: texture,
                transparent: true,
                side: THREE.DoubleSide
            });
            
            const logoMesh = new THREE.Mesh(logoGeometry, logoMaterial);
            logoMesh.position.set(0, 0.5, -0.21);
            logoMesh.rotation.y = Math.PI;
            logoMesh.userData.type = 'logo';
            logoMesh.userData.side = 'back';
            
            jersey.add(logoMesh);
        });
    }
}

// Reset camera view
function resetView() {
    controls.reset();
}

// Clear all design elements
function clearAll() {
    // Reset front design
    frontDesign.primaryColor = '#ffffff';
    frontDesign.secondaryColor = '#000000';
    frontDesign.textColor = '#000000';
    frontDesign.number = '';
    frontDesign.pattern = 'none';
    frontDesign.logoUrl = '';
    frontDesign.logoSize = 0.5;
    
    // Reset back design
    backDesign.primaryColor = '#ffffff';
    backDesign.secondaryColor = '#000000';
    backDesign.textColor = '#000000';
    backDesign.name = '';
    backDesign.number = '';
    backDesign.pattern = 'none';
    backDesign.logoUrl = '';
    backDesign.logoSize = 0.5;
    
    // Reset form inputs
    document.getElementById('primary-color').value = '#ffffff';
    document.getElementById('secondary-color').value = '#000000';
    document.getElementById('text-color').value = '#000000';
    document.getElementById('pattern').value = 'none';
    document.getElementById('front-number').value = '';
    document.getElementById('back-name').value = '';
    document.getElementById('back-number').value = '';
    document.getElementById('jersey-type').value = 'tshirt';
    
    // Hide logo size slider
    document.getElementById('logo-size-container').style.display = 'none';
    
    // Update jersey
    updateJerseyMaterials();
    updateJerseyText();
    updateJerseyLogo();
}

// Download design as image
function downloadDesign() {
    // Reset camera to front view for screenshot
    const originalRotation = jersey.rotation.y;
    jersey.rotation.y = 0;
    
    // Render the scene
    renderer.render(scene, camera);
    
    // Create a download link
    const link = document.createElement('a');
    link.download = 'custom-jersey.png';
    link.href = renderer.domElement.toDataURL('image/png');
    link.click();
    
    // Restore original rotation
    jersey.rotation.y = originalRotation;
}

// Initialize when the page loads
window.addEventListener('load', init);