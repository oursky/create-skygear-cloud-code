import { CommanderStatic } from "commander";

import { validateProjectName } from "../validation";
import generateSkygearServer from "../generator";
import { PythonTemplate } from "../template";

export function registerCommand(program: CommanderStatic) {
  program
    .command("init <projectName>")
    .description("Create a skygear server")
    .action((projectName: string) => {
      const isProjectNameValid = validateProjectName(projectName);
      if (!isProjectNameValid) {
        console.error(
          `${projectName} is not a valid name for a project.` +
            "Please use a valid identifier name (alphanumeric)."
        );
        return;
      }

      generateSkygearServer(projectName, PythonTemplate);
    });
}
