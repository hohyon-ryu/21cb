export type BookSlug = 'genesis' | 'exodus' | 'leviticus' | 'numbers' | 'deuteronomy' | 'joshua' | 'judges' | 'ruth';

export const BOOKS: Record<BookSlug, { name: string; total: number }> = {
  genesis: { name: '창세기', total: 50 },
  exodus: { name: '출애굽기', total: 40 },
  leviticus: { name: '레위기', total: 27 },
  numbers: { name: '민수기', total: 36 },
  deuteronomy: { name: '신명기', total: 34 },
  joshua: { name: '여호수아', total: 24 },
  judges: { name: '사사기', total: 21 },
  ruth: { name: '룻기', total: 4 },
};

export const BOOK_ORDER: BookSlug[] = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 'joshua', 'judges', 'ruth'];
