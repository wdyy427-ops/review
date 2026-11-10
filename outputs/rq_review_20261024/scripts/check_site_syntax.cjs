const fs = require('fs');
const path = require('path');

const htmlPath = path.resolve(__dirname, '..', 'site', 'dist', 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');
const marker = '<script src="data_thresholded.js"></script><script>';
const start = html.indexOf(marker);
const end = html.lastIndexOf('</script>');
if (start < 0 || end < 0) throw new Error('Inline script not found');
const source = html.slice(start + marker.length, end);
new Function(source);
console.log('inline-js-syntax: ok');
