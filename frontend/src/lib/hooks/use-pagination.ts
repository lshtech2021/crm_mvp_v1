import { useCallback, useState } from "react";
import type { PaginatedResponse } from "@/types";

export function usePagination(initialPage = 1, initialPageSize = 20) {
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(1);

  const setFromResponse = useCallback(
    <T>(response: PaginatedResponse<T>) => {
      setTotalPages(response.total_pages);
    },
    [],
  );

  return { page, pageSize, totalPages, setPage, setPageSize, setTotalPages, setFromResponse };
}
