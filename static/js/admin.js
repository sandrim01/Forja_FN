
function approveUser(userId) {
    if (confirm('Deseja aprovar este aluno?')) {
        fetch(`/admin/users/${userId}/approve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    }
}

function rejectUser(userId) {
    if (confirm('Deseja rejeitar este aluno?')) {
        fetch(`/admin/users/${userId}/reject`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    }
}

function updatePaymentStatus(userId) {
    if (confirm('Confirmar pagamento da mensalidade?')) {
        fetch(`/admin/users/${userId}/payment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    }
}
