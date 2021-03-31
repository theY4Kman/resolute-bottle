import { MovieType } from './types';

export interface PaginatedResponse<T> {
  count: number,
  next: string,
  previous: string,
  results: T[],
}

interface getMoviesOptions {
  query?: string,
  page?: number,
  pageSize?: number,
  signal?: AbortSignal,
}

export const getMovies = async ({
  query = '',
  page = 1,
  pageSize = 100,
  signal
}: getMoviesOptions): Promise<PaginatedResponse<MovieType>> => {
  const params = new URLSearchParams(Object.entries({
    q: query,
    page: page.toString(),
    page_size: pageSize.toString(),
  }));
  const url = `/api/movies?${params}`;

  let res = await fetch(url, { signal });
  return await res.json();
};
