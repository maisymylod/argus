import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export interface Artifact {
  kind: string;
  role?: string;
  url: string;
}

export interface Citation {
  source: string;
  detail: string;
}

export interface QueryRequest {
  aoi: string;
  before: string;
  after: string;
  query?: string;
  kb_only?: boolean;
}

export interface AgentResponse {
  mode: string;
  query: string;
  answer: string;
  aoi: string;
  bbox: [number, number, number, number] | null;
  artifacts: Artifact[];
  citations: Citation[];
}

// RTK Query: the Redux Toolkit data-fetching layer fronting the gateway.
export const api = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({ baseUrl: "/api" }),
  endpoints: (build) => ({
    runQuery: build.mutation<AgentResponse, QueryRequest>({
      query: (body) => ({ url: "/agent/query", method: "POST", body }),
    }),
  }),
});

export const { useRunQueryMutation } = api;
