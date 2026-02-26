export interface IMemoryResult {
    id: string;
    content: string;
    role: string;
    score: number; // Corrected field name from similarity to score
    metadata: Record<string, string | number | boolean | null>;
}

export interface IMemorySearchRequest {
    role: string;
    query: string;
    limit?: number;
}

export interface IMemorySearchResponse {
    results: IMemoryResult[];
}
