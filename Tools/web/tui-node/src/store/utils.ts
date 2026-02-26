export const parseAnswerToString = <D extends Record<string, string | number | boolean | D>>(
    data: D,
): string => {
    const answer: string[] = Object.entries(data).reduce((acc, [key, value]) => {
        if (typeof value === "object") {
            acc.push(`${key.toLocaleUpperCase()}:\n${parseAnswerToString(value || {})}`);
        } else {
            acc.push(`${key.toLocaleUpperCase()}: ${(value || "NO-VALUE").toLocaleString()}`);
        }
        return acc;
    }, [] as string[]);
    return answer.join("\n");
};
