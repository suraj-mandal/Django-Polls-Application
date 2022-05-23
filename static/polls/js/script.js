const paginationSelect = document.getElementById('pagination_selector');
const paginationForm = document.getElementById('pagination_form');

paginationSelect.addEventListener('change', (e) => {
    e.preventDefault();
    paginationForm.submit();
})