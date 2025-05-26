/**
 * 打字机效果函数
 * @param {string} elementId - 目标元素的ID
 * @param {string} text - 要显示的文本
 * @param {number} speed - 打字速度(毫秒)
 * @param {function} callback - 完成后的回调函数
 */
function typewriter(elementId, text, speed = 50, callback = null) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.error('Element not found:', elementId);
        return;
    }
    
    // 清空元素内容
    element.innerHTML = '';
    element.classList.add('typing');
    
    // 创建光标元素
    const cursor = document.createElement('span');
    cursor.className = 'typewriter-cursor';
    cursor.innerHTML = '|';
    
    let index = 0;
    
    function type() {
        if (index < text.length) {
            // 处理换行符
            if (text.charAt(index) === '\n') {
                element.appendChild(document.createElement('br'));
            } else {
                element.appendChild(document.createTextNode(text.charAt(index)));
            }
            index++;
            setTimeout(type, speed);
        } else {
            // 打字完成，移除typing类，添加光标闪烁一段时间后移除
            element.classList.remove('typing');
            element.appendChild(cursor);
            
            // 2秒后移除光标
            setTimeout(() => {
                if (cursor.parentNode) {
                    cursor.parentNode.removeChild(cursor);
                }
                if (callback) {
                    callback();
                }
            }, 2000);
        }
    }
    
    type();
}

/**
 * 延迟显示选项
 * @param {number} delay - 延迟时间(毫秒)
 */
function showChoicesWithDelay(delay = 1000) {
    const choicesContainer = document.querySelector('.choices-container');
    if (choicesContainer) {
        choicesContainer.style.opacity = '0';
        choicesContainer.style.transform = 'translateY(20px)';
        choicesContainer.style.transition = 'all 0.5s ease';
        
        setTimeout(() => {
            choicesContainer.style.opacity = '1';
            choicesContainer.style.transform = 'translateY(0)';
        }, delay);
    }
} 