import BackendService from "../../utils/services/backend.service.js";

/**
 * Helper function to quit clean application.
 * - stops API
 * - quit application with process.exit
 *
 * @param {number} exitCode - Optional. Exit code to use
 */
const quitApplication = (exitCode: number = 0) => {
    // Stop the backend process before exiting
    BackendService.stop();
    process.exit(exitCode);
};

export default quitApplication;
