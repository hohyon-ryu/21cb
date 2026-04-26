export type BookSlug = 'genesis' | 'exodus' | 'leviticus' | 'numbers' | 'deuteronomy' | 'joshua' | 'judges' | 'ruth' | 'samuel1' | 'samuel2' | 'kings1' | 'kings2';

export const BOOKS: Record<BookSlug, { name: string; total: number }> = {
  genesis: { name: '창세기', total: 50 },
  exodus: { name: '출애굽기', total: 40 },
  leviticus: { name: '레위기', total: 27 },
  numbers: { name: '민수기', total: 36 },
  deuteronomy: { name: '신명기', total: 34 },
  joshua: { name: '여호수아', total: 24 },
  judges: { name: '사사기', total: 21 },
  ruth: { name: '룻기', total: 4 },
  samuel1: { name: '사무엘상', total: 31 },
  samuel2: { name: '사무엘하', total: 24 },
  kings1: { name: '열왕기상', total: 22 },
  kings2: { name: '열왕기하', total: 25 },
};

export const BOOK_ORDER: BookSlug[] = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 'joshua', 'judges', 'ruth', 'samuel1', 'samuel2', 'kings1', 'kings2'];
