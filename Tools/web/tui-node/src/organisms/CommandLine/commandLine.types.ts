export interface ICommand {
    name: string;
    description: string;
    subCommands?: ICommand[];
    action?: (args: string[]) => void;
}

export interface ICommandState {
    input: string;
    suggestions: string[];
    info: string[];
    isCommandMode: boolean;
}
