import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const chapter = z.object({
  chapter: z.number(),
  title: z.string(),
  emoji: z.string().optional().default(''),
});

export const collections = {
  genesis: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/genesis' }),
    schema: chapter,
  }),
  exodus: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/exodus' }),
    schema: chapter,
  }),
  leviticus: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/leviticus' }),
    schema: chapter,
  }),
  numbers: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/numbers' }),
    schema: chapter,
  }),
  deuteronomy: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/deuteronomy' }),
    schema: chapter,
  }),
  joshua: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/joshua' }),
    schema: chapter,
  }),
  judges: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/judges' }),
    schema: chapter,
  }),
  ruth: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/ruth' }),
    schema: chapter,
  }),
  samuel1: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/samuel1' }),
    schema: chapter,
  }),
  samuel2: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/samuel2' }),
    schema: chapter,
  }),
  kings1: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/kings1' }),
    schema: chapter,
  }),
  kings2: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/kings2' }),
    schema: chapter,
  }),
  chronicles1: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/chronicles1' }),
    schema: chapter,
  }),
  chronicles2: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/chronicles2' }),
    schema: chapter,
  }),
  ezra: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/ezra' }),
    schema: chapter,
  }),
  nehemiah: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/nehemiah' }),
    schema: chapter,
  }),
  esther: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/esther' }),
    schema: chapter,
  }),
  job: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/job' }),
    schema: chapter,
  }),
  psalms: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/psalms' }), schema: chapter }),
  proverbs: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/proverbs' }),
    schema: chapter,
  }),
  ecclesiastes: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/ecclesiastes' }), schema: chapter }),
  song: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/song' }), schema: chapter }),
  isaiah: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/isaiah' }), schema: chapter }),
  jeremiah: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/jeremiah' }), schema: chapter }),
  lamentations: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/lamentations' }), schema: chapter }),
  ezekiel: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/ezekiel' }), schema: chapter }),
  daniel: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/daniel' }), schema: chapter }),
  hosea: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/hosea' }), schema: chapter }),
  joel: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/joel' }), schema: chapter }),
  amos: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/amos' }), schema: chapter }),
  obadiah: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/obadiah' }), schema: chapter }),
  jonah: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/jonah' }), schema: chapter }),
  micah: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/micah' }), schema: chapter }),
  nahum: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/nahum' }), schema: chapter }),
  habakkuk: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/habakkuk' }), schema: chapter }),
  zephaniah: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/zephaniah' }), schema: chapter }),
  haggai: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/haggai' }), schema: chapter }),
  zechariah: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/zechariah' }), schema: chapter }),
  malachi: defineCollection({ loader: glob({ pattern: '*.md', base: './src/content/malachi' }), schema: chapter }),
};
