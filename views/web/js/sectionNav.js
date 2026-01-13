// sectionNav.js

let scrollRoot = null;
let navRoot = null;
let observer = null;
const navItems = new Map();

function slugify(text) {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

function ensureCategoryMeta(group, index, existingIds) {
  let category = group.dataset.category;
  if (!category) {
    const header = group.querySelector('h2, h3, h4, h5, h6');
    category = header?.textContent?.trim() || `Section ${index + 1}`;
    group.dataset.category = category;
  }

  if (!group.id) {
    const base = slugify(category) || `section-${index + 1}`;
    let candidate = base;
    let suffix = 1;
    while (existingIds.has(candidate)) {
      candidate = `${base}-${suffix}`;
      suffix += 1;
    }
    group.id = candidate;
  }

  existingIds.add(group.id);
  return category;
}

function setActiveNavItem(targetId) {
  navRoot.querySelectorAll('.section-nav-item.active').forEach(item => {
    item.classList.remove('active');
  });
  const item = navItems.get(targetId);
  if (item) {
    item.classList.add('active');
  }
}

function createNavItem(label, targetId) {
  const item = document.createElement('button');
  item.type = 'button';
  item.className = 'section-nav-item';
  item.textContent = label;
  item.dataset.targetId = targetId;
  item.addEventListener('click', () => {
    const target = document.getElementById(targetId);
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setActiveNavItem(targetId);
    }
  });
  return item;
}

function ensureObserver() {
  if (observer) {
    observer.disconnect();
  }
  observer = new IntersectionObserver(
    entries => {
      let bestEntry = null;
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        if (!bestEntry || entry.intersectionRatio > bestEntry.intersectionRatio) {
          bestEntry = entry;
        }
      });
      if (bestEntry) {
        setActiveNavItem(bestEntry.target.id);
      }
    },
    { root: scrollRoot, threshold: [0.25, 0.5, 0.75] }
  );
}

export function initSectionNav({ scrollRootId, navRootId }) {
  scrollRoot = document.getElementById(scrollRootId);
  navRoot = document.getElementById(navRootId);
}

export function rebuildSectionNav() {
  if (!scrollRoot || !navRoot) {
    return;
  }

  const groups = Array.from(scrollRoot.querySelectorAll('.category-group'));
  navRoot.innerHTML = '';
  navItems.clear();

  const existingIds = new Set();
  groups.forEach((group, index) => {
    const label = ensureCategoryMeta(group, index, existingIds);
    const item = createNavItem(label, group.id);
    navRoot.appendChild(item);
    navItems.set(group.id, item);
  });

  ensureObserver();
  groups.forEach(group => observer.observe(group));

  if (groups.length > 0) {
    setActiveNavItem(groups[0].id);
  }
}
