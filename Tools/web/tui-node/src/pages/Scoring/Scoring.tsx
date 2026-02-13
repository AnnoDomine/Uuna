import { Box, Text } from "ink";
import type { FC } from "react";
import Table from "../../atoms/Table/Table.js";
import useScoring from "./scoring.hooks.js";

const Scoring: FC = () => {
    const { agentStats, rawScores, isLoading, error } = useScoring();

    const agentTableData = agentStats.map((s) => ({
        Agent: s.agent,
        Tasks: s.taskCount,
        "Avg %": `${s.averageScore}%`,
        Total: s.totalScore,
    }));

    const historyTableData = rawScores.map((s) => ({
        ID: s.score_id,
        Task: s.task_id.slice(0, 8),
        Score: `${s.final_percent}%`,
        Date: new Date(s.created_at).toLocaleDateString(),
    }));

    return (
        <Box flexDirection="column" flexGrow={1} height="100%" width="100%">
            <Box marginBottom={1}>
                <Text color="#7aa2f7" bold>
                    AGENT SCORING BOARD
                </Text>
            </Box>

            {isLoading && agentStats.length === 0 && (
                <Text color="yellow">Calculating performance metrics...</Text>
            )}
            {error && <Text color="red">{error}</Text>}

            <Box flexDirection="row" height="100%" width="100%">
                <Box flexDirection="column" height="100%" width="50%">
                    <Box marginBottom={1}>
                        <Text color="magenta" bold underline>
                            Agent Performance
                        </Text>
                    </Box>
                    {agentStats.length > 0 ? (
                        <Table
                            data={agentTableData}
                            headerStyles={{ color: "green" }}
                            id="scoring-agent-table"
                        />
                    ) : (
                        <Text color="gray">No agent data available.</Text>
                    )}
                </Box>
                <Box flexDirection="column" height="100%" width="50%">
                    <Box marginBottom={1}>
                        <Text color="magenta" bold underline>
                            Latest Scorings
                        </Text>
                    </Box>
                    {rawScores.length > 0 ? (
                        <Table
                            data={historyTableData}
                            headerStyles={{ color: "cyan" }}
                            id="scoring-history-table"
                        />
                    ) : (
                        <Text color="gray">No historical scorings found.</Text>
                    )}
                </Box>
            </Box>
        </Box>
    );
};

export default Scoring;
