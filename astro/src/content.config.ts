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
};
