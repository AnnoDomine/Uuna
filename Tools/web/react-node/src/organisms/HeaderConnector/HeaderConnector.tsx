import ConnectorIndicator from "../../atoms/ConnectorIndicator/ConnectorIndicator";
import ConnectorItem from "../../atoms/ConnectorItem/ConnectorItem";
import BuildSelection from "../../molecules/BuildSelection/BuildSelection";
import CurrentLevel from "../../molecules/CurrentLevel/CurrentLevel";
import CurrentType from "../../molecules/CurrentType/CurrentType";
import MapCurrentAgent from "../../molecules/MapCurrentAgent/MapCurrentAgent";
import useHeaderConnector from "./headerConnector.hooks";

const HeaderConnector = () => {
    const { connections } = useHeaderConnector();
    return (
        <div
            style={{
                display: "flex",
                flexDirection: "row",
                justifyContent: "space-between",
                alignItems: "flex-start",
                gap: "10px",
                width: "100%",
            }}
        >
            <div style={{ minWidth: "500px" }}>
                <MapCurrentAgent />
            </div>
            <div style={{ minWidth: "200px" }}>
                <BuildSelection />
            </div>
            <div style={{ minWidth: "150px" }}>
                {connections.map((c) => (
                    <ConnectorItem key={c.label}>
                        {c.label}
                        <ConnectorIndicator className={c.status} />
                    </ConnectorItem>
                ))}
                <CurrentType />
                <CurrentLevel />
            </div>
        </div>
    );
};

export default HeaderConnector;
