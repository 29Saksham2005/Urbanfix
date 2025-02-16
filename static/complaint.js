document.addEventListener('DOMContentLoaded', () => {
    const complaintForm = document.getElementById('complaintForm');
    const submitButton = complaintForm.querySelector('button[type="submit"]');
    const thankYouMessage = document.getElementById('thank-you-message');

    // Form validation
    function validateForm(formData) {
        const description = formData.get('description').trim();
        const image = formData.get('image');

        if (description.length < 10) {
            throw new Error('Description must be at least 10 characters long');
        }

        if (!image || image.size === 0) {
            throw new Error('Please select an image');
        }

        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        if (!allowedTypes.includes(image.type)) {
            throw new Error('Please upload a valid image file (JPEG, PNG, or GIF)');
        }

        if (image.size > 5 * 1024 * 1024) { // 5MB limit
            throw new Error('Image size should be less than 5MB');
        }
    }

    // Show loading state
    function setLoading(isLoading) {
        submitButton.disabled = isLoading;
        submitButton.innerHTML = isLoading ? 
            '<span class="spinner"></span> Submitting...' : 
            'Submit';
    }

    // Handle form submission
    complaintForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        thankYouMessage.style.display = 'none';
        setLoading(true);

        try {
            const formData = new FormData(event.target);
            
            // Validate form data
            validateForm(formData);

            const response = await fetch('/submit_complaint', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Server error occurred');
            }

            // Show success message
            thankYouMessage.style.display = 'block';
            thankYouMessage.textContent = data.message || 'Thank you for your submission!';
            complaintForm.reset();

            // Scroll to thank you message
            thankYouMessage.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            // Show error message
            alert(error.message || 'An error occurred. Please try again.');
            console.error('Submission error:', error);
        } finally {
            setLoading(false);
        }
    });

    // Preview image before upload
    const imageInput = document.getElementById('image');
    imageInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                // You can add an image preview element if desired
                console.log('Image loaded successfully');
            };
            reader.readAsDataURL(file);
        }
    });
}); 