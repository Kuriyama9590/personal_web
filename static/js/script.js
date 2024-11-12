function Welcome_alert(uname){
    alert("欢迎" + uname + "!");
}

function createCheer() {
    const cheers = ['🎉', '👏', '🎊', '🥳', '🙌'];
    const cheerContainer = document.getElementById('cheerContainer');
    
    for (let i = 0; i < 20; i++) {
        const cheer = document.createElement('div');
        cheer.className = 'cheer';
        cheer.textContent = cheers[Math.floor(Math.random() * cheers.length)];
        cheer.style.left = Math.random() * 100 + 'vw';
        cheer.style.top = Math.random() * 100 + 'vh';
        cheerContainer.appendChild(cheer);
        
        setTimeout(() => {
            cheer.classList.add('cheer-animation');
        }, i * 100);
    }
}

document.addEventListener('DOMContentLoaded', function() {/*导航栏函数 */
    const navButton = document.querySelector('.button-top');
    const sidebar = document.querySelector('.sidebar');
    const navContainer = document.querySelector('.nav-container');

    navButton.addEventListener('mouseenter', function() {
        sidebar.style.display = 'block'; // 鼠标进入按钮时显示导航栏
    });

    sidebar.addEventListener('mouseenter', function() {
        sidebar.style.display = 'block'; // 鼠标进入导航栏时保持显示
    });

    sidebar.addEventListener('mouseleave', function() {
        sidebar.style.display = 'none'; // 鼠标离开导航栏时隐藏
    });

    navContainer.addEventListener('mouseleave', function() {
        sidebar.style.display = 'none'; // 鼠标离开box时隐藏
    });
});