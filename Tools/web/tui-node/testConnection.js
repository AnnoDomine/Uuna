import axios from "axios";

const parseAnswer = (data, space = 0) => {
    const divider = `${"=".repeat(space)}======================`;
    const answer = [
        divider,
        ...Object.entries(data).reduce((acc, [key, value]) => {
            const spacer = " ".repeat(space);
            if (typeof value === "object") {
                acc.push(`${spacer}|${key.toLocaleUpperCase()}:\n${parseAnswer(value, space + 4)}`);
            } else {
                acc.push(
                    `${spacer}|${key.toLocaleUpperCase()}:\n${spacer}|${(
                        value || "undefined"
                    ).toLocaleString()}`,
                );
            }
            return acc;
        }, []),
        divider,
    ];
    return answer.join("\n");
};

async function testRequest() {
    await axios.get(`http://127.0.0.1:8001/builds/list/all`).then((res) => {
        console.log(parseAnswer(res?.data || {}));
        console.log(JSON.stringify(res?.data || []));
    });
}

testRequest();
