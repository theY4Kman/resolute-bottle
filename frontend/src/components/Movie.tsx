import {MovieType} from '../types';


export const Movie = ({
  id,
  title,
  year,
  genres,
  avg_rating,
  num_ratings,
  imdb_url,
  tmdb_url,
}: MovieType) => {
  return (
    <li key={id}>
      <a href={imdb_url} target="_blank">
        <strong>{title}</strong> ({year})
      </a>
    </li>
  );
};

export default Movie;
