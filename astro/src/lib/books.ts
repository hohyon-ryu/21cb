export type BookSlug = 'genesis' | 'exodus';

export const BOOKS: Record<BookSlug, { name: string; total: number }> = {
  genesis: { name: '창세기', total: 50 },
  exodus: { name: '출애굽기', total: 40 },
};

export const BOOK_ORDER: BookSlug[] = ['genesis', 'exodus'];
