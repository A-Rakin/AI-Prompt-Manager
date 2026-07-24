/**
 * ==============================================================================
 * PromptForge - Live Search & Client-Side Filtering
 * ==============================================================================
 * Enables instant, no-reload filtering of prompt cards directly in the browser DOM
 * while debouncing backend query synchronization.
 * ==============================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  const liveSearchInput = document.getElementById('liveSearchInput');
  const promptGrid = document.querySelector('.prompt-grid');

  if (liveSearchInput && promptGrid) {
    const cards = promptGrid.querySelectorAll('.prompt-card-wrapper');

    liveSearchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().strip ? e.target.value.toLowerCase().trim() : e.target.value.toLowerCase();

      cards.forEach(card => {
        const title = card.getAttribute('data-title') || '';
        const content = card.getAttribute('data-content') || '';
        const tags = card.getAttribute('data-tags') || '';
        const platform = card.getAttribute('data-platform') || '';

        if (
          title.includes(query) ||
          content.includes(query) ||
          tags.includes(query) ||
          platform.includes(query)
        ) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
  }
});
