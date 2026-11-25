import { defineCollection, z } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

export const collections = {
  docs: defineCollection({
    loader: docsLoader(),
    schema: docsSchema({
      extend: z.object({
        weight: z.number().optional(),
        date: z.coerce.date().optional(),
        aliases: z.array(z.string()).optional(),
      }),
    }),
  }),
};
