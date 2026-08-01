import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context: { site: URL }) {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  const sorted = posts.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

  return rss({
    title: 'Custom Skills Hub 博客',
    description: '分享 AI Agent 技能的设计思路、使用技巧和个人技术随笔。',
    site: context.site ?? 'https://hwj123hwj.asia',
    items: sorted.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      author: post.data.author,
      categories: post.data.tags,
      link: `/blog/${post.id}/`,
    })),
    customData: '<language>zh-cn</language>',
  });
}
