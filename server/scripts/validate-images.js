import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../client/public');
const mappingFile=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../data/movieImageMapping.json');
const mapping=JSON.parse(fs.readFileSync(mappingFile,'utf8'));const problems=[];
for(const name of ['poster-placeholder.svg','backdrop-placeholder.svg','cast-placeholder.svg']){const file=path.join(root,'assets/movies/placeholders',name);if(!fs.existsSync(file)||!fs.readFileSync(file,'utf8').trimStart().startsWith('<svg'))problems.push(`Missing or invalid local placeholder: ${file}`);}
for(const row of mapping){for(const field of ['posterPath','backdropPath']){const value=row[field];if(typeof value==='string'&&/^\/api\/images\/[a-f\d]{24}$/i.test(value))continue;if(typeof value!=='string'||/^https?:/i.test(value)||!value.startsWith('/assets/movies/')){problems.push(`${row.movieLensId}: invalid local ${field} ${value}`);continue;}const file=path.join(root,value.replace(/^\//,''));if(!fs.existsSync(file)){problems.push(`${row.movieLensId}: missing ${field} ${file}`);continue;}const bytes=fs.readFileSync(file);const valid=bytes.subarray(0,3).equals(Buffer.from([0xff,0xd8,0xff]))||bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))||bytes.subarray(0,4).toString()==='RIFF'&&bytes.subarray(8,12).toString()==='WEBP'||bytes.subarray(0,4).toString()==='<svg';if(!valid)problems.push(`${row.movieLensId}: invalid image signature ${file}`);}}
if(problems.length){console.error(problems.join('\n'));process.exitCode=1;}else console.log(`Validated ${mapping.length} local movie image mappings.`);
