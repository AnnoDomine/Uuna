import type { FC } from "react";
import Table from "../../atoms/Table/Table.js";
import useLogTable from "./log_table.hooks.js";

const LogTable: FC = () => {
    const { logs } = useLogTable();
    return <Table data={logs} />;
};

export default LogTable;
