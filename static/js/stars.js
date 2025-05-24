// 星空动画增强
document.addEventListener('DOMContentLoaded', function() {
    // 创建额外的星星粒子效果
    createStarField();
    
    // 添加鼠标移动视差效果
    addParallaxEffect();
    
    // 添加页面切换动画
    addPageTransitions();
});

function createStarField() {
    const starField = document.createElement('div');
    starField.className = 'star-field';
    starField.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    `;
    
    // 创建星星
    for (let i = 0; i < 100; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.cssText = `
            position: absolute;
            width: ${Math.random() * 3 + 1}px;
            height: ${Math.random() * 3 + 1}px;
            background: white;
            border-radius: 50%;
            top: ${Math.random() * 100}%;
            left: ${Math.random() * 100}%;
            opacity: ${Math.random() * 0.8 + 0.2};
            animation: twinkle ${Math.random() * 3 + 2}s infinite;
        `;
        starField.appendChild(star);
    }
    
    document.body.appendChild(starField);
    
    // 添加闪烁动画
    const style = document.createElement('style');
    style.textContent = `
        @keyframes twinkle {
            0%, 100% { opacity: 0.2; }
            50% { opacity: 1; }
        }
    `;
    document.head.appendChild(style);
}

function addParallaxEffect() {
    let mouseX = 0;
    let mouseY = 0;
    
    document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX / window.innerWidth;
        mouseY = e.clientY / window.innerHeight;
        
        // 移动星空背景
        const stars = document.querySelector('.stars');
        const twinkling = document.querySelector('.twinkling');
        
        if (stars) {
            stars.style.transform = `translate(${mouseX * 20}px, ${mouseY * 20}px)`;
        }
        
        if (twinkling) {
            twinkling.style.transform = `translate(${mouseX * -15}px, ${mouseY * -15}px)`;
        }
    });
}

function addPageTransitions() {
    // 页面加载动画
    const body = document.body;
    body.style.opacity = '0';
    body.style.transition = 'opacity 0.5s ease-in-out';
    
    window.addEventListener('load', function() {
        body.style.opacity = '1';
    });
    
    // 链接点击动画
    const links = document.querySelectorAll('a[href^="/"], a[href^="./"], a[href^="../"]');
    links.forEach(link => {
        if (link.getAttribute('href') !== '#') {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const href = this.getAttribute('href');
                
                body.style.opacity = '0';
                setTimeout(() => {
                    window.location.href = href;
                }, 300);
            });
        }
    });
}

// 添加页面滚动动画
function addScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // 观察需要动画的元素
    const animatedElements = document.querySelectorAll('.feature-card, .choice-card, .accordion-item');
    animatedElements.forEach(el => {
        el.style.animationPlayState = 'paused';
        observer.observe(el);
    });
}

// 添加打字机效果
function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.innerHTML = '';
    
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// 添加粒子效果（用于特殊场景）
function createParticleEffect(container, count = 20) {
    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: absolute;
            width: 4px;
            height: 4px;
            background: #ffd700;
            border-radius: 50%;
            pointer-events: none;
            animation: float ${Math.random() * 3 + 2}s infinite ease-in-out;
            top: ${Math.random() * 100}%;
            left: ${Math.random() * 100}%;
            opacity: ${Math.random() * 0.7 + 0.3};
        `;
        container.appendChild(particle);
    }
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(180deg); }
        }
    `;
    document.head.appendChild(style);
}

// 音效管理（可选）
class SoundManager {
    constructor() {
        this.sounds = {};
        this.enabled = true;
    }
    
    loadSound(name, url) {
        const audio = new Audio(url);
        audio.preload = 'auto';
        this.sounds[name] = audio;
    }
    
    play(name, volume = 0.5) {
        if (this.enabled && this.sounds[name]) {
            this.sounds[name].volume = volume;
            this.sounds[name].currentTime = 0;
            this.sounds[name].play().catch(() => {
                // 忽略播放失败
            });
        }
    }
    
    toggle() {
        this.enabled = !this.enabled;
    }
}

// 全局变量
window.soundManager = new SoundManager();

// 工具函数
function randomBetween(min, max) {
    return Math.random() * (max - min) + min;
}

function lerp(start, end, factor) {
    return start + (end - start) * factor;
}

// 性能优化 - 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// 移动设备优化
if (window.innerWidth <= 768) {
    // 在移动设备上减少动画以提高性能
    const style = document.createElement('style');
    style.textContent = `
        * {
            animation-duration: 0.1s !important;
            animation-delay: 0s !important;
            transition-duration: 0.1s !important;
        }
    `;
 