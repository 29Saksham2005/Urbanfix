document.addEventListener('DOMContentLoaded', () => {
    // Sample data (replace with dynamic data from backend)
    const complaints = [
        // ... (your complaint data)
    ];

    function displayComplaints(filter = "all") {
        const complaintTable = document.querySelector('.complaint-table');
        complaintTable.innerHTML = ""; // Clear any existing content

        const filteredComplaints = filter === "all" ? complaints : complaints.filter(c => c.status === filter);

        filteredComplaints.forEach(complaint => {
            const block = document.createElement('div');
            block.classList.add('complaint-block');
            block.innerHTML = `
                <h3>${complaint.id} - ${complaint.category} at ${complaint.location}</h3>
                <div class="complaint-details">
                    <p><strong>Location:</strong> ${complaint.location}</p>
                    <p><strong>Complaint Type:</strong> ${complaint.category}</p>
                    <p><strong>Date:</strong> ${complaint.date}</p>
                    <p><strong>ID:</strong> ${complaint.id}</p>
                    <p><strong>Description:</strong> ${complaint.description}</p>
                </div>
            `;

            block.addEventListener('click', () => {
                const details = block.querySelector('.complaint-details');
                details.style.display = details.style.display === 'block' ? 'none' : 'block';
            });

            complaintTable.appendChild(block);
        });
    }

    displayComplaints(); // Initial display

    const activeComplaintsButton = document.querySelector('.active-complaints');
    const resolvedComplaintsButton = document.querySelector('.resolved-complaints');

    activeComplaintsButton.addEventListener('click', () => {
        displayComplaints("Pending"); // Filter for active (pending) complaints
    });

    resolvedComplaintsButton.addEventListener('click', () => {
        displayComplaints("Resolved"); // Filter for resolved complaints
    });
});