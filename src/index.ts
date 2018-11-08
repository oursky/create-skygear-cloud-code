import * as program from "commander";

import { registerCommand as registerInitCommand } from "./commands/init";
import { registerCommand as registerHelpCommand } from "./commands/help";

program.version("1.0.0").description("Scaffolding for skygear server");

program.on("command:*", () => {
  console.error("Invalid command: %s", program.args.join(" "));
  program.help();
});

registerInitCommand(program);
registerHelpCommand(program);

program.parse(process.argv);
if (process.argv.slice(2).length === 0) {
  console.error(
    "You didn't pass any command\nSee --help for a list of available commands."
  );
}
