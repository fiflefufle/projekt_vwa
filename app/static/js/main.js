document.addEventListener('DOMContentLoaded', function() {

    const btnPridat = document.getElementById('btn-pridat');
    
    if (btnPridat) {
        btnPridat.addEventListener('click', function() {
            const container = document.getElementById('prace-container');
            const firstRow = container.querySelector('.prace-row');
            const newRow = firstRow.cloneNode(true);
            const select = newRow.querySelector('select');
            select.value = ""; 
            newRow.classList.add('mt-2');
            container.appendChild(newRow);
        });
    }

    const dateInput = document.getElementById('datePicker');
    
    if (dateInput) {
        const now = new Date();
        
        // Trik pro získání lokálního času ve formátu ISO (prohlížeče jinak vrací UTC)
        // Odečteme časový posun, aby to odpovídalo našemu času
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        
        // Ořízneme sekundy a milisekundy, zbyde: "YYYY-MM-DDTHH:MM"
        const currentDateTime = now.toISOString().slice(0, 16);
        
        // Nastavíme atribut min
        dateInput.min = currentDateTime;
    }

});