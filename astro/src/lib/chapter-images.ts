export type ChapterImage = {
  src: string;
  alt: string;
  caption: string;
};

export const HERO_OVERRIDES_GENESIS: Record<number, ChapterImage> = {
  1: {
    src: '/assets/maps/genesis/ch01_chapter_scene_creation_order.png',
    alt: '빛과 물, 땅의 질서가 시작된다.',
    caption: '빛과 물, 땅의 질서가 시작된다.',
  },
  3: {
    src: '/assets/maps/genesis/ch03_chapter_scene_fall_exile.png',
    alt: '에덴의 경계에서 동쪽 땅으로 향하는 추방이 시작된다.',
    caption: '에덴의 경계에서 동쪽 땅으로 향하는 추방이 시작된다.',
  },
};

export function extractMapFigure(markdown: string): ChapterImage | null {
  const imgMatch = markdown.match(/<img\s+[^>]*src="([^"]+)"[^>]*alt="([^"]*)"/i);
  if (!imgMatch) return null;

  const captionMatch = markdown.match(/<p class="map-caption">\s*([\s\S]*?)\s*<\/p>/i);
  const caption = captionMatch ? captionMatch[1].trim() : imgMatch[2].trim();

  return {
    src: imgMatch[1].trim(),
    alt: imgMatch[2].trim(),
    caption,
  };
}

export function getFallbackMap(
  chapter: number,
  anchors: Array<{ chapter: number; image: ChapterImage }>
): ChapterImage | null {
  if (!anchors.length) return null;
  const previous = [...anchors].reverse().find((a) => a.chapter < chapter);
  return previous ? previous.image : anchors[0].image;
}
