import { MovieType } from '../types';
import Movie from './Movie';


interface MovieListProps {
  movies?: MovieType[],
};

export const MovieList = ({ movies }: MovieListProps) => {
  if (movies == null || movies.length === 0) {
    return null;
  }

  return (
    <ol>
      {movies.map(movie => <Movie {...movie} key={movie.id} />)}
    </ol>
  );
};

export default MovieList;
