import { useEffect, useState } from 'react';
import { getMovies, PaginatedResponse } from './api';
import MovieList from './components/MovieList';
import { MovieType } from './types';


const App = () => {
  const [query, setQuery] = useState<string>('');
  const [response, setResponse] = useState<PaginatedResponse<MovieType> | undefined>(undefined);

  useEffect(() => {
    const controller = new AbortController();
    getMovies({ query, signal: controller.signal })
      .then(res => setResponse(res));
    return () => controller.abort();
  }, [query]);

  return (
    <div>
      <h1>MovieLens Title Search</h1>
      <input type="search" onChange={event => setQuery(event.target.value)} />
      {response && <div>{response?.count} results</div>}
      <MovieList movies={response?.results} />
    </div>
  );
}

export default App;
