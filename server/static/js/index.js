function openModal(newsId) {
    const modal = document.getElementById('newsModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    // Получаем данные новости по идентификатору
    modalTitle.textContent = newsContent[newsId].title;
    modalBody.innerHTML = newsContent[newsId].content;

    // Показываем модальное окно
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('newsModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

window.onclick = function (event) {
    const modal = document.getElementById('newsModal');
    if (event.target == modal) {
        closeModal();
    }
}