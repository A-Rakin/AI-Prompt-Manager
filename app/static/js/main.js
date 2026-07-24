/**
 * ==============================================================================
 * PromptForge - Main UI Logic & AJAX Handlers
 * ==============================================================================
 * Manages global UI components, sidebar toggling on mobile, SweetAlert2 toast
 * notifications, one-click clipboard copying, and AJAX favorite/pin interactions.
 * ==============================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Bootstrap Tooltips
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

  // Initialize AOS Animation library if enabled
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 600,
      once: true,
      easing: 'ease-out-cubic'
    });
  }

  // Setup CSRF token for all AJAX fetch calls
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

  /**
   * Universal Toast Notification helper using SweetAlert2
   */
  window.showToast = function(icon, title) {
    if (typeof Swal !== 'undefined') {
      const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 2500,
        timerProgressBar: true,
        background: '#1E293B',
        color: '#F8FAFC',
        didOpen: (toast) => {
          toast.addEventListener('mouseenter', Swal.stopTimer);
          toast.addEventListener('mouseleave', Swal.resumeTimer);
        }
      });
      Toast.fire({ icon: icon, title: title });
    }
  };

  /**
   * One-Click Copy Prompt Content to Clipboard
   */
  window.copyPromptToClipboard = function(promptId, buttonElement) {
    let textContent = "";
    if (promptId) {
      const contentEl = document.getElementById(`prompt-content-${promptId}`);
      if (contentEl) {
        textContent = contentEl.textContent || contentEl.innerText;
      }
    }

    if (!textContent) return;

    // Use native Web Clipboard API
    navigator.clipboard.writeText(textContent).then(() => {
      // Trigger backend copy counter endpoint via AJAX
      if (promptId && csrfToken) {
        fetch(`/prompts/${promptId}/copy`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
          }
        })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            // Update copy counter badge if present on DOM card
            const badge = document.getElementById(`copy-count-${promptId}`);
            if (badge) {
              badge.textContent = data.copy_count;
            }
          }
        })
        .catch(err => console.error("Error recording copy event:", err));
      }

      // Visual feedback on button
      if (buttonElement) {
        const originalHTML = buttonElement.innerHTML;
        buttonElement.innerHTML = '<i class="fas fa-check text-success"></i> Copied!';
        buttonElement.classList.add('btn-success');
        setTimeout(() => {
          buttonElement.innerHTML = originalHTML;
          buttonElement.classList.remove('btn-success');
        }, 2000);
      }

      showToast('success', 'Prompt copied to clipboard!');
    }).catch(err => {
      console.error('Failed to copy: ', err);
      showToast('error', 'Could not copy to clipboard.');
    });
  };

  /**
   * Toggle Favorite Status via AJAX
   */
  window.toggleFavorite = function(promptId, btnElement) {
    if (!csrfToken) return;

    fetch(`/prompts/${promptId}/favorite`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      }
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        const icon = btnElement.querySelector('i');
        if (data.is_favorite) {
          btnElement.classList.add('active-fav');
          if (icon) icon.className = 'fas fa-heart text-danger';
        } else {
          btnElement.classList.remove('active-fav');
          if (icon) icon.className = 'far fa-heart';
        }
        showToast('info', data.message);
      }
    })
    .catch(err => console.error("Error toggling favorite:", err));
  };

  /**
   * Toggle Pin Status via AJAX
   */
  window.togglePin = function(promptId, btnElement) {
    if (!csrfToken) return;

    fetch(`/prompts/${promptId}/pin`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      }
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        const icon = btnElement.querySelector('i');
        if (data.is_pinned) {
          btnElement.classList.add('active-pin');
          if (icon) icon.className = 'fas fa-thumbtack text-warning';
        } else {
          btnElement.classList.remove('active-pin');
          if (icon) icon.className = 'fas fa-thumbtack';
        }
        showToast('info', data.message);
      }
    })
    .catch(err => console.error("Error toggling pin:", err));
  };

  /**
   * Mobile Sidebar Toggle
   */
  const sidebarToggleBtn = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  if (sidebarToggleBtn && sidebar) {
    sidebarToggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });
  }
});
