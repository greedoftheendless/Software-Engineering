document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const entriesList = document.querySelector('ul');
    const sheetId = document.querySelector('body').dataset.sheetId;

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(form);
        const entry = {
            name: formData.get('name'),
            roll_number: formData.get('roll_number'),
            time_slots: formData.getAll('time_slots')
        };

        fetch(`/sheet/${sheetId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(entry)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addEntryToList(data.entry);
                    form.reset();
                } else {
                    alert(data.message);
                }
            })
            .catch(error => console.error('Error:', error));
    });

    function addEntryToList(entry) {
        const li = document.createElement('li');
        li.textContent = `${entry.name} - ${entry.roll_number} - ${entry.time_slots.join(', ')} by ${entry.user}`;
        if (entry.can_delete) {
            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.addEventListener('click', function() {
                deleteEntry(entry.id, li);
            });
            li.appendChild(deleteButton);
        }
        entriesList.appendChild(li);
    }

    function deleteEntry(entryId, listItem) {
        fetch(`/sheet/${sheetId}/delete_entry/${entryId}`, {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    listItem.remove();
                } else {
                    alert(data.message);
                }
            })
            .catch(error => console.error('Error:', error));
    }
});