const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');

export const url = (path: string) =>
  `${BASE}${path.startsWith('/') ? path : '/' + path}`;
