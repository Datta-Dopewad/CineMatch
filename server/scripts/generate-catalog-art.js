import dotenv from 'dotenv';
import mongoose from 'mongoose';
import fs from 'node:fs';
import path from 'node:path';

dotenv.config({ path: path.resolve('../.env') });
const root = path.resolve('../client/public/assets/movies');
const mappingPath = path.resolve('data/movieImageMapping.json');
const mappings = JSON.parse(fs.readFileSync(mappingPath, 'utf8'));
if(!process.env.MONGODB_URI)throw Error('MONGODB_URI is required; refusing to update a local fallback database.');
await mongoose.connect(process.env.MONGODB_URI);
const movies = await mongoose.connection.collection('movies').find({}, { projection: { movieLensId: 1, title: 1, genres: 1 } }).toArray();
const byId = new Map(movies.map(movie => [movie.movieLensId, movie]));
const palettes = {
  Action: ['#fb7185','#f97316','#431407'], Adventure: ['#34d399','#22d3ee','#052e2b'], Animation: ['#f0abfc','#818cf8','#312e81'],
  Children: ['#facc15','#fb7185','#422006'], Comedy: ['#fde047','#fb923c','#431407'], Crime: ['#f87171','#a78bfa','#1e1b4b'],
  Documentary: ['#67e8f9','#a3e635','#082f49'], Drama: ['#c4b5fd','#f472b6','#3b0764'], Fantasy: ['#c084fc','#22d3ee','#2e1065'],
  Horror: ['#4ade80','#a3e635','#052e16'], Musical: ['#f0abfc','#fb7185','#500724'], Mystery: ['#818cf8','#38bdf8','#172554'],
  Romance: ['#fda4af','#f9a8d4','#500724'], SciFi: ['#67e8f9','#818cf8','#0c1a3c'], Thriller: ['#f97316','#f43f5e','#450a0a'], War: ['#d4d4d8','#fb923c','#27272a'], Western: ['#fbbf24','#fb7185','#451a03']
};
const esc = s => String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&apos;');
function hash(n){let x=(n*2654435761)>>>0;return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)/4294967296;}}
function poster(movie){const rnd=hash(movie.movieLensId);const genre=(movie.genres||[]).find(g=>palettes[g])||'Drama';const [a,b,dark]=palettes[genre];let shapes='';
 for(let i=0;i<12;i++){const x=Math.round(rnd()*400),y=Math.round(rnd()*410),r=20+Math.round(rnd()*130);shapes+=`<circle cx="${x}" cy="${y}" r="${r}" fill="none" stroke="${i%2?a:b}" stroke-opacity="${(0.07+rnd()*0.17).toFixed(2)}" stroke-width="${1+Math.round(rnd()*5)}"/>`;}
 for(let i=0;i<30;i++){const x=Math.round(rnd()*400),y=Math.round(rnd()*440),r=1+Math.round(rnd()*2);shapes+=`<circle cx="${x}" cy="${y}" r="${r}" fill="#fff" opacity="${(0.12+rnd()*0.4).toFixed(2)}"/>`;}
 const title=movie.title.replace(/\s*\(\d{4}\).*$/,'').replace(/, The$/,'').replace(/, A$/,'');const words=title.toUpperCase().split(/\s+/);const lines=[];let line='';for(const word of words){if((line+' '+word).trim().length>17&&line){lines.push(line);line=word;}else line=(line+' '+word).trim();}if(line)lines.push(line);const shown=lines.slice(0,4);const start=432-(shown.length-1)*30;
 const titleSvg=shown.map((t,i)=>`<text x="30" y="${start+i*30}" fill="#fff" font-family="Arial,sans-serif" font-size="${t.length>15?20:25}" font-weight="800" letter-spacing="1">${esc(t)}</text>`).join('');
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600"><defs><linearGradient id="g" x2=".8" y2="1"><stop stop-color="${a}"/><stop offset=".52" stop-color="${b}"/><stop offset="1" stop-color="${dark}"/></linearGradient><radialGradient id="v"><stop stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".76"/></radialGradient></defs><rect width="400" height="600" fill="${dark}"/><path fill="url(#g)" d="M0 0h400v600H0z" opacity=".8"/>${shapes}<path fill="url(#v)" d="M0 0h400v600H0z"/><path fill="#080b14" fill-opacity=".76" d="M0 400h400v200H0z"/><text x="30" y="42" fill="#fff" opacity=".72" font-family="Arial,sans-serif" font-size="12" font-weight="700" letter-spacing="4">CINEMATCH · ${esc(genre.toUpperCase())}</text>${titleSvg}<path d="M30 465h52" stroke="${a}" stroke-width="4"/><text x="30" y="493" fill="#fff" opacity=".7" font-family="Arial,sans-serif" font-size="13" letter-spacing="3">A FILM FOR YOUR NEXT NIGHT</text></svg>`;
}
const ops=[];let generated=0;
for(const row of mappings){const movie=byId.get(row.movieLensId);if(!movie)continue;
 if([2010,6987].includes(row.movieLensId)){row.posterPath=`/assets/movies/posters/${row.movieLensId}.jpg`;continue;}
 const posterPath=`/assets/movies/posters/${row.movieLensId}.svg`;fs.writeFileSync(path.join(root,'posters',`${row.movieLensId}.svg`),poster(movie));row.posterPath=posterPath;
 ops.push({updateOne:{filter:{movieLensId:row.movieLensId},update:{$set:{posterPath}}}});generated++;
}
fs.writeFileSync(mappingPath,JSON.stringify(mappings,null,2));
for(let i=0;i<ops.length;i+=500)await mongoose.connection.collection('movies').bulkWrite(ops.slice(i,i+500),{ordered:false});
console.log(`Generated ${generated} unique local movie artworks and updated the catalog. Preserved the two sourced historical posters.`);
await mongoose.disconnect();
