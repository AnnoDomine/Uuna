import MapAiSetting from "../../molecules/MapAiSetting/MapAiSetting";
import MapAnalysisSettig from "../../molecules/MapAnalysisSetting/MapAnalysisSettig";
import MapIngestionSetting from "../../molecules/MapIngestionSetting/MapIngestionSetting";
import MapSystemSetting from "../../molecules/MapSystemSetting/MapSystemSetting";
import MapTasksSetting from "../../molecules/MapTasksSetting/MapTasksSetting";
import { ReduxSettings } from "../../redux/types/settings.types";

type Props = {
    setting: ReduxSettings;
};

const MapSettings = ({ setting }: Props) => {
    switch (setting) {
        case ReduxSettings.AI:
            return <MapAiSetting />;
        case ReduxSettings.INGESTION:
            return <MapIngestionSetting />;
        case ReduxSettings.SYSTEM:
            return <MapSystemSetting />;
        case ReduxSettings.ANALYSIS:
            return <MapAnalysisSettig />;
        case ReduxSettings.TASKS:
            return <MapTasksSetting />;
        default:
            return null;
    }
};

export default MapSettings;
