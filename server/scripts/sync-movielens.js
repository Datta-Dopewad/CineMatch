import dotenv from 'dotenv';
import mongoose from 'mongoose';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../..');
dotenv.config({path:path.join(root,'.env')});
const ml=path.join(root,'ml-service');
const download=spawnSync(process.env.PYTHON||'python',['-m','dataset.dataset_downloader'],{cwd:ml,stdio:'inherit'});
if(download.status!==0) process.exit(download.status||1);
const catalogPath=path.join(here,'../data/.movieCatalog.tmp.json');
const mapper=spawnSync(process.env.PYTHON||'python',['-c','import pandas as pd; from dataset.dataset_mapper import write_catalog; m=pd.read_csv("dataset/ml-latest-small/movies.csv").join(pd.read_csv("dataset/ml-latest-small/ratings.csv").groupby("movieId").rating.agg(["mean","count"]),on="movieId"); write_catalog(m,"../server/data/.movieCatalog.tmp.json")'],{cwd:ml,encoding:'utf8'});
if(mapper.status!==0) throw Error(mapper.stderr||mapper.error);
const movies=JSON.parse(fs.readFileSync(catalogPath,'utf8'));
const mappingPath=path.join(here,'../data/movieImageMapping.json');
const existingMapping=fs.existsSync(mappingPath)?JSON.parse(fs.readFileSync(mappingPath,'utf8')):[];
const curated=new Map(existingMapping.filter(row=>row.posterPath&&!row.posterPath.includes('/placeholders/')).map(row=>[row.movieLensId,row.posterPath]));
for(const movie of movies){const posterPath=curated.get(movie.movieLensId);if(posterPath)movie.posterPath=posterPath;}
const mapping=movies.map(({movieLensId,posterPath,backdropPath})=>({movieLensId,posterPath,backdropPath}));
fs.mkdirSync(path.join(here,'../data'),{recursive:true});fs.writeFileSync(mappingPath,JSON.stringify(mapping,null,2));
const Movie=mongoose.model('Movie',new mongoose.Schema({movieLensId:Number,title:String,genres:[String],releaseYear:Number,averageRating:Number,ratingCount:Number,datasetAverageRating:Number,datasetRatingCount:Number,popularity:Number,posterPath:String,backdropPath:String},{timestamps:true}));
if(!process.env.MONGODB_URI)throw Error('MONGODB_URI is required; refusing to sync to a local fallback.');
await mongoose.connect(process.env.MONGODB_URI);
const localStats=await mongoose.connection.collection('ratings').aggregate([{$group:{_id:'$movieId',average:{$avg:'$rating'},count:{$sum:1}}},{$lookup:{from:'movies',localField:'_id',foreignField:'_id',as:'movie'}},{$unwind:'$movie'},{$project:{_id:0,movieLensId:'$movie.movieLensId',average:1,count:1}}]).toArray();
const localByLens=new Map(localStats.map(row=>[row.movieLensId,row]));
for(let i=0;i<movies.length;i+=500){const batch=movies.slice(i,i+500).map(m=>{const local=localByLens.get(m.movieLensId);const count=m.datasetRatingCount+(local?.count||0);const average=count?(m.datasetAverageRating*m.datasetRatingCount+(local?.average||0)*(local?.count||0))/count:0;const insert={...m};delete insert.posterPath;delete insert.averageRating;delete insert.ratingCount;delete insert.datasetAverageRating;delete insert.datasetRatingCount;delete insert.popularity;return {updateOne:{filter:{movieLensId:m.movieLensId},update:{$setOnInsert:insert,$set:{posterPath:m.posterPath,datasetAverageRating:m.datasetAverageRating,datasetRatingCount:m.datasetRatingCount,averageRating:average,ratingCount:count,popularity:m.popularity}},upsert:true}}});await Movie.bulkWrite(batch,{ordered:false});}
console.log(`Synced ${movies.length} MovieLens movies and preserved curated local poster mappings.`);
fs.rmSync(catalogPath,{force:true});
await mongoose.disconnect();
