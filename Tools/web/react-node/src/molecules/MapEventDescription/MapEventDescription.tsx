import { memo } from "react";

type Props = {
    /**
     * Stringified JSON
     */
    description: string;
};

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
interface DescriptionItem
    extends Record<string, string | number | boolean | DescriptionItem | DescriptionItem[]> {}

type FieldProps = {
    field: string;
    value: string | number | boolean | DescriptionItem | DescriptionItem[];
    level?: number;
    key: string;
};

const DescriptionField = ({ field, value, level = 0, key }: FieldProps) => {
    const parsedValue = (() => {
        console.log("VALUE: ", value, typeof value);
        const parsedV: DescriptionItem | DescriptionItem[] | string =
            typeof value === "string" && (value.startsWith("{") || value.startsWith("["))
                ? JSON.parse(JSON.stringify(value))
                : value;
        console.log("PARSED VALUE: ", parsedV);

        if (Array.isArray(parsedV)) {
            return (
                <div key={key}
            style={{
                marginLeft: `calc(8px * ${level})`,
                borderLeft: "1px solid black",
                padding: "4px",
                display: "flex",
                flexDirection: "column",
                gap: "4px",
            }}>
                    {parsedV.map((v, i) => (
                        <DescriptionField
                            field={i.toString()}
                            value={v}
                            level={level + 1}
                            key={`${field}-${i.toString()}`}
                        />
                    ))}
                </div>
            );
        }
        if (typeof parsedV === "object") {
            return (
                <div key={key}
            style={{
                marginLeft: `calc(8px * ${level})`,
                borderLeft: "1px solid black",
                padding: "4px",
                display: "flex",
                flexDirection: "column",
                gap: "4px",
            }}>
                    {Object.entries(parsedV).map(([k, v]) => (
                        <DescriptionField
                            field={k}
                            value={v}
                            level={level + 1}
                            key={`${field}-${k}`}
                        />
                    ))}
                </div>
            );
        }
        return <div
            style={{
                marginLeft: `calc(8px * ${level})`,
                borderLeft: "1px solid black",
                padding: "4px",
                display: "flex",
                flexDirection: "column",
                gap: "4px",
            }} key={key}>{parsedV.toString()}</div>;
    })();

    return (
        <div
            style={{
                marginLeft: `calc(8px * ${level})`,
                borderLeft: "1px solid black",
                padding: "4px",
                display: "flex",
                flexDirection: "column",
                gap: "4px",
            }}
        >
            <div>{field}</div>
            {parsedValue}
        </div>
    );
};

const MapEventDescription = memo(({ description }: Props) => {
    const parsedDescription: DescriptionItem | DescriptionItem[] | string = JSON.parse(description);
    if (Array.isArray(parsedDescription)) {
        return parsedDescription.map((v, i) => (
            <DescriptionField field={i.toString()} value={v} key={i.toString()} />
        ));
    }
    if (typeof parsedDescription === "object") {
        return Object.entries(parsedDescription).map(([k, v]) => (
            <DescriptionField field={k} value={v} key={k} />
        ));
    }
    if (!parsedDescription) {
        return <div>No description</div>;
    }
    if (typeof parsedDescription === "string") {
        return <div>{parsedDescription}</div>;
    }
    return null;
});

export default MapEventDescription;
