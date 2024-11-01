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