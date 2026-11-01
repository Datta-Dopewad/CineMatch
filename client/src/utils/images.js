const posterPlaceholder='/assets/movies/placeholders/poster-placeholder.svg';
const backdropPlaceholder='/assets/movies/placeholders/backdrop-placeholder.svg';
const castPlaceholder='/assets/movies/placeholders/cast-placeholder.svg';
const configuredApi=import.meta.env.VITE_API_URL||'/api';
const imageServer=/^https?:\/\//i.test(configuredApi)?configuredApi.replace(/\/api\/?$/,'').replace(/\/$/,''):'';
function safeLocal(path,fallback){
  if(typeof path!=='string')return fallback;
  if(path.startsWith('/assets/movies/')&&!path.startsWith('//'))return path;
  if(/^\/api\/images\/[a-f\d]{24}$/i.test(path))return `${imageServer}${path}`;
  return fallback;
}
export const getMoviePoster=movie=>safeLocal(movie?.posterPath,posterPlaceholder);
export const getMovieBackdrop=movie=>safeLocal(movie?.backdropPath,backdropPlaceholder);
export const getCastImage=path=>safeLocal(path,castPlaceholder);
export const getPlaceholderImage=kind=>kind==='backdrop'?backdropPlaceholder:kind==='cast'?castPlaceholder:posterPlaceholder;
