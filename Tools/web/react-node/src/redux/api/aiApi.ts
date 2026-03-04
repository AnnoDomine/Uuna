import { fetchBaseQuery } from "@reduxjs/toolkit/query";
import { createApi } from "@reduxjs/toolkit/query/react";
import { addMessage } from "../slices/ai";

type ResearchAnswer = Record<"initial_knowledge", string>;
type CompleteAnswer = Record<"knowledge", string>;
type SuccessAnswerKnowledge = ResearchAnswer | CompleteAnswer;
type FullSuccessAnswerObj = Record<"status" | "task_id", string> & SuccessAnswerKnowledge;
type ErrorAnswer = Record<"error", string>;

type AIAnswer = FullSuccessAnswerObj | ErrorAnswer;

type AIRequest = {
    prompt: string;
    builds: string[];
};

const NO_PROMP_ANSWER: string[] = [
    "Your quest log is empty, hero! I’d love to grant you the wisdom you seek, but even a Level 80 Mage can't read a mind that isn't thinking. Speak up, or are you just here for the hearthstone?",
    "Thy voice is as silent as the Whispering Forest. I hold the wisdom of the Titans within me, yet I cannot conjure an answer from a void. Present thy query, Champion, so that the light of knowledge may shine upon thee!",
    "Greetings, seeker! Thy scrolls remain blank. I would fain assist thee in thy quest for knowledge, but even the Great Archivist cannot answer a silence. Speak thy query, or the vaults of Azeroth shall remain sealed!",
];
const NO_BUILD_ANSWER: string[] = [
    "The timelines are tangled, seeker! Choose an era to begin our investigation.",
    "Chromie is confused! Please select a point in the timeline to proceed.",
    "The Bronze Dragonflight demands a destination. Which build shall we delve into?",
    "Even Khadgar cannot scry without a focus! Select a version to continue.",
    "The Great Archives are vast and labyrinthine. Narrow your search to a specific build.",
    "Data is scattered across the Twisting Nether. Pick a version to ground our research.",
    "Nozdormu's hourglass is empty. Refill it by selecting a WoW build.",
    "The Caverns of Time remain locked until you specify an era, traveler.",
    "Are we in the past or the future? The Archivist needs a build to orient himself.",
    "A silent timeline yields no secrets. Select a version to break the spell!",
    "The strands of fate are frayed. Pick a build to weave the data together.",
    "Murozond approaches... Quick! Select a build to stabilize this timeline.",
    "Your research is lost in the Mists of Pandaria. Choose a build to clear the way.",
    "The Titans left many records, but you must choose which era to audit, mortal.",
    "Without a version, your query is as lost as a soul in the Maw!",
    "The scrolls of destiny require a specific date. Pick a build for the Librarian.",
    "Even the most skilled goblin miner needs to know where to dig. Choose a build!",
    "Silence in the halls of time. The Courier awaits your command and a version.",
    "The records of Azeroth are organized by patch. Which shall we open first?",
    "The Infinite Dragonflight has blurred the records. Choose a build to restore order!",
];

const aiApi = createApi({
    reducerPath: "aiResearch",
    baseQuery: fetchBaseQuery({ baseUrl: "http://127.0.0.1:8001" }),
    endpoints: (builder) => ({
        ask: builder.mutation<AIAnswer, AIRequest>({
            query: (body) => ({
                url: "/ai/ask",
                method: "POST",
                body,
            }),
            onQueryStarted: async (args, { dispatch, queryFulfilled }) => {
                if (!args.prompt) {
                    dispatch(
                        addMessage({
                            agent: "librarian",
                            message:
                                NO_PROMP_ANSWER[Math.floor(Math.random() * NO_PROMP_ANSWER.length)],
                            timestamp: Date.now(),
                            type: "error",
                            level: "error",
                        }),
                    );
                    return;
                }
                if (!args.builds?.length) {
                    dispatch(
                        addMessage({
                            agent: "librarian",
                            message:
                                NO_BUILD_ANSWER[Math.floor(Math.random() * NO_BUILD_ANSWER.length)],
                            timestamp: Date.now(),
                            type: "error",
                            level: "error",
                        }),
                    );
                    return;
                }

                try {
                    const { data } = await queryFulfilled;
                    console.log(data);
                    let knowledge = "";
                    let type: "error" | "response" | "chat" | "research" | "" = "";
                    if ("initial_knowledge" in data) {
                        knowledge = data.initial_knowledge;
                        type = "research";
                    }
                    if ("knowledge" in data) {
                        knowledge = data.knowledge;
                        type = "response";
                    }
                    if ("error" in data) {
                        knowledge = data.error;
                        type = "error";
                    }
                    if (!type) {
                        type = "chat";
                    }
                    if (knowledge === "None") {
                        // Do not add a "None" knowledge chat
                        return;
                    }
                    dispatch(
                        addMessage({
                            agent: "librarian",
                            message: knowledge,
                            timestamp: Date.now(),
                            type,
                            level: "info",
                        }),
                    );
                } catch (err) {
                    console.error(err);
                }
            },
        }),
    }),
});

export const { useAskMutation } = aiApi;

export default aiApi;
