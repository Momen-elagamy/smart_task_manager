document.addEventListener('DOMContentLoaded', () => {
    const newProjectBtn = document.getElementById('new-project-btn');
    const newProjectModal = document.getElementById('new-project-modal');
    const newProjectForm = document.getElementById('new-project-form');

    if (!newProjectBtn || !newProjectModal || !newProjectForm) {
        console.error('Required elements for project creation not found.');
        return;
    }

    // Function to open the modal
    const openModal = () => {
        newProjectModal.classList.add('active');
    };

    // Function to close the modal
    const closeModal = () => {
        newProjectModal.classList.remove('active');
        newProjectForm.reset(); // Reset form fields
    };

    // Event listener for the "New Project" button
    newProjectBtn.addEventListener('click', openModal);

    // Event listeners for closing the modal
    newProjectModal.addEventListener('click', (e) => {
        if (e.target === newProjectModal || e.target.closest('[data-close-modal]')) {
            closeModal();
        }
    });

    // Event listener for form submission
    newProjectForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(newProjectForm);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await api.post('/projects/', data);
            if (response.status === 201) {
                showToast('Project created successfully!', 'success');
                closeModal();
                // Optionally, refresh the project list or add the new project to the UI
                // For now, we will just reload the page to see the new project.
                window.location.reload();
            }
        } catch (error) {
            console.error('Failed to create project:', error);
            showToast('Failed to create project. Please check the details.', 'error');
        }
    });
});