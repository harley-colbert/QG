// toast.js

const DEFAULT_DURATION = 3500;

function getToastContainer() {
  return document.getElementById('toast-container');
}

function createToast(message, variant, duration = DEFAULT_DURATION) {
  const container = getToastContainer();
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${variant}`;
  toast.textContent = message;

  const closeBtn = document.createElement('button');
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'Dismiss notification');
  closeBtn.textContent = '×';

  closeBtn.addEventListener('click', () => {
    toast.remove();
  });

  toast.appendChild(closeBtn);
  container.appendChild(toast);

  if (duration > 0) {
    setTimeout(() => {
      toast.remove();
    }, duration);
  }
}

export function toastSuccess(message, duration) {
  createToast(message, 'success', duration);
}

export function toastError(message, duration) {
  createToast(message, 'error', duration);
}

export function toastInfo(message, duration) {
  createToast(message, 'info', duration);
}
