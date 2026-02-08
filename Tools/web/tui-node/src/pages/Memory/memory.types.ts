export interface IMemoryResult {
    id: string;
    content: string;
    role: string;
    similarity: number;
    metadata: Record<string, any>;
}

export interface IMemorySearchRequest {
    role: string;
    query: string;
    limit?: number;
}

export interface IMemorySearchResponse {
    results: IMemoryResult[];
}
