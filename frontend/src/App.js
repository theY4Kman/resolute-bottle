import React, {useEffect, useState} from 'react';


const getMovies = async ({ query = '', page = 1, page_size = 100, signal } = {}) => {
  const params = new URLSearchParams({
    q: query,
    page,
    page_size,
  });
  const url = `/api/movies?${params}`;

  let res = await fetch(url, { signal });
  return await res.json();
};


const App = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    getMovies({ query, signal: controller.signal }).then(res => setResponse(res));
    return controller.abort;
  }, [query]);

  return (
    <div>
      <h1>MovieLens Title Search</h1>
      <input type="search" onChange={event => setQuery(event.target.value)} />
      {response && <div>{response.count} results</div>}
      <ol>
        {(response?.results || []).map(
          ({ id, title, year, genres, avg_rating, num_ratings, imdb_url, tmdb_url }) => (
            <li key={id}>
              <a href={imdb_url} target="_blank">
                <strong>{title}</strong> ({year})
              </a>
            </li>
          ))
        }
      </ol>
    </div>
  );
}

export default App;
