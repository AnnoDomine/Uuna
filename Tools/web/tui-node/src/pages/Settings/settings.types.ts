export interface ISetting {
    key: string;
    value: string | number | boolean;
    description: string;
}

export interface ISettingsResponse {
    settings: ISetting[];
}
