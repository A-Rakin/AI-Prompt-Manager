/**
 * ==============================================================================
 * PromptForge - Drag and Drop Prompt Collection Management
 * ==============================================================================
 * Enables power users to drag prompt cards and drop them onto collection folder
 * targets for rapid organization.
 * ==============================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  const draggablePrompts = document.querySelectorAll('[draggable="true"]');
  const collectionDropzones = document.querySelectorAll('.collection-dropzone');
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

  draggablePrompts.forEach(promptCard => {
    promptCard.addEventListener('dragstart', (e) => {
      const promptId = promptCard.getAttribute('data-prompt-id');
      e.dataTransfer.setData('text/plain', promptId);
      promptCard.classList.add('dragging');
    });

    promptCard.addEventListener('dragend', () => {
      promptCard.classList.remove('dragging');
    });
  });

  collectionDropzones.forEach(zone => {
    zone.addEventListener('dragover', (e) => {
      e.preventDefault();
      zone.classList.add('dropzone-hover');
    });

    zone.addEventListener('dragleave', () => {
      zone.classList.remove('dropzone-hover');
    });

    zone.addEventListener('drop', (e) => {
      e.preventDefault();
      zone.classList.remove('dropzone-hover');
      const promptId = e.dataTransfer.getData('text/plain');
      const collectionId = zone.getAttribute('data-collection-id');

      if (promptId && collectionId && csrfToken) {
        fetch(`/collections/${collectionId}/add-prompt`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
          },
          body: JSON.stringify({ prompt_id: promptId })
        })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            if (typeof window.showToast === 'function') {
              window.showToast('success', data.message);
            }
          }
        })
        .catch(err => console.error("Error adding prompt to collection via drag drop:", err));
      }
    });
  });
});
