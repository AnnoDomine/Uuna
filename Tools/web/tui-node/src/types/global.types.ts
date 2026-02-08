/** biome-ignore-all lint/suspicious/noExplicitAny: Inside global definitions 'any' is a valid type for extending */

export type BasicFunction<Args extends Array<any> = Array<any>, RT = any> = (...args: Args) => RT;

export type LogType = "ERROR" | "INFO" | "DEBUG" | "WARN" | "TRACE" | "CRITICAL";
