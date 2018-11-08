import { CommanderStatic } from "commander";

export function registerCommand(program: CommanderStatic) {
  program.command("init").action(() => {
    console.log("Init a skygear server");
  });
}
