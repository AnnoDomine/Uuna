import {
    Step,
    Stepper,
    stepClasses,
    stepIndicatorClasses,
    styled,
    Typography,
    typographyClasses,
} from "@mui/joy";
import clsx from "clsx";
import useMapCurrentAgent from "./mapCurrentAgent.hooks";

const BorderedStep = styled(Step)(() => ({
    transition: "background-color 0.2s ease-in-out",
    display: "flex",
}));

const CustomStepper = styled(Stepper)(({ theme }) => ({
    "--Stepper-verticalGap": "0rem",
    "--Stepper-horizontalGap": "0rem",
    "--StepIndicator-size": "0rem",
    "--Step-gap": "0rem",
    "--Step-connectorInset": "0rem",
    "--Step-connectorRadius": "0rem",
    "--Step-connectorThickness": "0px",
    [`& .${stepClasses.completed}`]: {
        "&::after": { bgcolor: "transparent" },
    },
    [`& .${stepClasses.active}`]: {
        [`& .${stepIndicatorClasses.root}`]: {
            border: "4px solid",
            borderColor: "transparent",
            boxShadow: `0 0 0 1px ${theme.vars.palette.primary[500]}`,
        },
    },
    [`& .${stepClasses.disabled} *`]: {
        color: "neutral.softDisabledColor",
    },
    [`& .${typographyClasses["title-sm"]}`]: {
        textTransform: "uppercase",
        letterSpacing: "1px",
        fontSize: "10px",
    },
}));

const StepTypo = styled(Typography)(() => ({
    textAlign: "center",
    borderRadius: "16px",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    margin: "8px",
    padding: "8px",
    transition:
        "background-color 0.2s ease-in-out, color 0.2s ease-in-out, border 0.2s ease-in-out, fonwWeight 0.2s ease-in-out",
    backgroundColor: "white",
    color: "black",
    fontWeight: 400,
    border: "0.5px solid black",
    "&.active": {
        backgroundColor: "green",
        color: "white",
        border: "0.5px solid white",
        fontWeight: 700,
        "&.lib": {
            backgroundColor: "var(--color-librarian)",
        },
        "&.cour": {
            backgroundColor: "var(--color-courier)",
        },
        "&.arch": {
            backgroundColor: "var(--color-archivist)",
        },
        "&.exp": {
            backgroundColor: "var(--color-expedition-group)",
        },
        "&.sani": {
            backgroundColor: "var(--color-sentinel)",
        },
        "&.cart": {
            backgroundColor: "var(--color-cartographer)",
        },
        "&.sage": {
            backgroundColor: "var(--color-sages)",
        },
        "&.tink": {
            backgroundColor: "var(--color-tinker)",
        },
        "&.obs": {
            backgroundColor: "var(--color-observer)",
        },
    },
}));

/**
 * This component maps a visual indicator of the current agent.
 */
const MapCurrentAgent = () => {
    const { step, isError } = useMapCurrentAgent();
    return (
        <div
            style={{
                display: "flex",
                flexDirection: "row",
                justifyContent: "space-between",
                alignItems: "center",
                gap: "10px",
                width: "100%",
                outline: isError ? "2px solid red" : "none",
            }}
        >
            <div style={{ display: "flex" }}>
                <CustomStepper>
                    <BorderedStep>
                        <StepTypo className={clsx("lib", { active: step === "lib" })}>
                            Librarian
                        </StepTypo>
                    </BorderedStep>
                    <CustomStepper orientation="vertical">
                        <BorderedStep>
                            <StepTypo className={clsx("cour", { active: step === "cour" })}>
                                Courier
                            </StepTypo>
                        </BorderedStep>
                        <CustomStepper>
                            <BorderedStep>
                                <StepTypo className={clsx("arch", { active: step === "arch" })}>
                                    Archivist
                                </StepTypo>
                            </BorderedStep>
                            <CustomStepper orientation="vertical">
                                <BorderedStep>
                                    <StepTypo className={clsx("exp", { active: step === "exp" })}>
                                        Expedition Group
                                    </StepTypo>
                                </BorderedStep>
                                <BorderedStep>
                                    <StepTypo className={clsx("sani", { active: step === "sani" })}>
                                        Sentinel
                                    </StepTypo>
                                </BorderedStep>
                            </CustomStepper>
                            <BorderedStep>
                                <StepTypo className={clsx("cart", { active: step === "cart" })}>
                                    Cartographer
                                </StepTypo>
                            </BorderedStep>
                            <BorderedStep>
                                <StepTypo className={clsx("sage", { active: step === "sage" })}>
                                    Sages
                                </StepTypo>
                            </BorderedStep>
                            <CustomStepper orientation="vertical">
                                <BorderedStep>
                                    <StepTypo className={clsx("tink", { active: step === "tink" })}>
                                        Tinker
                                    </StepTypo>
                                </BorderedStep>
                                <BorderedStep>
                                    <StepTypo className={clsx("obs", { active: step === "obs" })}>
                                        Observer
                                    </StepTypo>
                                </BorderedStep>
                            </CustomStepper>
                        </CustomStepper>
                    </CustomStepper>
                </CustomStepper>
            </div>
        </div>
    );
};

export default MapCurrentAgent;
