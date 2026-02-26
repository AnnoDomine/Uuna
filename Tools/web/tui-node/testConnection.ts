import axios from "axios";

const parseAnswer = (data: Record<string, unknown>, space = 0): string => {
    const divider = `${"=".repeat(space)}======================`;
    const answer = [
        divider,
        ...Object.entries(data).reduce<string[]>((acc, [key, value]) => {
            const spacer = " ".repeat(space);
            if (typeof value === "object" && value !== null) {
                acc.push(
                    `${spacer}|${key.toLocaleUpperCase()}:\n${parseAnswer(
                        value as Record<string, unknown>,
                        space + 4,
                    )}`,
                );
            } else {
                acc.push(
                    `${spacer}|${key.toLocaleUpperCase()}:\n${spacer}|${
                        value ? String(value).toLocaleString() : "undefined"
                    }`,
                );
            }
            return acc;
        }, []),
        divider,
    ];
    return answer.join("\n");
};

async function testRequest() {
    try {
        const res = await axios.get("http://127.0.0.1:8001/builds/list/all");
        console.log(parseAnswer(res?.data || {}));
        console.log(JSON.stringify(res?.data || []));
    } catch (error) {
        console.error("Request failed:", error);
    }
}

testRequest();
