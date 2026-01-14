// Color select preview functionality
(function() {
    function updateColorPreview(selectElement) {
        const previewBox = document.getElementById(selectElement.id + '-preview');
        if (previewBox) {
            const selectedOption = selectElement.options[selectElement.selectedIndex];
            const color = selectedOption.getAttribute('data-color') || selectedOption.value;
            previewBox.style.backgroundColor = color;
        }
    }

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        const colorSelects = document.querySelectorAll('.color-select');
        colorSelects.forEach(function(select) {
            updateColorPreview(select);

            // Update preview on change
            select.addEventListener('change', function() {
                updateColorPreview(this);
            });
        });
    });

    // Handle dynamic admin inlines
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).on('formset:added', function(event, row) {
            const colorSelect = row.find('.color-select')[0];
            if (colorSelect) {
                updateColorPreview(colorSelect);
            }
        });
    }
})();
