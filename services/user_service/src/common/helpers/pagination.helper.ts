import { PaginationMetaDto } from '../dto/pagination-meta.dto';

/**
 * Create pagination metadata
 */
export function createPaginationMeta(
  total: number,
  limit: number,
  page: number,
): PaginationMetaDto {
  const total_pages = Math.ceil(total / limit);
  const has_next = page < total_pages;
  const has_previous = page > 1;

  return {
    total,
    limit,
    page,
    total_pages,
    has_next,
    has_previous,
  };
}
