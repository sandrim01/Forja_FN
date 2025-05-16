// Inicialização do Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    // Inicialização de tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicialização de popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Verificação de nível a cada 10 segundos para usuários logados
    if (document.querySelector('#levelUpContainer')) {
        setInterval(checkXPLevel, 10000);
    }
});

// Função para verificar nível de XP
function checkXPLevel() {
    if (!document.querySelector('#levelUpContainer')) return;
    
    fetch('/check_xp')
        .then(response => response.json())
        .then(data => {
            if (data.leveled_up) {
                showLevelUpNotification(data.level, data.rank_name);
            }
        })
        .catch(error => console.error('Erro ao verificar XP:', error));
}

// Mostrar notificação de nível alcançado
function showLevelUpNotification(level, rankName) {
    const container = document.querySelector('#levelUpContainer');
    if (!container) return;
    
    // Atualizar informações
    container.querySelector('p:nth-of-type(1) span').textContent = level;
    container.querySelector('p:nth-of-type(2) span').textContent = rankName;
    
    // Exibir a notificação
    container.classList.remove('d-none');
    container.classList.add('animate-pulse');
    
    // Reproduzir som de congratulação (se disponível)
    const audio = new Audio('/static/sounds/level-up.mp3');
    audio.play().catch(e => console.log('Reprodução de áudio não suportada'));
    
    // Ocultar após 5 segundos
    setTimeout(() => {
        container.classList.add('d-none');
        container.classList.remove('animate-pulse');
    }, 5000);
}

// Função para inicializar o temporizador do quiz
function initQuizTimer(timeLimit) {
    const timerElement = document.getElementById('quizTimer');
    if (!timerElement) return;
    
    let minutes = timeLimit;
    let seconds = 0;
    
    const interval = setInterval(() => {
        if (seconds === 0) {
            if (minutes === 0) {
                clearInterval(interval);
                document.getElementById('quizForm').submit();
                return;
            }
            minutes--;
            seconds = 59;
        } else {
            seconds--;
        }
        
        // Formatar tempo (MM:SS)
        const formattedMinutes = minutes.toString().padStart(2, '0');
        const formattedSeconds = seconds.toString().padStart(2, '0');
        timerElement.textContent = `${formattedMinutes}:${formattedSeconds}`;
        
        // Aviso de tempo acabando
        if (minutes === 0 && seconds <= 30) {
            timerElement.classList.add('text-danger');
            timerElement.classList.add('animate-pulse');
        }
    }, 1000);
}

// Seleção de opção de resposta no quiz
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('answer-option') || e.target.closest('.answer-option')) {
        const option = e.target.classList.contains('answer-option') ? e.target : e.target.closest('.answer-option');
        const questionId = option.dataset.questionId;
        const radioInput = option.querySelector('input[type="radio"]');
        
        // Deselecionar outras opções do mesmo grupo
        document.querySelectorAll(`.answer-option[data-question-id="${questionId}"]`).forEach(el => {
            el.classList.remove('selected');
        });
        
        // Selecionar opção atual
        option.classList.add('selected');
        radioInput.checked = true;
    }
});

// Confirmação para ações destrutivas
document.addEventListener('click', function(e) {
    if (e.target.hasAttribute('data-confirm')) {
        if (!confirm(e.target.getAttribute('data-confirm'))) {
            e.preventDefault();
        }
    }
});