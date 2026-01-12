// Initialize Sortable on each column
document.addEventListener('DOMContentLoaded', function() {
    const columns = document.querySelectorAll('.status-column');
    let isUpdating = false;

    // Detect which kanban board we're on based on current URL
    const currentPath = window.location.pathname;
    let kanbanConfig = detectKanbanType(currentPath);

    columns.forEach(function(column) {
        new Sortable(column, {
            group: 'kanban-cards',
            animation: 150,
            handle: '.cursor-grab',
            ghostClass: 'ghost-grab',
            dragClass: 'drag-kanban',

            onStart: function(event) {
                if (isUpdating) return false;
            },

            onEnd: function(event) {
                isUpdating = true;

                const card = event.item;
                const itemId = card.dataset.leadId; // Note: uses data-lead-id for both leads and quotes

                // Get new status from column ID
                const newColumn = event.to;
                const columnId = newColumn.id;
                const newStatus = columnId.replace('-column', '');

                // Store original position for revert
                const originalColumn = event.from;
                const originalIndex = event.oldIndex;

                // Validate data
                if (!itemId || !newStatus) {
                    console.error('Could not determine item ID or new status');
                    alert(kanbanConfig.errorMessages.updateFailed);
                    originalColumn.insertBefore(card, originalColumn.children[originalIndex]);
                    isUpdating = false;
                    return;
                }

                // Get CSRF token
                const csrfToken = getCookie('csrftoken');

                // Prepare request body
                const requestBody = {};
                requestBody[kanbanConfig.idField] = itemId;
                requestBody['new_status'] = newStatus;

                // Send AJAX request
                fetch(kanbanConfig.apiEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify(requestBody)
                })
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('Server responded with error: ' + response.status);
                    }
                    return response.json();
                })
                .then(function(data) {
                    console.log(kanbanConfig.itemName + ' status updated successfully:', data);
                    updateStatusCounts(data.status_counts);
                    isUpdating = false;
                })
                .catch(function(error) {
                    console.error('Error updating ' + kanbanConfig.itemName + ' status:', error);

                    let errorMessage = kanbanConfig.errorMessages.updateFailed;
                    if (!navigator.onLine) {
                        errorMessage = 'אין חיבור לאינטרנט. בדוק את החיבור שלך ונסה שוב.';
                    } else if (error.message.includes('500')) {
                        errorMessage = 'שגיאת שרת. פנה לתמיכה הטכנית.';
                    } else if (error.message.includes('404')) {
                        errorMessage = kanbanConfig.errorMessages.notFound;
                    }

                    alert(errorMessage + '\n\n' + kanbanConfig.errorMessages.revert);
                    originalColumn.insertBefore(card, originalColumn.children[originalIndex]);
                    isUpdating = false;
                });
            }
        });
    });
});

// Detect which type of kanban board we're on
function detectKanbanType(pathname) {
    if (pathname.includes('/leads/') || pathname.includes('/lead-kanban')) {
        return {
            itemName: 'lead',
            idField: 'lead_id',
            apiEndpoint: '/leads/api/update-status',
            errorMessages: {
                updateFailed: 'שגיאה: לא ניתן לעדכן את הליד. נסה לרענן את הדף.',
                notFound: 'הליד לא נמצא במערכת.',
                revert: 'הליד יוחזר למיקום המקורי.'
            }
        };
    } else if (pathname.includes('/quotes/') || pathname.includes('/quote-kanban')) {
        return {
            itemName: 'quote',
            idField: 'quote_id',
            apiEndpoint: '/quotes/api/update-status',
            errorMessages: {
                updateFailed: 'שגיאה: לא ניתן לעדכן את הצעת המחיר. נסה לרענן את הדף.',
                notFound: 'הצעת המחיר לא נמצאה במערכת.',
                revert: 'הצעת המחיר תוחזר למיקום המקורי.'
            }
        };
    } 

    // Default fallback (can be extended for future kanban boards)
    return {
        itemName: 'item',
        idField: 'item_id',
        apiEndpoint: '/api/update-status',
        errorMessages: {
            updateFailed: 'שגיאה: לא ניתן לעדכן. נסה לרענן את הדף.',
            notFound: 'הפריט לא נמצא במערכת.',
            revert: 'הפריט יוחזר למיקום המקורי.'
        }
    };
}

// Helper function to get cookie value
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Helper function to update status count badges
function updateStatusCounts(statusCounts) {
    const statusPills = document.querySelectorAll('span[name="status-count"]');

    // Update each pill by finding the corresponding column
    statusPills.forEach(function(pill) {
        // Find the parent column to get the status from its ID
        const column = pill.closest('.bg-gray-50').querySelector('.status-column');
        if (column && column.id) {
            const status = column.id.replace('-column', '');
            if (statusCounts[status] !== undefined) {
                pill.textContent = statusCounts[status];
            }
        }
    });
}
