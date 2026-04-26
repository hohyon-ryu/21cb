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
  proverbs: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/proverbs' }),
    schema: chapter,
  }),
};
