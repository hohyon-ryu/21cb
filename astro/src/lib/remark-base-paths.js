import { visit } from 'unist-util-visit';

/**
 * Prepend Astro's `base` to all internal image URLs (markdown ![]() and raw <img>).
 */
export function remarkBasePaths(base = '') {
  const prefix = base.replace(/\/$/, '');
  if (!prefix) return () => () => {};

  const imgRe = new RegExp(
    `(<img\\s+[^>]*src=)(["'])\\/(?!${prefix.slice(1)}\\/)([^"']+)\\2`,
    'g'
  );

  return () => (tree) => {
    visit(tree, 'image', (node) => {
      if (
        typeof node.url === 'string' &&
        node.url.startsWith('/') &&
        !node.url.startsWith(prefix + '/')
      ) {
        node.url = prefix + node.url;
      }
    });
    visit(tree, 'html', (node) => {
      if (typeof node.value === 'string') {
        node.value = node.value.replace(
          imgRe,
          (_m, p1, q, path) => `${p1}${q}${prefix}/${path}${q}`
        );
      }
    });
  };
}
