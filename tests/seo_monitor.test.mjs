import test from 'node:test';
import assert from 'node:assert/strict';
import { extractLocs, inspectRobots } from '../seo_monitor.mjs';

test('extractLocs extrae URLs de sitemap XML', () => {
  const xml = '<urlset><url><loc>https://a.test/</loc></url><url><loc>https://b.test/x</loc></url></urlset>';
  assert.deepEqual(extractLocs(xml), ['https://a.test/', 'https://b.test/x']);
});

test('inspectRobots reconoce apertura raíz y sitemap institucional', () => {
  const robots = 'User-agent: *\nAllow: /\n\nSitemap: https://crebeucayali.github.io/sitemap-v2.xml\n';
  assert.deepEqual(inspectRobots(robots), { allows_root: true, sitemap_declared: true });
});

test('inspectRobots detecta ausencia de sitemap', () => {
  const result = inspectRobots('User-agent: *\nAllow: /\n');
  assert.equal(result.allows_root, true);
  assert.equal(result.sitemap_declared, false);
});
